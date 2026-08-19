import re

from sqlalchemy.exc import IntegrityError

from validacion_honorarios.db.connection import (
    session_scope,
)
from validacion_honorarios.db.models import (
    Aduana,
    Proveedor,
)
from validacion_honorarios.repositories.aduana_repository import (
    AduanaRepository,
)
from validacion_honorarios.repositories.proveedor_repository import (
    ProveedorRepository,
)
from validacion_honorarios.services.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


CUIT_PATTERN = re.compile(
    r"^[0-9]{11}$"
)


class ProveedorService:
    """Casos de uso y validaciones de Proveedores."""

    def listar(
        self,
        busqueda: str | None = None,
        aduana_id: int | None = None,
    ):
        termino = (
            busqueda.strip()
            if busqueda
            else None
        )

        if aduana_id is not None:
            self._validar_id_positivo(
                aduana_id,
                "aduana",
            )

        with session_scope() as session:
            repository = ProveedorRepository(
                session
            )

            proveedores = repository.listar(
                busqueda=termino,
                aduana_id=aduana_id,
            )

            for proveedor in proveedores:
                session.expunge(
                    proveedor.aduana
                )

                session.expunge(
                    proveedor
                )

            return proveedores

    def obtener(
        self,
        proveedor_id: int,
    ) -> Proveedor:
        self._validar_id_positivo(
            proveedor_id,
            "proveedor",
        )

        with session_scope() as session:
            repository = ProveedorRepository(
                session
            )

            proveedor = repository.obtener_por_id(
                proveedor_id
            )

            if proveedor is None:
                raise NotFoundError(
                    "El proveedor solicitado no existe."
                )

            aduana = proveedor.aduana

            session.expunge(
                aduana
            )

            session.expunge(
                proveedor
            )

            return proveedor

    def crear(
        self,
        aduana_id: int,
        razon_social: str,
        cuit: str,
    ) -> Proveedor:
        self._validar_id_positivo(
            aduana_id,
            "aduana",
        )

        razon_social_normalizada = (
            self._normalizar_razon_social(
                razon_social
            )
        )

        cuit_normalizado = (
            self._normalizar_cuit(
                cuit
            )
        )

        try:
            with session_scope() as session:
                aduana_repository = (
                    AduanaRepository(session)
                )

                proveedor_repository = (
                    ProveedorRepository(session)
                )

                aduana = (
                    aduana_repository
                    .obtener_por_id(
                        aduana_id
                    )
                )

                if aduana is None:
                    raise NotFoundError(
                        "La aduana seleccionada "
                        "no existe."
                    )

                self._validar_unicidad(
                    repository=proveedor_repository,
                    cuit=cuit_normalizado,
                )

                proveedor = (
                    proveedor_repository.crear(
                        aduana_id=aduana_id,
                        razon_social=(
                            razon_social_normalizada
                        ),
                        cuit=cuit_normalizado,
                    )
                )

                proveedor.aduana = aduana

                session.expunge(
                    aduana
                )

                session.expunge(
                    proveedor
                )

                return proveedor

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo crear el proveedor "
                "porque el CUIT ya está registrado "
                "o la aduana no es válida."
            ) from exc

    def actualizar(
        self,
        proveedor_id: int,
        aduana_id: int,
        razon_social: str,
        cuit: str,
    ) -> Proveedor:
        self._validar_id_positivo(
            proveedor_id,
            "proveedor",
        )

        self._validar_id_positivo(
            aduana_id,
            "aduana",
        )

        razon_social_normalizada = (
            self._normalizar_razon_social(
                razon_social
            )
        )

        cuit_normalizado = (
            self._normalizar_cuit(
                cuit
            )
        )

        try:
            with session_scope() as session:
                aduana_repository = (
                    AduanaRepository(session)
                )

                proveedor_repository = (
                    ProveedorRepository(session)
                )

                proveedor = (
                    proveedor_repository
                    .obtener_por_id(
                        proveedor_id
                    )
                )

                if proveedor is None:
                    raise NotFoundError(
                        "El proveedor que se intenta "
                        "modificar no existe."
                    )

                aduana = (
                    aduana_repository
                    .obtener_por_id(
                        aduana_id
                    )
                )

                if aduana is None:
                    raise NotFoundError(
                        "La aduana seleccionada "
                        "no existe."
                    )

                self._validar_unicidad(
                    repository=proveedor_repository,
                    cuit=cuit_normalizado,
                    excluir_proveedor_id=(
                        proveedor_id
                    ),
                )

                proveedor = (
                    proveedor_repository.actualizar(
                        proveedor=proveedor,
                        aduana_id=aduana_id,
                        razon_social=(
                            razon_social_normalizada
                        ),
                        cuit=cuit_normalizado,
                    )
                )

                proveedor.aduana = aduana

                session.expunge(
                    aduana
                )

                session.expunge(
                    proveedor
                )

                return proveedor

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo modificar el proveedor "
                "porque el CUIT ya está registrado "
                "o la aduana no es válida."
            ) from exc

    def eliminar(
        self,
        proveedor_id: int,
    ) -> None:
        self._validar_id_positivo(
            proveedor_id,
            "proveedor",
        )

        try:
            with session_scope() as session:
                repository = ProveedorRepository(
                    session
                )

                proveedor = repository.obtener_por_id(
                    proveedor_id
                )

                if proveedor is None:
                    raise NotFoundError(
                        "El proveedor que se intenta "
                        "eliminar no existe."
                    )

                if proveedor.esquemas_cotizacion:
                    raise ConflictError(
                        "No se puede eliminar el "
                        "proveedor porque tiene "
                        "esquemas de cotización "
                        "asociados."
                    )

                repository.eliminar(
                    proveedor
                )

        except IntegrityError as exc:
            raise ConflictError(
                "No se puede eliminar el proveedor "
                "porque tiene información relacionada."
            ) from exc

    def listar_aduanas(
        self,
    ):
        with session_scope() as session:
            repository = AduanaRepository(
                session
            )

            aduanas = repository.listar()

            for aduana in aduanas:
                session.expunge(
                    aduana
                )

            return aduanas

    @staticmethod
    def _validar_id_positivo(
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

    @staticmethod
    def _normalizar_cuit(
        cuit: str,
    ) -> str:
        if cuit is None:
            raise ValidationError(
                "El CUIT es obligatorio."
            )

        cuit_normalizado = (
            cuit.strip()
            .replace("-", "")
            .replace(" ", "")
        )

        if not CUIT_PATTERN.fullmatch(
            cuit_normalizado
        ):
            raise ValidationError(
                "El CUIT debe contener "
                "exactamente once dígitos."
            )

        return cuit_normalizado

    @staticmethod
    def _normalizar_razon_social(
        razon_social: str,
    ) -> str:
        if razon_social is None:
            raise ValidationError(
                "La razón social es obligatoria."
            )

        razon_social_normalizada = " ".join(
            razon_social.strip().split()
        )

        if not razon_social_normalizada:
            raise ValidationError(
                "La razón social es obligatoria."
            )

        if len(
            razon_social_normalizada
        ) > 200:
            raise ValidationError(
                "La razón social no puede superar "
                "los 200 caracteres."
            )

        return razon_social_normalizada

    @staticmethod
    def _validar_unicidad(
        repository: ProveedorRepository,
        cuit: str,
        excluir_proveedor_id: int | None = None,
    ) -> None:
        if repository.existe_cuit(
            cuit,
            excluir_proveedor_id,
        ):
            raise ConflictError(
                f"Ya existe un proveedor con "
                f"el CUIT {cuit}."
            )