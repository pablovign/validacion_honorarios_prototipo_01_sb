from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.esquema_cotizacion import (
        EsquemaCotizacion,
    )
    from validacion_honorarios.db.models.tarifa_zona_canal import (
        TarifaZonaCanalSelectividad,
    )
    from validacion_honorarios.db.models.tarifa_camiones_zona import (
        TarifaAdicionalCamionesZona,
    )


class Zona(Base):
    __tablename__ = "zona"

    zona_id: Mapped[int] = mapped_column(
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

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    esquema_cotizacion: Mapped["EsquemaCotizacion"] = relationship(
        back_populates="zonas",
    )

    tarifas_por_canal: Mapped[
        list["TarifaZonaCanalSelectividad"]
    ] = relationship(
        back_populates="zona",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    tarifas_adicionales_camiones: Mapped[
        list["TarifaAdicionalCamionesZona"]
    ] = relationship(
        back_populates="zona",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="adicional_camiones,tarifas_por_zona",
    )

    def __repr__(self) -> str:
        return (
            "Zona("
            f"zona_id={self.zona_id!r}, "
            f"esquema_cotizacion_id="
            f"{self.esquema_cotizacion_id!r}, "
            f"nombre={self.nombre!r}"
            ")"
        )