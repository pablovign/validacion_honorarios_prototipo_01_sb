from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError

from validacion_honorarios.db.connection import (
    session_scope,
)
from validacion_honorarios.db.models import (
    TarifaZonaCanalSelectividad,
    Zona,
)
from validacion_honorarios.repositories.canal_selectividad_repository import (
    CanalSelectividadRepository,
)
from validacion_honorarios.repositories.esquema_cotizacion_repository import (
    EsquemaCotizacionRepository,
)
from validacion_honorarios.repositories.tarifa_zona_canal_repository import (
    TarifaZonaCanalRepository,
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


class ZonaTarifaService:
    """Gestión de zonas y tarifas principales."""

    def listar_zonas(
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

            zona_repository = ZonaRepository(
                session
            )

            esquema = esquema_repository.obtener_por_id(
                esquema_cotizacion_id
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema de cotización "
                    "no existe."
                )

            zonas = (
                zona_repository.listar_por_esquema(
                    esquema_cotizacion_id
                )
            )

            session.expunge_all()

            return zonas

    def listar_canales(self):
        with session_scope() as session:
            repository = (
                CanalSelectividadRepository(
                    session
                )
            )

            canales = repository.listar()

            session.expunge_all()

            return canales

    def crear_zona(
        self,
        esquema_cotizacion_id: int,
        nombre: str,
    ) -> Zona:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        nombre_normalizado = (
            self._normalizar_nombre_zona(
                nombre
            )
        )

        try:
            with session_scope() as session:
                esquema_repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                zona_repository = ZonaRepository(
                    session
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

                if zona_repository.existe_nombre(
                    esquema_cotizacion_id=(
                        esquema_cotizacion_id
                    ),
                    nombre=nombre_normalizado,
                ):
                    raise ConflictError(
                        "Ya existe una zona con "
                        f"el nombre {nombre_normalizado} "
                        "dentro del esquema."
                    )

                zona = zona_repository.crear(
                    esquema_cotizacion_id=(
                        esquema_cotizacion_id
                    ),
                    nombre=nombre_normalizado,
                )

                session.expunge_all()

                return zona

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo crear la zona porque "
                "el nombre ya está utilizado."
            ) from exc

    def actualizar_zona(
        self,
        zona_id: int,
        nombre: str,
    ) -> Zona:
        self._validar_id(
            zona_id,
            "zona",
        )

        nombre_normalizado = (
            self._normalizar_nombre_zona(
                nombre
            )
        )

        try:
            with session_scope() as session:
                esquema_repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                zona_repository = ZonaRepository(
                    session
                )

                zona = zona_repository.obtener_por_id(
                    zona_id
                )

                if zona is None:
                    raise NotFoundError(
                        "La zona que se intenta "
                        "modificar no existe."
                    )

                esquema = (
                    esquema_repository.obtener_por_id(
                        zona.esquema_cotizacion_id
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

                if zona_repository.existe_nombre(
                    esquema_cotizacion_id=(
                        zona.esquema_cotizacion_id
                    ),
                    nombre=nombre_normalizado,
                    excluir_zona_id=zona_id,
                ):
                    raise ConflictError(
                        "Ya existe otra zona con "
                        f"el nombre {nombre_normalizado}."
                    )

                zona = zona_repository.actualizar(
                    zona=zona,
                    nombre=nombre_normalizado,
                )

                session.expunge_all()

                return zona

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo modificar la zona."
            ) from exc

    def eliminar_zona(
        self,
        zona_id: int,
    ) -> None:
        self._validar_id(
            zona_id,
            "zona",
        )

        try:
            with session_scope() as session:
                esquema_repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                zona_repository = ZonaRepository(
                    session
                )

                zona = zona_repository.obtener_por_id(
                    zona_id
                )

                if zona is None:
                    raise NotFoundError(
                        "La zona que se intenta "
                        "eliminar no existe."
                    )

                esquema = (
                    esquema_repository.obtener_por_id(
                        zona.esquema_cotizacion_id
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

                zona_repository.eliminar(
                    zona
                )

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo eliminar la zona "
                "porque tiene información relacionada."
            ) from exc

    def establecer_tarifa(
        self,
        esquema_cotizacion_id: int,
        zona_id: int,
        canal_selectividad_id: int,
        monto,
    ) -> TarifaZonaCanalSelectividad:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        self._validar_id(
            zona_id,
            "zona",
        )

        self._validar_id(
            canal_selectividad_id,
            "canal de selectividad",
        )

        monto_normalizado = (
            self._normalizar_monto(
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

                zona_repository = ZonaRepository(
                    session
                )

                canal_repository = (
                    CanalSelectividadRepository(
                        session
                    )
                )

                tarifa_repository = (
                    TarifaZonaCanalRepository(
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

                zona = zona_repository.obtener_por_id(
                    zona_id
                )

                if zona is None:
                    raise NotFoundError(
                        "La zona seleccionada "
                        "no existe."
                    )

                if (
                    zona.esquema_cotizacion_id
                    != esquema_cotizacion_id
                ):
                    raise BusinessRuleError(
                        "La zona no pertenece al "
                        "esquema seleccionado."
                    )

                canal = (
                    canal_repository.obtener_por_id(
                        canal_selectividad_id
                    )
                )

                if canal is None:
                    raise NotFoundError(
                        "El canal seleccionado "
                        "no existe."
                    )

                tarifa = tarifa_repository.obtener(
                    zona_id=zona_id,
                    canal_selectividad_id=(
                        canal_selectividad_id
                    ),
                )

                if tarifa is None:
                    tarifa = tarifa_repository.crear(
                        zona_id=zona_id,
                        canal_selectividad_id=(
                            canal_selectividad_id
                        ),
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
                "para la zona y el canal."
            ) from exc

    def eliminar_tarifa(
        self,
        esquema_cotizacion_id: int,
        zona_id: int,
        canal_selectividad_id: int,
    ) -> None:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        self._validar_id(
            zona_id,
            "zona",
        )

        self._validar_id(
            canal_selectividad_id,
            "canal de selectividad",
        )

        with session_scope() as session:
            esquema_repository = (
                EsquemaCotizacionRepository(
                    session
                )
            )

            zona_repository = ZonaRepository(
                session
            )

            tarifa_repository = (
                TarifaZonaCanalRepository(
                    session
                )
            )

            esquema = esquema_repository.obtener_por_id(
                esquema_cotizacion_id
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema de cotización "
                    "no existe."
                )

            self._validar_esquema_editable(
                esquema.estado
            )

            zona = zona_repository.obtener_por_id(
                zona_id
            )

            if zona is None:
                raise NotFoundError(
                    "La zona seleccionada no existe."
                )

            if (
                zona.esquema_cotizacion_id
                != esquema_cotizacion_id
            ):
                raise BusinessRuleError(
                    "La zona no pertenece al "
                    "esquema seleccionado."
                )

            tarifa = tarifa_repository.obtener(
                zona_id=zona_id,
                canal_selectividad_id=(
                    canal_selectividad_id
                ),
            )

            if tarifa is None:
                return

            tarifa_repository.eliminar(
                tarifa
            )

    @staticmethod
    def _normalizar_nombre_zona(
        nombre: str,
    ) -> str:
        if nombre is None:
            raise ValidationError(
                "El nombre de la zona "
                "es obligatorio."
            )

        nombre_normalizado = " ".join(
            nombre.strip().split()
        )

        if not nombre_normalizado:
            raise ValidationError(
                "El nombre de la zona "
                "es obligatorio."
            )

        if len(nombre_normalizado) > 150:
            raise ValidationError(
                "El nombre de la zona no puede "
                "superar los 150 caracteres."
            )

        return nombre_normalizado

    @staticmethod
    def _normalizar_monto(
        monto,
    ) -> Decimal:
        if isinstance(monto, str):
            texto = (
                monto.strip()
                .replace(" ", "")
            )

            if not texto:
                raise ValidationError(
                    "El monto es obligatorio."
                )

            if "," in texto and "." in texto:
                texto = (
                    texto.replace(".", "")
                    .replace(",", ".")
                )
            elif "," in texto:
                texto = texto.replace(
                    ",",
                    ".",
                )

            monto = texto

        try:
            monto_decimal = Decimal(
                str(monto)
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            raise ValidationError(
                "El monto ingresado no es válido."
            ) from exc

        if not monto_decimal.is_finite():
            raise ValidationError(
                "El monto ingresado no es válido."
            )

        if monto_decimal < Decimal("0"):
            raise ValidationError(
                "El monto no puede ser negativo."
            )

        return monto_decimal.quantize(
            Decimal("0.01")
        )

    @staticmethod
    def _validar_esquema_editable(
        estado: str,
    ) -> None:
        if estado != "BORRADOR":
            raise BusinessRuleError(
                "Solo pueden modificarse zonas "
                "y tarifas de esquemas en estado "
                "BORRADOR."
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