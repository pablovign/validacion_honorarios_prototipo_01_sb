from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.adicional_camiones import (
        AdicionalCamiones,
    )
    from validacion_honorarios.db.models.esquema_cotizacion import (
        EsquemaCotizacion,
    )
    from validacion_honorarios.db.models.zona import Zona


class TarifaAdicionalCamionesZona(Base):
    __tablename__ = "tarifa_adicional_camiones_zona"

    __table_args__ = (
        ForeignKeyConstraint(
            [
                "adicional_camiones_id",
                "esquema_cotizacion_id",
            ],
            [
                "adicional_camiones.adicional_camiones_id",
                "adicional_camiones.esquema_cotizacion_id",
            ],
            name="fk_tarifa_adicional_camiones_rango",
            onupdate="RESTRICT",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "zona_id",
                "esquema_cotizacion_id",
            ],
            [
                "zona.zona_id",
                "zona.esquema_cotizacion_id",
            ],
            name="fk_tarifa_adicional_camiones_zona",
            onupdate="RESTRICT",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "adicional_camiones_id",
            "zona_id",
            name="uq_tarifa_adicional_camiones_zona",
        ),
    )

    tarifa_adicional_camiones_zona_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    esquema_cotizacion_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "esquema_cotizacion.esquema_cotizacion_id",
            name="fk_tarifa_adicional_camiones_esquema",
            onupdate="RESTRICT",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    adicional_camiones_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    zona_id: Mapped[int] = mapped_column(
        BigInteger,
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

    esquema_cotizacion: Mapped["EsquemaCotizacion"] = relationship(
        foreign_keys=[esquema_cotizacion_id],
        viewonly=True,
    )

    adicional_camiones: Mapped["AdicionalCamiones"] = relationship(
        back_populates="tarifas_por_zona",
        foreign_keys=[
            adicional_camiones_id,
            esquema_cotizacion_id,
        ],
        overlaps=(
            "esquema_cotizacion,"
            "zona,"
            "tarifas_adicionales_camiones"
        ),
    )

    zona: Mapped["Zona"] = relationship(
        back_populates="tarifas_adicionales_camiones",
        foreign_keys=[
            zona_id,
            esquema_cotizacion_id,
        ],
        overlaps=(
            "adicional_camiones,"
            "esquema_cotizacion,"
            "tarifas_por_zona"
        ),
    )

    def __repr__(self) -> str:
        return (
            "TarifaAdicionalCamionesZona("
            f"id="
            f"{self.tarifa_adicional_camiones_zona_id!r}, "
            f"esquema_cotizacion_id="
            f"{self.esquema_cotizacion_id!r}, "
            f"adicional_camiones_id="
            f"{self.adicional_camiones_id!r}, "
            f"zona_id={self.zona_id!r}, "
            f"monto={self.monto!r}"
            ")"
        )