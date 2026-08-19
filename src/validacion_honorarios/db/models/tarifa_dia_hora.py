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
    from validacion_honorarios.db.models.dia_hora import DiaHora
    from validacion_honorarios.db.models.esquema_cotizacion import (
        EsquemaCotizacion,
    )


class TarifaAdicionalDiaHora(Base):
    __tablename__ = "tarifa_adicional_dia_hora"

    __table_args__ = (
        UniqueConstraint(
            "esquema_cotizacion_id",
            "dia_hora_id",
            name="uq_tarifa_adicional_dia_hora",
        ),
    )

    tarifa_adicional_dia_hora_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    esquema_cotizacion_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "esquema_cotizacion.esquema_cotizacion_id",
            onupdate="RESTRICT",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    dia_hora_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey(
            "dia_hora.dia_hora_id",
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
        default=Decimal("0.00"),
    )

    esquema_cotizacion: Mapped[
        "EsquemaCotizacion"
    ] = relationship(
        back_populates="tarifas_adicionales_dia_hora",
    )

    dia_hora: Mapped["DiaHora"] = relationship(
        back_populates="tarifas_adicionales",
    )

    @property
    def tiene_adicional(self) -> bool:
        return self.monto > Decimal("0.00")

    def __repr__(self) -> str:
        return (
            "TarifaAdicionalDiaHora("
            f"tarifa_adicional_dia_hora_id="
            f"{self.tarifa_adicional_dia_hora_id!r}, "
            f"esquema_cotizacion_id="
            f"{self.esquema_cotizacion_id!r}, "
            f"dia_hora_id={self.dia_hora_id!r}, "
            f"monto={self.monto!r}"
            ")"
        )