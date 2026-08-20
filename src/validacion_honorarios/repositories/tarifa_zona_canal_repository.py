from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from validacion_honorarios.db.models import (
    TarifaZonaCanalSelectividad,
)


class TarifaZonaCanalRepository:
    """Acceso a tarifas principales por zona y canal."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def obtener(
        self,
        zona_id: int,
        canal_selectividad_id: int,
    ) -> TarifaZonaCanalSelectividad | None:
        statement = select(
            TarifaZonaCanalSelectividad
        ).where(
            TarifaZonaCanalSelectividad.zona_id
            == zona_id,
            TarifaZonaCanalSelectividad
            .canal_selectividad_id
            == canal_selectividad_id,
        )

        return self.session.scalar(
            statement
        )

    def crear(
        self,
        zona_id: int,
        canal_selectividad_id: int,
        monto: Decimal,
    ) -> TarifaZonaCanalSelectividad:
        tarifa = TarifaZonaCanalSelectividad(
            zona_id=zona_id,
            canal_selectividad_id=(
                canal_selectividad_id
            ),
            monto=monto,
        )

        self.session.add(tarifa)
        self.session.flush()

        return tarifa

    def actualizar(
        self,
        tarifa: TarifaZonaCanalSelectividad,
        monto: Decimal,
    ) -> TarifaZonaCanalSelectividad:
        tarifa.monto = monto

        self.session.flush()

        return tarifa

    def eliminar(
        self,
        tarifa: TarifaZonaCanalSelectividad,
    ) -> None:
        self.session.delete(tarifa)
        self.session.flush()