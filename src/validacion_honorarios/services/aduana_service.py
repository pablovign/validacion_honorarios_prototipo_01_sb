import re

from sqlalchemy.exc import IntegrityError

from validacion_honorarios.db.connection import (
    session_scope,
)
from validacion_honorarios.db.models import Aduana
from validacion_honorarios.repositories.aduana_repository import (
    AduanaRepository,
)
from validacion_honorarios.services.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


CODIGO_ADUANA_PATTERN = re.compile(
    r"^[0-9]{3}$"
)

class AduanaService:
    """Casos de uso y validaciones de Aduanas."""

    def listar(
        self,
        busqueda: str | None = None,
    ):
        termino = (
            busqueda.strip()
            if busqueda
            else None
        )

        with session_scope() as session:
            repository = AduanaRepository(session)

            aduanas = repository.listar(termino)

            for aduana in aduanas:
                session.expunge(aduana)

            return aduanas

    def obtener(
        self,
        aduana_id: int,
    ) -> Aduana:
        self._validar_id(aduana_id)

        with session_scope() as session:
            repository = AduanaRepository(session)

            aduana = repository.obtener_por_id(
                aduana_id
            )

            if aduana is None:
                raise NotFoundError(
                    "La aduana solicitada no existe."
                )

            session.expunge(aduana)

            return aduana

    def crear(
        self,
        codigo: str,
        nombre: str,
    ) -> Aduana:
        codigo_normalizado = (
            self._normalizar_codigo(codigo)
        )

        nombre_normalizado = (
            self._normalizar_nombre(nombre)
        )

        try:
            with session_scope() as session:
                repository = AduanaRepository(
                    session
                )

                self._validar_unicidad(
                    repository=repository,
                    codigo=codigo_normalizado,
                    nombre=nombre_normalizado,
                )

                aduana = repository.crear(
                    codigo=codigo_normalizado,
                    nombre=nombre_normalizado,
                )

                session.expunge(aduana)

                return aduana

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo crear la aduana porque "
                "el código o el nombre ya existe."
            ) from exc

    def actualizar(
        self,
        aduana_id: int,
        codigo: str,
        nombre: str,
    ) -> Aduana:
        self._validar_id(aduana_id)

        codigo_normalizado = (
            self._normalizar_codigo(codigo)
        )

        nombre_normalizado = (
            self._normalizar_nombre(nombre)
        )

        try:
            with session_scope() as session:
                repository = AduanaRepository(
                    session
                )

                aduana = repository.obtener_por_id(
                    aduana_id
                )

                if aduana is None:
                    raise NotFoundError(
                        "La aduana que se intenta "
                        "modificar no existe."
                    )

                self._validar_unicidad(
                    repository=repository,
                    codigo=codigo_normalizado,
                    nombre=nombre_normalizado,
                    excluir_aduana_id=aduana_id,
                )

                aduana = repository.actualizar(
                    aduana=aduana,
                    codigo=codigo_normalizado,
                    nombre=nombre_normalizado,
                )

                session.expunge(aduana)

                return aduana

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo modificar la aduana "
                "porque el código o el nombre "
                "ya está siendo utilizado."
            ) from exc

    def eliminar(
        self,
        aduana_id: int,
    ) -> None:
        self._validar_id(aduana_id)

        try:
            with session_scope() as session:
                repository = AduanaRepository(
                    session
                )

                aduana = repository.obtener_por_id(
                    aduana_id
                )

                if aduana is None:
                    raise NotFoundError(
                        "La aduana que se intenta "
                        "eliminar no existe."
                    )

                repository.eliminar(aduana)

        except IntegrityError as exc:
            raise ConflictError(
                "No se puede eliminar la aduana "
                "porque tiene proveedores asociados."
            ) from exc

    @staticmethod
    def _validar_id(
        aduana_id: int,
    ) -> None:
        if (
            not isinstance(aduana_id, int)
            or isinstance(aduana_id, bool)
            or aduana_id <= 0
        ):
            raise ValidationError(
                "El identificador de la aduana "
                "no es válido."
            )

    @staticmethod
    def _normalizar_codigo(
        codigo: str,
    ) -> str:
        if codigo is None:
            raise ValidationError(
                "El código es obligatorio."
            )

        codigo_normalizado = codigo.strip()

        if not CODIGO_ADUANA_PATTERN.fullmatch(
            codigo_normalizado
        ):
            raise ValidationError(
                "El código debe contener "
                "exactamente tres dígitos."
            )

        return codigo_normalizado

    @staticmethod
    def _normalizar_nombre(
        nombre: str,
    ) -> str:
        if nombre is None:
            raise ValidationError(
                "El nombre es obligatorio."
            )

        nombre_normalizado = " ".join(
            nombre.strip().split()
        ).upper()

        if not nombre_normalizado:
            raise ValidationError(
                "El nombre es obligatorio."
            )

        if len(nombre_normalizado) > 150:
            raise ValidationError(
                "El nombre no puede superar "
                "los 150 caracteres."
            )

        return nombre_normalizado

    @staticmethod
    def _validar_unicidad(
        repository: AduanaRepository,
        codigo: str,
        nombre: str,
        excluir_aduana_id: int | None = None,
    ) -> None:
        if repository.existe_codigo(
            codigo,
            excluir_aduana_id,
        ):
            raise ConflictError(
                f"Ya existe una aduana con "
                f"el código {codigo}."
            )

        if repository.existe_nombre(
            nombre,
            excluir_aduana_id,
        ):
            raise ConflictError(
                f"Ya existe una aduana con "
                f"el nombre {nombre}."
            )