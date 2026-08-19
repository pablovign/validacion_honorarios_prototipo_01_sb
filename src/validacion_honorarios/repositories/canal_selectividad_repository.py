from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from validacion_honorarios.db.models import (
    CanalSelectividad,
)


class CanalSelectividadRepository:
    """Acceso a datos del catálogo de canales."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def listar(
        self,
        busqueda: str | None = None,
    ):
        statement = select(
            CanalSelectividad
        )

        if busqueda:
            termino = f"%{busqueda.strip()}%"

            statement = statement.where(
                CanalSelectividad.nombre.ilike(
                    termino
                )
            )

        statement = statement.order_by(
            CanalSelectividad.nombre
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def obtener_por_id(
        self,
        canal_selectividad_id: int,
    ) -> CanalSelectividad | None:
        statement = (
            select(CanalSelectividad)
            .options(
                selectinload(
                    CanalSelectividad
                    .tarifas_por_zona
                )
            )
            .where(
                CanalSelectividad
                .canal_selectividad_id
                == canal_selectividad_id
            )
        )

        return self.session.scalar(
            statement
        )

    def obtener_por_nombre(
        self,
        nombre: str,
    ) -> CanalSelectividad | None:
        statement = select(
            CanalSelectividad
        ).where(
            func.lower(
                CanalSelectividad.nombre
            )
            == nombre.lower()
        )

        return self.session.scalar(
            statement
        )

    def existe_nombre(
        self,
        nombre: str,
        excluir_canal_id: int | None = None,
    ) -> bool:
        statement = select(
            func.count(
                CanalSelectividad
                .canal_selectividad_id
            )
        ).where(
            func.lower(
                CanalSelectividad.nombre
            )
            == nombre.lower()
        )

        if excluir_canal_id is not None:
            statement = statement.where(
                CanalSelectividad
                .canal_selectividad_id
                != excluir_canal_id
            )

        cantidad = self.session.scalar(
            statement
        )

        return bool(cantidad)

    def crear(
        self,
        nombre: str,
    ) -> CanalSelectividad:
        canal = CanalSelectividad(
            nombre=nombre
        )

        self.session.add(canal)
        self.session.flush()

        return canal

    def actualizar(
        self,
        canal: CanalSelectividad,
        nombre: str,
    ) -> CanalSelectividad:
        canal.nombre = nombre

        self.session.flush()

        return canal

    def eliminar(
        self,
        canal: CanalSelectividad,
    ) -> None:
        self.session.delete(canal)
        self.session.flush()