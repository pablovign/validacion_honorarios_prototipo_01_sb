from datetime import date, datetime

from sqlalchemy.exc import IntegrityError

from validacion_honorarios.db.connection import (
    session_scope,
)
from validacion_honorarios.db.models import (
    EsquemaCotizacion,
)
from validacion_honorarios.repositories.esquema_cotizacion_repository import (
    EsquemaCotizacionRepository,
)
from validacion_honorarios.repositories.proveedor_repository import (
    ProveedorRepository,
)
from validacion_honorarios.services.exceptions import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


ESTADOS_VALIDOS = {
    "BORRADOR",
    "APROBADO",
    "RECHAZADO",
}

MONEDAS_VALIDAS = {
    "ARS",
    "USD",
}


class EsquemaCotizacionService:
    """Casos de uso de esquemas de cotización."""

    def listar(
        self,
        busqueda: str | None = None,
        proveedor_id: int | None = None,
        aduana_id: int | None = None,
        estado: str | None = None,
        moneda_codigo: str | None = None,
    ):
        termino = (
            busqueda.strip()
            if busqueda
            else None
        )

        if proveedor_id is not None:
            self._validar_id(
                proveedor_id,
                "proveedor",
            )

        if aduana_id is not None:
            self._validar_id(
                aduana_id,
                "aduana",
            )

        estado_normalizado = None

        if estado:
            estado_normalizado = (
                self._normalizar_estado(
                    estado
                )
            )

        moneda_normalizada = None

        if moneda_codigo:
            moneda_normalizada = (
                self._normalizar_moneda(
                    moneda_codigo
                )
            )

        with session_scope() as session:
            repository = (
                EsquemaCotizacionRepository(
                    session
                )
            )

            esquemas = repository.listar(
                busqueda=termino,
                proveedor_id=proveedor_id,
                aduana_id=aduana_id,
                estado=estado_normalizado,
                moneda_codigo=moneda_normalizada,
            )

            session.expunge_all()

            return esquemas

    def obtener(
        self,
        esquema_cotizacion_id: int,
    ) -> EsquemaCotizacion:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        with session_scope() as session:
            repository = (
                EsquemaCotizacionRepository(
                    session
                )
            )

            esquema = repository.obtener_por_id(
                esquema_cotizacion_id
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema de cotización "
                    "solicitado no existe."
                )

            session.expunge_all()

            return esquema

    def crear(
        self,
        proveedor_id: int,
        fecha_inicio: date | str,
        moneda_codigo: str,
        observaciones: str | None = None,
    ) -> EsquemaCotizacion:
        self._validar_id(
            proveedor_id,
            "proveedor",
        )

        fecha_normalizada = (
            self._normalizar_fecha(
                fecha_inicio
            )
        )

        moneda_normalizada = (
            self._normalizar_moneda(
                moneda_codigo
            )
        )

        observaciones_normalizadas = (
            self._normalizar_observaciones(
                observaciones
            )
        )

        try:
            with session_scope() as session:
                proveedor_repository = (
                    ProveedorRepository(session)
                )

                repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                proveedor = (
                    proveedor_repository
                    .obtener_por_id(
                        proveedor_id
                    )
                )

                if proveedor is None:
                    raise NotFoundError(
                        "El proveedor seleccionado "
                        "no existe."
                    )

                esquema = repository.crear(
                    proveedor_id=proveedor_id,
                    fecha_inicio=fecha_normalizada,
                    moneda_codigo=moneda_normalizada,
                    observaciones=(
                        observaciones_normalizadas
                    ),
                )

                esquema.proveedor = proveedor

                session.expunge_all()

                return esquema

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo crear el esquema "
                "de cotización."
            ) from exc

    def actualizar(
        self,
        esquema_cotizacion_id: int,
        proveedor_id: int,
        fecha_inicio: date | str,
        moneda_codigo: str,
        observaciones: str | None = None,
    ) -> EsquemaCotizacion:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        self._validar_id(
            proveedor_id,
            "proveedor",
        )

        fecha_normalizada = (
            self._normalizar_fecha(
                fecha_inicio
            )
        )

        moneda_normalizada = (
            self._normalizar_moneda(
                moneda_codigo
            )
        )

        observaciones_normalizadas = (
            self._normalizar_observaciones(
                observaciones
            )
        )

        try:
            with session_scope() as session:
                proveedor_repository = (
                    ProveedorRepository(session)
                )

                repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                esquema = repository.obtener_por_id(
                    esquema_cotizacion_id
                )

                if esquema is None:
                    raise NotFoundError(
                        "El esquema que se intenta "
                        "modificar no existe."
                    )

                self._validar_editable(
                    esquema
                )

                proveedor = (
                    proveedor_repository
                    .obtener_por_id(
                        proveedor_id
                    )
                )

                if proveedor is None:
                    raise NotFoundError(
                        "El proveedor seleccionado "
                        "no existe."
                    )

                esquema = repository.actualizar(
                    esquema=esquema,
                    proveedor_id=proveedor_id,
                    fecha_inicio=fecha_normalizada,
                    moneda_codigo=moneda_normalizada,
                    observaciones=(
                        observaciones_normalizadas
                    ),
                )

                esquema.proveedor = proveedor

                session.expunge_all()

                return esquema

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo modificar el "
                "esquema de cotización."
            ) from exc

    def rechazar(
        self,
        esquema_cotizacion_id: int,
    ) -> EsquemaCotizacion:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        with session_scope() as session:
            repository = (
                EsquemaCotizacionRepository(
                    session
                )
            )

            esquema = repository.obtener_por_id(
                esquema_cotizacion_id
            )

            if esquema is None:
                raise NotFoundError(
                    "El esquema que se intenta "
                    "rechazar no existe."
                )

            self._validar_editable(
                esquema
            )

            esquema = repository.cambiar_estado(
                esquema=esquema,
                estado="RECHAZADO",
            )

            session.expunge_all()

            return esquema

    def eliminar(
        self,
        esquema_cotizacion_id: int,
    ) -> None:
        self._validar_id(
            esquema_cotizacion_id,
            "esquema de cotización",
        )

        try:
            with session_scope() as session:
                repository = (
                    EsquemaCotizacionRepository(
                        session
                    )
                )

                esquema = repository.obtener_por_id(
                    esquema_cotizacion_id
                )

                if esquema is None:
                    raise NotFoundError(
                        "El esquema que se intenta "
                        "eliminar no existe."
                    )

                self._validar_editable(
                    esquema
                )

                repository.eliminar(
                    esquema
                )

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo eliminar el esquema "
                "porque tiene información relacionada."
            ) from exc

    def listar_proveedores(self):
        with session_scope() as session:
            repository = ProveedorRepository(
                session
            )

            proveedores = repository.listar()

            session.expunge_all()

            return proveedores

    @staticmethod
    def _validar_editable(
        esquema: EsquemaCotizacion,
    ) -> None:
        if esquema.estado != "BORRADOR":
            raise BusinessRuleError(
                "Solo los esquemas en estado "
                "BORRADOR pueden modificarse "
                "o eliminarse."
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

    @staticmethod
    def _normalizar_fecha(
        valor: date | str,
    ) -> date:
        if isinstance(valor, datetime):
            return valor.date()

        if isinstance(valor, date):
            return valor

        if not isinstance(valor, str):
            raise ValidationError(
                "La fecha de inicio no es válida."
            )

        texto = valor.strip()

        if not texto:
            raise ValidationError(
                "La fecha de inicio es obligatoria."
            )

        formatos = (
            "%d/%m/%Y",
            "%Y-%m-%d",
        )

        for formato in formatos:
            try:
                return datetime.strptime(
                    texto,
                    formato,
                ).date()

            except ValueError:
                continue

        raise ValidationError(
            "La fecha debe ingresarse como "
            "DD/MM/AAAA."
        )

    @staticmethod
    def _normalizar_moneda(
        moneda_codigo: str,
    ) -> str:
        if moneda_codigo is None:
            raise ValidationError(
                "La moneda es obligatoria."
            )

        moneda_normalizada = (
            moneda_codigo.strip().upper()
        )

        if moneda_normalizada not in MONEDAS_VALIDAS:
            raise ValidationError(
                "La moneda debe ser ARS o USD."
            )

        return moneda_normalizada

    @staticmethod
    def _normalizar_estado(
        estado: str,
    ) -> str:
        if estado is None:
            raise ValidationError(
                "El estado es obligatorio."
            )

        estado_normalizado = (
            estado.strip().upper()
        )

        if estado_normalizado not in ESTADOS_VALIDOS:
            raise ValidationError(
                "El estado debe ser BORRADOR, "
                "APROBADO o RECHAZADO."
            )

        return estado_normalizado

    @staticmethod
    def _normalizar_observaciones(
        observaciones: str | None,
    ) -> str | None:
        if observaciones is None:
            return None

        observaciones_normalizadas = (
            observaciones.strip()
        )

        if not observaciones_normalizadas:
            return None

        return observaciones_normalizadas