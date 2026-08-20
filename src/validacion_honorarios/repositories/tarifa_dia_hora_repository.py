from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from validacion_honorarios.db.models import (
    DiaHora,
    TarifaAdicionalDiaHora,
)


class TarifaDiaHoraRepository:
    """Persistencia de tarifas adicionales por día y hora."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def listar_catalogo(self):
        statement = select(
            DiaHora
        ).order_by(
            DiaHora.dia,
            DiaHora.hora,
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def listar_por_esquema(
        self,
        esquema_cotizacion_id: int,
    ):
        statement = (
            select(TarifaAdicionalDiaHora)
            .options(
                selectinload(
                    TarifaAdicionalDiaHora.dia_hora
                )
            )
            .join(
                TarifaAdicionalDiaHora.dia_hora
            )
            .where(
                TarifaAdicionalDiaHora
                .esquema_cotizacion_id
                == esquema_cotizacion_id
            )
            .order_by(
                DiaHora.dia,
                DiaHora.hora,
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def obtener(
        self,
        esquema_cotizacion_id: int,
        dia_hora_id: int,
    ) -> TarifaAdicionalDiaHora | None:
        statement = (
            select(TarifaAdicionalDiaHora)
            .options(
                selectinload(
                    TarifaAdicionalDiaHora.dia_hora
                )
            )
            .where(
                TarifaAdicionalDiaHora
                .esquema_cotizacion_id
                == esquema_cotizacion_id,
                TarifaAdicionalDiaHora.dia_hora_id
                == dia_hora_id,
            )
        )

        return self.session.scalar(
            statement
        )

    def crear(
        self,
        esquema_cotizacion_id: int,
        dia_hora_id: int,
        monto: Decimal,
    ) -> TarifaAdicionalDiaHora:
        tarifa = TarifaAdicionalDiaHora(
            esquema_cotizacion_id=(
                esquema_cotizacion_id
            ),
            dia_hora_id=dia_hora_id,
            monto=monto,
        )

        self.session.add(tarifa)
        self.session.flush()

        return tarifa

    def actualizar(
        self,
        tarifa: TarifaAdicionalDiaHora,
        monto: Decimal,
    ) -> TarifaAdicionalDiaHora:
        tarifa.monto = monto

        self.session.flush()

        return tarifa

    def eliminar_todas_por_esquema(
        self,
        esquema_cotizacion_id: int,
    ) -> int:
        statement = delete(
            TarifaAdicionalDiaHora
        ).where(
            TarifaAdicionalDiaHora
            .esquema_cotizacion_id
            == esquema_cotizacion_id
        )

        result = self.session.execute(
            statement
        )

        self.session.flush()

        return result.rowcount or 0