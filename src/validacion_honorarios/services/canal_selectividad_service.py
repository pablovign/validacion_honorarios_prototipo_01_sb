from sqlalchemy.exc import IntegrityError

from validacion_honorarios.db.connection import (
    session_scope,
)
from validacion_honorarios.db.models import (
    CanalSelectividad,
)
from validacion_honorarios.repositories.canal_selectividad_repository import (
    CanalSelectividadRepository,
)
from validacion_honorarios.services.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


class CanalSelectividadService:
    """Casos de uso del catálogo de canales."""

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
            repository = (
                CanalSelectividadRepository(
                    session
                )
            )

            canales = repository.listar(
                busqueda=termino
            )

            session.expunge_all()

            return canales

    def obtener(
        self,
        canal_selectividad_id: int,
    ) -> CanalSelectividad:
        self._validar_id(
            canal_selectividad_id
        )

        with session_scope() as session:
            repository = (
                CanalSelectividadRepository(
                    session
                )
            )

            canal = repository.obtener_por_id(
                canal_selectividad_id
            )

            if canal is None:
                raise NotFoundError(
                    "El canal de selectividad "
                    "solicitado no existe."
                )

            session.expunge_all()

            return canal

    def crear(
        self,
        nombre: str,
    ) -> CanalSelectividad:
        nombre_normalizado = (
            self._normalizar_nombre(
                nombre
            )
        )

        try:
            with session_scope() as session:
                repository = (
                    CanalSelectividadRepository(
                        session
                    )
                )

                self._validar_unicidad(
                    repository=repository,
                    nombre=nombre_normalizado,
                )

                canal = repository.crear(
                    nombre=nombre_normalizado
                )

                session.expunge_all()

                return canal

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo crear el canal "
                "porque el nombre ya existe."
            ) from exc

    def actualizar(
        self,
        canal_selectividad_id: int,
        nombre: str,
    ) -> CanalSelectividad:
        self._validar_id(
            canal_selectividad_id
        )

        nombre_normalizado = (
            self._normalizar_nombre(
                nombre
            )
        )

        try:
            with session_scope() as session:
                repository = (
                    CanalSelectividadRepository(
                        session
                    )
                )

                canal = repository.obtener_por_id(
                    canal_selectividad_id
                )

                if canal is None:
                    raise NotFoundError(
                        "El canal que se intenta "
                        "modificar no existe."
                    )

                self._validar_unicidad(
                    repository=repository,
                    nombre=nombre_normalizado,
                    excluir_canal_id=(
                        canal_selectividad_id
                    ),
                )

                canal = repository.actualizar(
                    canal=canal,
                    nombre=nombre_normalizado,
                )

                session.expunge_all()

                return canal

        except IntegrityError as exc:
            raise ConflictError(
                "No se pudo modificar el canal "
                "porque el nombre ya está utilizado."
            ) from exc

    def eliminar(
        self,
        canal_selectividad_id: int,
    ) -> None:
        self._validar_id(
            canal_selectividad_id
        )

        try:
            with session_scope() as session:
                repository = (
                    CanalSelectividadRepository(
                        session
                    )
                )

                canal = repository.obtener_por_id(
                    canal_selectividad_id
                )

                if canal is None:
                    raise NotFoundError(
                        "El canal que se intenta "
                        "eliminar no existe."
                    )

                if canal.tarifas_por_zona:
                    raise ConflictError(
                        "No se puede eliminar el canal "
                        "porque tiene tarifas asociadas."
                    )

                repository.eliminar(canal)

        except IntegrityError as exc:
            raise ConflictError(
                "No se puede eliminar el canal "
                "porque tiene información relacionada."
            ) from exc

    @staticmethod
    def _validar_id(
        canal_selectividad_id: int,
    ) -> None:
        if (
            not isinstance(
                canal_selectividad_id,
                int,
            )
            or isinstance(
                canal_selectividad_id,
                bool,
            )
            or canal_selectividad_id <= 0
        ):
            raise ValidationError(
                "El identificador del canal "
                "no es válido."
            )

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

        if len(nombre_normalizado) > 50:
            raise ValidationError(
                "El nombre no puede superar "
                "los 50 caracteres."
            )

        return nombre_normalizado

    @staticmethod
    def _validar_unicidad(
        repository: CanalSelectividadRepository,
        nombre: str,
        excluir_canal_id: int | None = None,
    ) -> None:
        if repository.existe_nombre(
            nombre,
            excluir_canal_id,
        ):
            raise ConflictError(
                "Ya existe un canal de "
                f"selectividad llamado {nombre}."
            )