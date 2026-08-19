from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from validacion_honorarios.db.models.base import Base


if TYPE_CHECKING:
    from validacion_honorarios.db.models.tarifa_dia_hora import (
        TarifaAdicionalDiaHora,
    )


class DiaHora(Base):
    __tablename__ = "dia_hora"

    __table_args__ = (
        UniqueConstraint(
            "dia",
            "hora",
            name="uq_dia_hora",
        ),
    )

    dia_hora_id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    dia: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    hora: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    tarifas_adicionales: Mapped[
        list["TarifaAdicionalDiaHora"]
    ] = relationship(
        back_populates="dia_hora",
        passive_deletes=True,
    )

    @property
    def nombre_dia(self) -> str:
        nombres = {
            1: "Lunes",
            2: "Martes",
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
            6: "Sábado",
            7: "Domingo",
        }

        return nombres.get(
            self.dia,
            f"Día {self.dia}",
        )

    @property
    def hora_desde(self) -> str:
        return f"{self.hora:02d}:00"

    @property
    def hora_hasta(self) -> str:
        hora_siguiente = (self.hora + 1) % 24

        return f"{hora_siguiente:02d}:00"

    @property
    def descripcion(self) -> str:
        return (
            f"{self.nombre_dia}, "
            f"{self.hora_desde} a "
            f"{self.hora_hasta}"
        )

    @property
    def orden_semanal(self) -> int:
        return (
            (self.dia - 1) * 24
            + self.hora
        )

    def __repr__(self) -> str:
        return (
            "DiaHora("
            f"dia_hora_id={self.dia_hora_id!r}, "
            f"dia={self.dia!r}, "
            f"hora={self.hora!r}"
            ")"
        )