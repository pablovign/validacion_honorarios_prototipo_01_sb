from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from validacion_honorarios.db.connection import session_scope
from validacion_honorarios.db.models import (
    AdicionalCamiones,
    EsquemaCotizacion,
    Proveedor,
    TarifaAdicionalCamionesZona,
    TarifaAdicionalDiaHora,
    TarifaZonaCanalSelectividad,
    Zona,
)
from validacion_honorarios.services.exceptions import (
    NotFoundError,
    ValidationError,
)


class ResumenEsquemaService:
    """Consulta integral y de solo lectura de un esquema."""

    CANTIDAD_POSICIONES_HORARIAS = 168

    def obtener(self, esquema_cotizacion_id: int) -> dict:
        self._validar_id(esquema_cotizacion_id)

        with session_scope() as session:
            statement = (
                select(EsquemaCotizacion)
                .options(
                    selectinload(
                        EsquemaCotizacion.proveedor
                    ).selectinload(
                        Proveedor.aduana
                    ),
                    selectinload(
                        EsquemaCotizacion.zonas
                    )
                    .selectinload(
                        Zona.tarifas_por_canal
                    )
                    .selectinload(
                        TarifaZonaCanalSelectividad
                        .canal_selectividad
                    ),
                    selectinload(
                        EsquemaCotizacion.adicionales_camiones
                    )
                    .selectinload(
                        AdicionalCamiones.tarifas_por_zona
                    )
                    .selectinload(
                        TarifaAdicionalCamionesZona.zona
                    ),
                    selectinload(
                        EsquemaCotizacion
                        .tarifas_adicionales_dia_hora
                    )
                    .selectinload(
                        TarifaAdicionalDiaHora.dia_hora
                    ),
                )
                .where(
                    EsquemaCotizacion.esquema_cotizacion_id
                    == esquema_cotizacion_id
                )
            )

            esquema = session.scalar(statement)

            if esquema is None:
                raise NotFoundError(
                    "El esquema de cotización no existe."
                )

            resumen = self._construir_resumen(esquema)

            return resumen

    def _construir_resumen(
        self,
        esquema: EsquemaCotizacion,
    ) -> dict:
        proveedor = esquema.proveedor
        aduana = proveedor.aduana

        zonas_ordenadas = sorted(
            esquema.zonas,
            key=lambda zona: zona.nombre.casefold(),
        )

        canales_por_id = {}
        tarifas_principales = []

        for zona in zonas_ordenadas:
            tarifas_zona = {}

            for tarifa in zona.tarifas_por_canal:
                canal = tarifa.canal_selectividad
                canales_por_id[
                    canal.canal_selectividad_id
                ] = canal
                tarifas_zona[
                    canal.canal_selectividad_id
                ] = tarifa.monto

            tarifas_principales.append(
                {
                    "zona_id": zona.zona_id,
                    "zona": zona.nombre,
                    "tarifas": tarifas_zona,
                }
            )

        canales = sorted(
            canales_por_id.values(),
            key=lambda canal: canal.nombre.casefold(),
        )

        tramos = []

        for tramo in sorted(
            esquema.adicionales_camiones,
            key=lambda item: item.camion_desde,
        ):
            tarifas_por_zona = {
                tarifa.zona_id: tarifa.monto
                for tarifa in tramo.tarifas_por_zona
            }

            tramos.append(
                {
                    "adicional_camiones_id": (
                        tramo.adicional_camiones_id
                    ),
                    "descripcion": tramo.descripcion_rango,
                    "camion_desde": tramo.camion_desde,
                    "camion_hasta": tramo.camion_hasta,
                    "tarifas": tarifas_por_zona,
                }
            )

        tarifas_horarias = sorted(
            esquema.tarifas_adicionales_dia_hora,
            key=lambda tarifa: (
                tarifa.dia_hora.dia,
                tarifa.dia_hora.hora,
            ),
        )

        bloques_horarios = self.agrupar_bloques_horarios(
            tarifas_horarias
        )

        advertencias = self._construir_advertencias(
            zonas=zonas_ordenadas,
            canales=canales,
            tarifas_principales=tarifas_principales,
            tramos=tramos,
            cantidad_tarifas_horarias=len(tarifas_horarias),
        )

        return {
            "general": {
                "esquema_cotizacion_id": (
                    esquema.esquema_cotizacion_id
                ),
                "estado": esquema.estado,
                "proveedor": proveedor.razon_social,
                "cuit": proveedor.cuit,
                "aduana_codigo": aduana.codigo,
                "aduana_nombre": aduana.nombre,
                "fecha_inicio": esquema.fecha_inicio,
                "fecha_fin": esquema.fecha_fin,
                "moneda_codigo": esquema.moneda_codigo,
                "observaciones": esquema.observaciones,
            },
            "zonas": [
                {
                    "zona_id": zona.zona_id,
                    "nombre": zona.nombre,
                }
                for zona in zonas_ordenadas
            ],
            "canales": [
                {
                    "canal_selectividad_id": (
                        canal.canal_selectividad_id
                    ),
                    "nombre": canal.nombre,
                }
                for canal in canales
            ],
            "tarifas_principales": tarifas_principales,
            "tramos_camiones": tramos,
            "horario": {
                "cantidad_registros": len(tarifas_horarias),
                "cantidad_mayor_cero": sum(
                    1
                    for tarifa in tarifas_horarias
                    if tarifa.monto > Decimal("0.00")
                ),
                "cantidad_en_cero": sum(
                    1
                    for tarifa in tarifas_horarias
                    if tarifa.monto == Decimal("0.00")
                ),
                "bloques": bloques_horarios,
                "tarifas": [
                    {
                        "dia": tarifa.dia_hora.dia,
                        "nombre_dia": tarifa.dia_hora.nombre_dia,
                        "hora": tarifa.dia_hora.hora,
                        "monto": tarifa.monto,
                    }
                    for tarifa in tarifas_horarias
                ],
            },
            "advertencias": advertencias,
        }

    @classmethod
    def agrupar_bloques_horarios(cls, tarifas) -> list[dict]:
        """Agrupa horas consecutivas del mismo día y monto positivo."""

        items = []

        for tarifa in tarifas:
            monto = tarifa.monto

            if monto <= Decimal("0.00"):
                continue

            posicion = tarifa.dia_hora
            items.append(
                {
                    "dia": posicion.dia,
                    "nombre_dia": posicion.nombre_dia,
                    "hora": posicion.hora,
                    "monto": monto,
                }
            )

        items.sort(
            key=lambda item: (
                item["dia"],
                item["hora"],
            )
        )

        bloques = []

        for item in items:
            if not bloques:
                bloques.append(
                    cls._nuevo_bloque(item)
                )
                continue

            ultimo = bloques[-1]
            es_contiguo = (
                ultimo["dia"] == item["dia"]
                and ultimo["hora_hasta"] == item["hora"]
                and ultimo["monto"] == item["monto"]
            )

            if es_contiguo:
                ultimo["hora_hasta"] = item["hora"] + 1
            else:
                bloques.append(
                    cls._nuevo_bloque(item)
                )

        return bloques

    @staticmethod
    def _nuevo_bloque(item: dict) -> dict:
        return {
            "dia": item["dia"],
            "nombre_dia": item["nombre_dia"],
            "hora_desde": item["hora"],
            "hora_hasta": item["hora"] + 1,
            "monto": item["monto"],
        }

    def _construir_advertencias(
        self,
        zonas,
        canales,
        tarifas_principales,
        tramos,
        cantidad_tarifas_horarias: int,
    ) -> list[dict[str, str]]:
        advertencias = []

        if not zonas:
            advertencias.append(
                {
                    "nivel": "ADVERTENCIA",
                    "mensaje": "El esquema no tiene zonas cargadas.",
                }
            )

        if zonas and not canales:
            advertencias.append(
                {
                    "nivel": "INFORMACIÓN",
                    "mensaje": (
                        "No hay canales utilizados en las tarifas "
                        "principales del esquema."
                    ),
                }
            )

        for fila in tarifas_principales:
            for canal in canales:
                canal_id = canal.canal_selectividad_id

                if canal_id not in fila["tarifas"]:
                    advertencias.append(
                        {
                            "nivel": "INFORMACIÓN",
                            "mensaje": (
                                f"La zona {fila['zona']} no tiene "
                                f"tarifa para el canal {canal.nombre}."
                            ),
                        }
                    )

        zona_ids = {
            zona.zona_id
            for zona in zonas
        }

        for tramo in tramos:
            for zona in zonas:
                if zona.zona_id not in tramo["tarifas"]:
                    advertencias.append(
                        {
                            "nivel": "INFORMACIÓN",
                            "mensaje": (
                                f"{tramo['descripcion']} no tiene tarifa "
                                f"para la zona {zona.nombre}."
                            ),
                        }
                    )

            claves_desconocidas = (
                set(tramo["tarifas"]) - zona_ids
            )

            if claves_desconocidas:
                advertencias.append(
                    {
                        "nivel": "ADVERTENCIA",
                        "mensaje": (
                            f"{tramo['descripcion']} contiene tarifas "
                            "para zonas que ya no están disponibles."
                        ),
                    }
                )

        if cantidad_tarifas_horarias not in (
            0,
            self.CANTIDAD_POSICIONES_HORARIAS,
        ):
            advertencias.append(
                {
                    "nivel": "ADVERTENCIA",
                    "mensaje": (
                        "La configuración horaria está incompleta: "
                        f"{cantidad_tarifas_horarias} de 168 posiciones."
                    ),
                }
            )

        if not advertencias:
            advertencias.append(
                {
                    "nivel": "OK",
                    "mensaje": (
                        "No se detectaron advertencias de consistencia."
                    ),
                }
            )

        return advertencias

    @staticmethod
    def _validar_id(esquema_cotizacion_id: int) -> None:
        if (
            not isinstance(esquema_cotizacion_id, int)
            or isinstance(esquema_cotizacion_id, bool)
            or esquema_cotizacion_id <= 0
        ):
            raise ValidationError(
                "El identificador del esquema no es válido."
            )
