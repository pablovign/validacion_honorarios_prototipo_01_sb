from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from validacion_honorarios.db.connection import (
    session_scope,
)
from validacion_honorarios.db.models import (
    AdicionalCamiones,
    TarifaAdicionalCamionesZona,
)
from validacion_honorarios.repositories.adicional_camiones_repository import (
    AdicionalCamionesRepository,
)
from validacion_honorarios.repositories.esquema_cotizacion_repository import (
    EsquemaCotizacionRepository,
)
from validacion_honorarios.repositories.tarifa_camiones_zona_repository import (
    TarifaCamionesZonaRepository,
)
from validacion_honorarios.repositories.zona_repository import (
    ZonaRepository,
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


class AdicionalCamionesService:
    """Gestión de tramos y tarifas adicionales por camiones."""

    def listar_tramos(
        self,
        esquema_cotizacion_id: int,
    ):
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        with session_scope() as session:
            esquema_repository = (
                EsquemaCotizacionRepository(session)
            )

            adicional_repository = (
                AdicionalCamionesRepository(session)
            )

            esquema = esquema_repository.obtener_por_id(
                esquema_cotizacion_id
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema de cotización no existe."
                )

            adicionales = (
                adicional_repository.listar_por_esquema(
                    esquema_cotizacion_id
                )
            )

            session.expunge_all()

            return adicionales

    def crear_tramo(
        self,
        esquema_cotizacion_id: int,
        camion_desde,
        camion_hasta=None,
    ) -> AdicionalCamiones:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        desde = self._normalizar_camion(
            camion_desde,
            "Camión desde",
        )

        hasta = self._normalizar_camion_hasta(
            camion_hasta
        )

        self._validar_limites(
            desde,
            hasta,
        )

        try:
            with session_scope() as session:
                esquema_repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                adicional_repository = (
                    AdicionalCamionesRepository(
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

                tramos = (
                    adicional_repository
                    .listar_por_esquema(
                        esquema_cotizacion_id
                    )
                )

                self._validar_no_solapamiento(
                    camion_desde=desde,
                    camion_hasta=hasta,
                    tramos_existentes=tramos,
                )

                nombre = self._generar_nombre(
                    desde,
                    hasta,
                )

                adicional = adicional_repository.crear(
                    esquema_cotizacion_id=(
                        esquema_cotizacion_id
                    ),
                    nombre=nombre,
                    camion_desde=desde,
                    camion_hasta=hasta,
                )

                session.expunge_all()

                return adicional

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo crear el tramo. "
                "Comprueba que no se superponga "
                "con otro tramo del esquema."
            ) from exc

    def actualizar_tramo(
        self,
        adicional_camiones_id: int,
        camion_desde,
        camion_hasta=None,
    ) -> AdicionalCamiones:
        self._validar_id(
            adicional_camiones_id,
            "tramo de camiones",
        )

        desde = self._normalizar_camion(
            camion_desde,
            "Camión desde",
        )

        hasta = self._normalizar_camion_hasta(
            camion_hasta
        )

        self._validar_limites(
            desde,
            hasta,
        )

        try:
            with session_scope() as session:
                esquema_repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                adicional_repository = (
                    AdicionalCamionesRepository(
                        session
                    )
                )

                adicional = (
                    adicional_repository.obtener_por_id(
                        adicional_camiones_id
                    )
                )

                if adicional is None:
                    raise NotFoundError(
                        "El tramo que se intenta "
                        "modificar no existe."
                    )

                esquema = (
                    esquema_repository.obtener_por_id(
                        adicional.esquema_cotizacion_id
                    )
                )

                if esquema is None:
                    raise NotFoundError(
                        "El esquema relacionado "
                        "no existe."
                    )

                self._validar_esquema_editable(
                    esquema.estado
                )

                tramos = (
                    adicional_repository
                    .listar_por_esquema(
                        adicional.esquema_cotizacion_id
                    )
                )

                self._validar_no_solapamiento(
                    camion_desde=desde,
                    camion_hasta=hasta,
                    tramos_existentes=tramos,
                    excluir_adicional_id=(
                        adicional_camiones_id
                    ),
                )

                nombre = self._generar_nombre(
                    desde,
                    hasta,
                )

                adicional = (
                    adicional_repository.actualizar(
                        adicional=adicional,
                        nombre=nombre,
                        camion_desde=desde,
                        camion_hasta=hasta,
                    )
                )

                session.expunge_all()

                return adicional

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo modificar el tramo. "
                "Comprueba que no se superponga "
                "con otro tramo."
            ) from exc

    def eliminar_tramo(
        self,
        adicional_camiones_id: int,
    ) -> None:
        self._validar_id(
            adicional_camiones_id,
            "tramo de camiones",
        )

        with session_scope() as session:
            esquema_repository = (
                EsquemaCotizacionRepository(session)
            )

            adicional_repository = (
                AdicionalCamionesRepository(session)
            )

            adicional = (
                adicional_repository.obtener_por_id(
                    adicional_camiones_id
                )
            )

            if adicional is None:
                raise NotFoundError(
                    "El tramo que se intenta "
                    "eliminar no existe."
                )

            esquema = (
                esquema_repository.obtener_por_id(
                    adicional.esquema_cotizacion_id
                )
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema relacionado no existe."
                )

            self._validar_esquema_editable(
                esquema.estado
            )

            adicional_repository.eliminar(
                adicional
            )

    def establecer_tarifa(
        self,
        esquema_cotizacion_id: int,
        adicional_camiones_id: int,
        zona_id: int,
        monto,
    ) -> TarifaAdicionalCamionesZona:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        self._validar_id(
            adicional_camiones_id,
            "tramo de camiones",
        )

        self._validar_id(
            zona_id,
            "zona",
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

                adicional_repository = (
                    AdicionalCamionesRepository(
                        session
                    )
                )

                zona_repository = ZonaRepository(
                    session
                )

                tarifa_repository = (
                    TarifaCamionesZonaRepository(
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

                adicional = (
                    adicional_repository.obtener_por_id(
                        adicional_camiones_id
                    )
                )

                if adicional is None:
                    raise NotFoundError(
                        "El tramo seleccionado no existe."
                    )

                zona = zona_repository.obtener_por_id(
                    zona_id
                )

                if zona is None:
                    raise NotFoundError(
                        "La zona seleccionada no existe."
                    )

                if (
                    adicional.esquema_cotizacion_id
                    != esquema_cotizacion_id
                    or zona.esquema_cotizacion_id
                    != esquema_cotizacion_id
                ):
                    raise BusinessRuleError(
                        "El tramo y la zona deben "
                        "pertenecer al mismo esquema."
                    )

                tarifa = tarifa_repository.obtener(
                    adicional_camiones_id=(
                        adicional_camiones_id
                    ),
                    zona_id=zona_id,
                )

                if tarifa is None:
                    tarifa = tarifa_repository.crear(
                        esquema_cotizacion_id=(
                            esquema_cotizacion_id
                        ),
                        adicional_camiones_id=(
                            adicional_camiones_id
                        ),
                        zona_id=zona_id,
                        monto=monto_normalizado,
                    )
                else:
                    tarifa = tarifa_repository.actualizar(
                        tarifa=tarifa,
                        monto=monto_normalizado,
                    )

                session.expunge_all()

                return tarifa

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo guardar la tarifa "
                "del tramo para la zona."
            ) from exc

    def eliminar_tarifa(
        self,
        esquema_cotizacion_id: int,
        adicional_camiones_id: int,
        zona_id: int,
    ) -> None:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        self._validar_id(
            adicional_camiones_id,
            "tramo de camiones",
        )

        self._validar_id(
            zona_id,
            "zona",
        )

        with session_scope() as session:
            esquema_repository = (
                EsquemaCotizacionRepository(session)
            )

            tarifa_repository = (
                TarifaCamionesZonaRepository(session)
            )

            esquema = esquema_repository.obtener_por_id(
                esquema_cotizacion_id
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema no existe."
                )

            self._validar_esquema_editable(
                esquema.estado
            )

            tarifa = tarifa_repository.obtener(
                adicional_camiones_id=(
                    adicional_camiones_id
                ),
                zona_id=zona_id,
            )

            if tarifa is None:
                return

            if (
                tarifa.esquema_cotizacion_id
                != esquema_cotizacion_id
            ):
                raise BusinessRuleError(
                    "La tarifa no pertenece "
                    "al esquema seleccionado."
                )

            tarifa_repository.eliminar(
                tarifa
            )

    @staticmethod
    def _normalizar_camion(
        valor,
        etiqueta: str,
    ) -> int:
        if isinstance(valor, bool):
            raise ValidationError(
                f"{etiqueta} no es válido."
            )

        if isinstance(valor, str):
            valor = valor.strip()

            if not valor:
                raise ValidationError(
                    f"{etiqueta} es obligatorio."
                )

        try:
            numero = int(valor)

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValidationError(
                f"{etiqueta} debe ser "
                "un número entero."
            ) from exc

        if numero < 1:
            raise ValidationError(
                f"{etiqueta} debe ser "
                "mayor o igual que 1."
            )

        return numero

    @classmethod
    def _normalizar_camion_hasta(
        cls,
        valor,
    ) -> int | None:
        if valor is None:
            return None

        if isinstance(valor, str) and not valor.strip():
            return None

        return cls._normalizar_camion(
            valor,
            "Camión hasta",
        )

    @staticmethod
    def _validar_limites(
        camion_desde: int,
        camion_hasta: int | None,
    ) -> None:
        if (
            camion_hasta is not None
            and camion_hasta < camion_desde
        ):
            raise ValidationError(
                "Camión hasta no puede ser "
                "menor que camión desde."
            )

    @staticmethod
    def _intervalos_se_superponen(
        desde_a: int,
        hasta_a: int | None,
        desde_b: int,
        hasta_b: int | None,
    ) -> bool:
        limite_a = (
            float("inf")
            if hasta_a is None
            else hasta_a
        )

        limite_b = (
            float("inf")
            if hasta_b is None
            else hasta_b
        )

        return (
            desde_a <= limite_b
            and desde_b <= limite_a
        )

    @classmethod
    def _validar_no_solapamiento(
        cls,
        camion_desde: int,
        camion_hasta: int | None,
        tramos_existentes,
        excluir_adicional_id: int | None = None,
    ) -> None:
        for tramo in tramos_existentes:
            if (
                excluir_adicional_id is not None
                and tramo.adicional_camiones_id
                == excluir_adicional_id
            ):
                continue

            if cls._intervalos_se_superponen(
                camion_desde,
                camion_hasta,
                tramo.camion_desde,
                tramo.camion_hasta,
            ):
                raise ConflictError(
                    "El rango se superpone con "
                    f"{tramo.descripcion_rango}."
                )

    @staticmethod
    def _generar_nombre(
        camion_desde: int,
        camion_hasta: int | None,
    ) -> str:
        if camion_hasta is None:
            return (
                f"Desde el camión "
                f"{camion_desde}"
            )

        if camion_desde == camion_hasta:
            return f"Camión {camion_desde}"

        return (
            f"Camiones {camion_desde} "
            f"a {camion_hasta}"
        )

    @staticmethod
    def _validar_esquema_editable(
        estado: str,
    ) -> None:
        if estado != "BORRADOR":
            raise BusinessRuleError(
                "Los adicionales por camiones "
                "solo pueden modificarse en "
                "esquemas BORRADOR."
            )

    @staticmethod
    def _validar_id(
        identificador: int,
        entidad: str,
    ) -> None:
        if (
            not isinstance(identificador, int)
            or isinstance(identificador, bool)
            or identificador <= 0
        ):
            raise ValidationError(
                f"El identificador de {entidad} "
                "no es válido."
            )