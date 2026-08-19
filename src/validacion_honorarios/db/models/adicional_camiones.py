from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.esquema_cotizacion import (
        EsquemaCotizacion,
    )
    from validacion_honorarios.db.models.tarifa_camiones_zona import (
        TarifaAdicionalCamionesZona,
    )


class AdicionalCamiones(Base):
    __tablename__ = "adicional_camiones"

    __table_args__ = (
        UniqueConstraint(
            "esquema_cotizacion_id",
            "nombre",
            name="uq_adicional_camiones_nombre",
        ),
        UniqueConstraint(
            "adicional_camiones_id",
            "esquema_cotizacion_id",
            name="uq_adicional_camiones_id_esquema",
        ),
    )

    adicional_camiones_id: Mapped[int] = mapped_column(
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

    camion_desde: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    camion_hasta: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    esquema_cotizacion: Mapped["EsquemaCotizacion"] = relationship(
        back_populates="adicionales_camiones",
    )

    tarifas_por_zona: Mapped[
        list["TarifaAdicionalCamionesZona"]
    ] = relationship(
        back_populates="adicional_camiones",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="zona,tarifas_adicionales_camiones",
    )

    @property
    def descripcion_rango(self) -> str:
        if self.camion_hasta is None:
            return f"Desde el camión {self.camion_desde}"

        if self.camion_desde == self.camion_hasta:
            return f"Camión {self.camion_desde}"

        return (
            f"Camiones {self.camion_desde} "
            f"a {self.camion_hasta}"
        )

    def contiene_camion(self, numero_camion: int) -> bool:
        if numero_camion < self.camion_desde:
            return False

        return (
            self.camion_hasta is None
            or numero_camion <= self.camion_hasta
        )

    def __repr__(self) -> str:
        return (
            "AdicionalCamiones("
            f"adicional_camiones_id="
            f"{self.adicional_camiones_id!r}, "
            f"esquema_cotizacion_id="
            f"{self.esquema_cotizacion_id!r}, "
            f"nombre={self.nombre!r}, "
            f"camion_desde={self.camion_desde!r}, "
            f"camion_hasta={self.camion_hasta!r}"
            ")"
        )