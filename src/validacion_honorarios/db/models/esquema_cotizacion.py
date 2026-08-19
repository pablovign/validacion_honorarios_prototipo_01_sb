from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.adicional_camiones import (
        AdicionalCamiones,
    )
    from validacion_honorarios.db.models.proveedor import Proveedor
    from validacion_honorarios.db.models.tarifa_dia_hora import (
        TarifaAdicionalDiaHora,
    )
    from validacion_honorarios.db.models.zona import Zona


class EsquemaCotizacion(Base):
    __tablename__ = "esquema_cotizacion"

    esquema_cotizacion_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    proveedor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "proveedor.proveedor_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    fecha_fin: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        default="BORRADOR",
    )

    moneda_codigo: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    proveedor: Mapped["Proveedor"] = relationship(
        back_populates="esquemas_cotizacion",
    )

    zonas: Mapped[list["Zona"]] = relationship(
        back_populates="esquema_cotizacion",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    adicionales_camiones: Mapped[
        list["AdicionalCamiones"]
    ] = relationship(
        back_populates="esquema_cotizacion",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    tarifas_adicionales_dia_hora: Mapped[
        list["TarifaAdicionalDiaHora"]
    ] = relationship(
        back_populates="esquema_cotizacion",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def esta_vigente(self) -> bool:
        hoy = date.today()

        return (
            self.estado == "APROBADO"
            and self.fecha_inicio <= hoy
            and (
                self.fecha_fin is None
                or hoy < self.fecha_fin
            )
        )

    @property
    def utiliza_adicional_horario(self) -> bool:
        return bool(
            self.tarifas_adicionales_dia_hora
        )

    @property
    def configuracion_horaria_completa(self) -> bool:
        cantidad = len(
            self.tarifas_adicionales_dia_hora
        )

        return cantidad in (0, 168)

    def __repr__(self) -> str:
        return (
            "EsquemaCotizacion("
            f"esquema_cotizacion_id="
            f"{self.esquema_cotizacion_id!r}, "
            f"proveedor_id={self.proveedor_id!r}, "
            f"fecha_inicio={self.fecha_inicio!r}, "
            f"fecha_fin={self.fecha_fin!r}, "
            f"estado={self.estado!r}, "
            f"moneda_codigo={self.moneda_codigo!r}"
            ")"
        )