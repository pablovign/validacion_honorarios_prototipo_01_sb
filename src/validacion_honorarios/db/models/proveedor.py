from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.aduana import Aduana
    from validacion_honorarios.db.models.esquema_cotizacion import (
        EsquemaCotizacion,
    )


class Proveedor(Base):
    __tablename__ = "proveedor"

    proveedor_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    aduana_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "aduana.aduana_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    razon_social: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    cuit: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
        unique=True,
    )

    aduana: Mapped["Aduana"] = relationship(
        back_populates="proveedores",
    )

    esquemas_cotizacion: Mapped[list["EsquemaCotizacion"]] = relationship(
        back_populates="proveedor",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            "Proveedor("
            f"proveedor_id={self.proveedor_id!r}, "
            f"razon_social={self.razon_social!r}, "
            f"cuit={self.cuit!r}"
            ")"
        )