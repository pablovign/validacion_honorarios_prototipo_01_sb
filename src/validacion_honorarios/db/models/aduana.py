from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.proveedor import Proveedor


class Aduana(Base):
    __tablename__ = "aduana"

    aduana_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    codigo: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        unique=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )

    proveedores: Mapped[list["Proveedor"]] = relationship(
        back_populates="aduana",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            "Aduana("
            f"aduana_id={self.aduana_id!r}, "
            f"codigo={self.codigo!r}, "
            f"nombre={self.nombre!r}"
            ")"
        )