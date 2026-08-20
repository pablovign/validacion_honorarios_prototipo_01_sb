from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from validacion_honorarios.db.models import (
    TarifaAdicionalCamionesZona,
)


class TarifaCamionesZonaRepository:
    """Acceso a tarifas de tramos de camiones por zona."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def obtener(
        self,
        adicional_camiones_id: int,
        zona_id: int,
    ) -> TarifaAdicionalCamionesZona | None:
        statement = select(
            TarifaAdicionalCamionesZona
        ).where(
            TarifaAdicionalCamionesZona
            .adicional_camiones_id
            == adicional_camiones_id,
            TarifaAdicionalCamionesZona.zona_id
            == zona_id,
        )

        return self.session.scalar(
            statement
        )

    def crear(
        self,
        esquema_cotizacion_id: int,
        adicional_camiones_id: int,
        zona_id: int,
        monto: Decimal,
    ) -> TarifaAdicionalCamionesZona:
        tarifa = TarifaAdicionalCamionesZona(
            esquema_cotizacion_id=(
                esquema_cotizacion_id
            ),
            adicional_camiones_id=(
                adicional_camiones_id
            ),
            zona_id=zona_id,
            monto=monto,
        )

        self.session.add(
            tarifa
        )

        self.session.flush()

        return tarifa

    def actualizar(
        self,
        tarifa: TarifaAdicionalCamionesZona,
        monto: Decimal,
    ) -> TarifaAdicionalCamionesZona:
        tarifa.monto = monto

        self.session.flush()

        return tarifa

    def eliminar(
        self,
        tarifa: TarifaAdicionalCamionesZona,
    ) -> None:
        self.session.delete(
            tarifa
        )

        self.session.flush()