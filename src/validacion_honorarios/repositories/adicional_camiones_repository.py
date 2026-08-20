from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from validacion_honorarios.db.models import (
    AdicionalCamiones,
    TarifaAdicionalCamionesZona,
)


class AdicionalCamionesRepository:
    """Acceso a los tramos adicionales por camiones."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def listar_por_esquema(
        self,
        esquema_cotizacion_id: int,
    ):
        statement = (
            select(AdicionalCamiones)
            .options(
                selectinload(
                    AdicionalCamiones.tarifas_por_zona
                ).selectinload(
                    TarifaAdicionalCamionesZona.zona
                )
            )
            .where(
                AdicionalCamiones.esquema_cotizacion_id
                == esquema_cotizacion_id
            )
            .order_by(
                AdicionalCamiones.camion_desde,
                AdicionalCamiones.camion_hasta,
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def obtener_por_id(
        self,
        adicional_camiones_id: int,
    ) -> AdicionalCamiones | None:
        statement = (
            select(AdicionalCamiones)
            .options(
                selectinload(
                    AdicionalCamiones.tarifas_por_zona
                ).selectinload(
                    TarifaAdicionalCamionesZona.zona
                )
            )
            .where(
                AdicionalCamiones.adicional_camiones_id
                == adicional_camiones_id
            )
        )

        return self.session.scalar(
            statement
        )

    def crear(
        self,
        esquema_cotizacion_id: int,
        nombre: str,
        camion_desde: int,
        camion_hasta: int | None,
    ) -> AdicionalCamiones:
        adicional = AdicionalCamiones(
            esquema_cotizacion_id=(
                esquema_cotizacion_id
            ),
            nombre=nombre,
            camion_desde=camion_desde,
            camion_hasta=camion_hasta,
        )

        self.session.add(adicional)
        self.session.flush()

        return adicional

    def actualizar(
        self,
        adicional: AdicionalCamiones,
        nombre: str,
        camion_desde: int,
        camion_hasta: int | None,
    ) -> AdicionalCamiones:
        adicional.nombre = nombre
        adicional.camion_desde = camion_desde
        adicional.camion_hasta = camion_hasta

        self.session.flush()

        return adicional

    def eliminar(
        self,
        adicional: AdicionalCamiones,
    ) -> None:
        self.session.delete(adicional)
        self.session.flush()