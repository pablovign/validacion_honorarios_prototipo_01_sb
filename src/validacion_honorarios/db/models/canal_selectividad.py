from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.tarifa_zona_canal import (
        TarifaZonaCanalSelectividad,
    )


class CanalSelectividad(Base):
    __tablename__ = "canal_selectividad"

    canal_selectividad_id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    tarifas_por_zona: Mapped[
        list["TarifaZonaCanalSelectividad"]
    ] = relationship(
        back_populates="canal_selectividad",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            "CanalSelectividad("
            f"canal_selectividad_id="
            f"{self.canal_selectividad_id!r}, "
            f"nombre={self.nombre!r}"
            ")"
        )