from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Numeric,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.canal_selectividad import (
        CanalSelectividad,
    )
    from validacion_honorarios.db.models.zona import Zona


class TarifaZonaCanalSelectividad(Base):
    __tablename__ = "tarifa_zona_canal_selectividad"

    __table_args__ = (
        UniqueConstraint(
            "zona_id",
            "canal_selectividad_id",
            name="uq_tarifa_zona_canal",
        ),
    )

    tarifa_zona_canal_selectividad_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    zona_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "zona.zona_id",
            onupdate="RESTRICT",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    canal_selectividad_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey(
            "canal_selectividad.canal_selectividad_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    monto: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=18,
            scale=2,
        ),
        nullable=False,
    )

    zona: Mapped["Zona"] = relationship(
        back_populates="tarifas_por_canal",
    )

    canal_selectividad: Mapped[
        "CanalSelectividad"
    ] = relationship(
        back_populates="tarifas_por_zona",
    )

    def __repr__(self) -> str:
        return (
            "TarifaZonaCanalSelectividad("
            f"id={self.tarifa_zona_canal_selectividad_id!r}, "
            f"zona_id={self.zona_id!r}, "
            f"canal_selectividad_id="
            f"{self.canal_selectividad_id!r}, "
            f"monto={self.monto!r}"
            ")"
        )