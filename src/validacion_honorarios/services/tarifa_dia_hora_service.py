from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from validacion_honorarios.db.connection import (
    session_scope,
)
from validacion_honorarios.db.models import (
    DiaHora,
    TarifaAdicionalDiaHora,
)
from validacion_honorarios.repositories.esquema_cotizacion_repository import (
    EsquemaCotizacionRepository,
)
from validacion_honorarios.repositories.tarifa_dia_hora_repository import (
    TarifaDiaHoraRepository,
)
from validacion_honorarios.services.exceptions import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from validacion_honorarios.services.zona_tarifa_service import (
    ZonaTarifaService,
)


class TarifaDiaHoraService:
    """Gestión de la matriz semanal de adicionales horarios."""

    CANTIDAD_POSICIONES = 168

    def listar(
        self,
        esquema_cotizacion_id: int,
    ):
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        with session_scope() as session:
            esquema_repository = (
                EsquemaCotizacionRepository(
                    session
                )
            )

            tarifa_repository = (
                TarifaDiaHoraRepository(
                    session
                )
            )

            esquema = (
                esquema_repository.obtener_por_id(
                    esquema_cotizacion_id
                )
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema de cotización "
                    "no existe."
                )

            tarifas = (
                tarifa_repository.listar_por_esquema(
                    esquema_cotizacion_id
                )
            )

            session.expunge_all()

            return tarifas

    def listar_catalogo(self):
        with session_scope() as session:
            repository = TarifaDiaHoraRepository(
                session
            )

            posiciones = repository.listar_catalogo()

            session.expunge_all()

            return posiciones

    def inicializar(
        self,
        esquema_cotizacion_id: int,
    ):
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        try:
            with session_scope() as session:
                esquema_repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                tarifa_repository = (
                    TarifaDiaHoraRepository(
                        session
                    )
                )

                esquema = (
                    esquema_repository.obtener_por_id(
                        esquema_cotizacion_id
                    )
                )

                if esquema is None:
                    raise NotFoundError(
                        "El esquema de cotización "
                        "no existe."
                    )

                self._validar_esquema_editable(
                    esquema.estado
                )

                existentes = (
                    tarifa_repository
                    .listar_por_esquema(
                        esquema_cotizacion_id
                    )
                )

                if existentes:
                    if (
                        len(existentes)
                        != self.CANTIDAD_POSICIONES
                    ):
                        raise BusinessRuleError(
                            "La configuración horaria "
                            "está incompleta: existen "
                            f"{len(existentes)} registros "
                            "en lugar de 168."
                        )

                    session.expunge_all()

                    return existentes

                catalogo = (
                    tarifa_repository
                    .listar_catalogo()
                )

                if (
                    len(catalogo)
                    != self.CANTIDAD_POSICIONES
                ):
                    raise BusinessRuleError(
                        "El catálogo Día-Hora debe "
                        "contener exactamente "
                        "168 posiciones."
                    )

                tarifas = []

                for posicion in catalogo:
                    tarifa = (
                        tarifa_repository.crear(
                            esquema_cotizacion_id=(
                                esquema_cotizacion_id
                            ),
                            dia_hora_id=(
                                posicion.dia_hora_id
                            ),
                            monto=Decimal("0.00"),
                        )
                    )

                    tarifa.dia_hora = posicion
                    tarifas.append(tarifa)

                session.expunge_all()

                return tarifas

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo inicializar la "
                "configuración horaria."
            ) from exc

    def eliminar_configuracion(
        self,
        esquema_cotizacion_id: int,
    ) -> int:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        with session_scope() as session:
            esquema_repository = (
                EsquemaCotizacionRepository(
                    session
                )
            )

            tarifa_repository = (
                TarifaDiaHoraRepository(
                    session
                )
            )

            esquema = (
                esquema_repository.obtener_por_id(
                    esquema_cotizacion_id
                )
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema de cotización "
                    "no existe."
                )

            self._validar_esquema_editable(
                esquema.estado
            )

            return (
                tarifa_repository
                .eliminar_todas_por_esquema(
                    esquema_cotizacion_id
                )
            )

    def establecer_monto(
        self,
        esquema_cotizacion_id: int,
        dia_hora_id: int,
        monto,
    ) -> TarifaAdicionalDiaHora:
        resultados = self.establecer_montos(
            esquema_cotizacion_id=(
                esquema_cotizacion_id
            ),
            dia_hora_ids=[
                dia_hora_id,
            ],
            monto=monto,
        )

        return resultados[0]

    def establecer_montos(
        self,
        esquema_cotizacion_id: int,
        dia_hora_ids: list[int],
        monto,
    ):
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        ids_normalizados = (
            self._normalizar_ids_posiciones(
                dia_hora_ids
            )
        )

        monto_normalizado = (
            ZonaTarifaService._normalizar_monto(
                monto
            )
        )

        try:
            with session_scope() as session:
                esquema_repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                tarifa_repository = (
                    TarifaDiaHoraRepository(
                        session
                    )
                )

                esquema = (
                    esquema_repository.obtener_por_id(
                        esquema_cotizacion_id
                    )
                )

                if esquema is None:
                    raise NotFoundError(
                        "El esquema de cotización "
                        "no existe."
                    )

                self._validar_esquema_editable(
                    esquema.estado
                )

                tarifas = (
                    tarifa_repository
                    .listar_por_esquema(
                        esquema_cotizacion_id
                    )
                )

                if (
                    len(tarifas)
                    != self.CANTIDAD_POSICIONES
                ):
                    raise BusinessRuleError(
                        "Antes de editar importes "
                        "debes inicializar las "
                        "168 posiciones horarias."
                    )

                tarifa_por_posicion = {
                    tarifa.dia_hora_id: tarifa
                    for tarifa in tarifas
                }

                faltantes = [
                    posicion_id
                    for posicion_id in ids_normalizados
                    if (
                        posicion_id
                        not in tarifa_por_posicion
                    )
                ]

                if faltantes:
                    raise NotFoundError(
                        "Una o más posiciones "
                        "seleccionadas no existen "
                        "en la configuración horaria."
                    )

                actualizadas = []

                for posicion_id in ids_normalizados:
                    tarifa = tarifa_por_posicion[
                        posicion_id
                    ]

                    tarifa_repository.actualizar(
                        tarifa=tarifa,
                        monto=monto_normalizado,
                    )

                    actualizadas.append(tarifa)

                session.expunge_all()

                return actualizadas

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudieron actualizar "
                "los importes horarios."
            ) from exc

    def restablecer_montos(
        self,
        esquema_cotizacion_id: int,
        dia_hora_ids: list[int],
    ):
        return self.establecer_montos(
            esquema_cotizacion_id=(
                esquema_cotizacion_id
            ),
            dia_hora_ids=dia_hora_ids,
            monto=Decimal("0.00"),
        )

    def obtener_resumen(
        self,
        esquema_cotizacion_id: int,
    ) -> dict[str, int | Decimal]:
        tarifas = self.listar(
            esquema_cotizacion_id
        )

        tarifas_con_adicional = [
            tarifa
            for tarifa in tarifas
            if tarifa.monto > Decimal("0.00")
        ]

        monto_maximo = max(
            (
                tarifa.monto
                for tarifa in tarifas
            ),
            default=Decimal("0.00"),
        )

        return {
            "cantidad_registros": len(tarifas),
            "cantidad_con_adicional": len(
                tarifas_con_adicional
            ),
            "cantidad_en_cero": (
                len(tarifas)
                - len(tarifas_con_adicional)
            ),
            "monto_maximo": monto_maximo,
        }

    @staticmethod
    def _normalizar_ids_posiciones(
        dia_hora_ids,
    ) -> list[int]:
        if not isinstance(
            dia_hora_ids,
            (list, tuple, set),
        ):
            raise ValidationError(
                "Las posiciones horarias deben "
                "proporcionarse como una colección."
            )

        if not dia_hora_ids:
            raise ValidationError(
                "Selecciona al menos una "
                "posición horaria."
            )

        resultado = []

        for identificador in dia_hora_ids:
            TarifaDiaHoraService._validar_id(
                identificador,
                "posición día-hora",
            )

            if identificador not in resultado:
                resultado.append(
                    identificador
                )

        return resultado

    @staticmethod
    def _validar_esquema_editable(
        estado: str,
    ) -> None:
        if estado != "BORRADOR":
            raise BusinessRuleError(
                "Los adicionales horarios solo "
                "pueden modificarse en esquemas "
                "en estado BORRADOR."
            )

    @staticmethod
    def _validar_id(
        identificador: int,
        entidad: str,
    ) -> None:
        if (
            not isinstance(
                identificador,
                int,
            )
            or isinstance(
                identificador,
                bool,
            )
            or identificador <= 0
        ):
            raise ValidationError(
                f"El identificador de {entidad} "
                "no es válido."
            )