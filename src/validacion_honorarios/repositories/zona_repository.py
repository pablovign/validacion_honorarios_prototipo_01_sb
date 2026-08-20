from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from validacion_honorarios.db.models import (
    TarifaZonaCanalSelectividad,
    Zona,
)


class ZonaRepository:
    """Acceso a datos de zonas de un esquema."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def listar_por_esquema(
        self,
        esquema_cotizacion_id: int,
    ):
        statement = (
            select(Zona)
            .options(
                selectinload(
                    Zona.tarifas_por_canal
                ).selectinload(
                    TarifaZonaCanalSelectividad
                    .canal_selectividad
                )
            )
            .where(
                Zona.esquema_cotizacion_id
                == esquema_cotizacion_id
            )
            .order_by(
                Zona.nombre
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def obtener_por_id(
        self,
        zona_id: int,
    ) -> Zona | None:
        statement = (
            select(Zona)
            .options(
                selectinload(
                    Zona.tarifas_por_canal
                ).selectinload(
                    TarifaZonaCanalSelectividad
                    .canal_selectividad
                )
            )
            .where(
                Zona.zona_id == zona_id
            )
        )

        return self.session.scalar(
            statement
        )

    def existe_nombre(
        self,
        esquema_cotizacion_id: int,
        nombre: str,
        excluir_zona_id: int | None = None,
    ) -> bool:
        statement = select(
            func.count(
                Zona.zona_id
            )
        ).where(
            Zona.esquema_cotizacion_id
            == esquema_cotizacion_id,
            func.lower(Zona.nombre)
            == nombre.lower(),
        )

        if excluir_zona_id is not None:
            statement = statement.where(
                Zona.zona_id
                != excluir_zona_id
            )

        cantidad = self.session.scalar(
            statement
        )

        return bool(cantidad)

    def crear(
        self,
        esquema_cotizacion_id: int,
        nombre: str,
    ) -> Zona:
        zona = Zona(
            esquema_cotizacion_id=(
                esquema_cotizacion_id
            ),
            nombre=nombre,
        )

        self.session.add(zona)
        self.session.flush()

        return zona

    def actualizar(
        self,
        zona: Zona,
        nombre: str,
    ) -> Zona:
        zona.nombre = nombre

        self.session.flush()

        return zona

    def eliminar(
        self,
        zona: Zona,
    ) -> None:
        self.session.delete(zona)
        self.session.flush()