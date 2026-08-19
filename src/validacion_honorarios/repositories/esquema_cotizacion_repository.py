from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from validacion_honorarios.db.models import (
    Aduana,
    EsquemaCotizacion,
    Proveedor,
)


class EsquemaCotizacionRepository:
    """Acceso a datos de esquemas de cotización."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def listar(
        self,
        busqueda: str | None = None,
        proveedor_id: int | None = None,
        aduana_id: int | None = None,
        estado: str | None = None,
        moneda_codigo: str | None = None,
    ):
        statement = (
            select(EsquemaCotizacion)
            .join(
                EsquemaCotizacion.proveedor
            )
            .join(
                Proveedor.aduana
            )
            .options(
                selectinload(
                    EsquemaCotizacion.proveedor
                ).selectinload(
                    Proveedor.aduana
                ),
                selectinload(
                    EsquemaCotizacion.zonas
                ),
                selectinload(
                    EsquemaCotizacion
                    .adicionales_camiones
                ),
                selectinload(
                    EsquemaCotizacion
                    .tarifas_adicionales_dia_hora
                ),
            )
        )

        if busqueda:
            termino = f"%{busqueda.strip()}%"

            condiciones = [
                Proveedor.razon_social.ilike(
                    termino
                ),
                Proveedor.cuit.ilike(
                    termino
                ),
                Aduana.codigo.ilike(
                    termino
                ),
                Aduana.nombre.ilike(
                    termino
                ),
            ]

            if busqueda.strip().isdigit():
                condiciones.append(
                    EsquemaCotizacion
                    .esquema_cotizacion_id
                    == int(busqueda.strip())
                )

            statement = statement.where(
                or_(*condiciones)
            )

        if proveedor_id is not None:
            statement = statement.where(
                EsquemaCotizacion.proveedor_id
                == proveedor_id
            )

        if aduana_id is not None:
            statement = statement.where(
                Proveedor.aduana_id
                == aduana_id
            )

        if estado is not None:
            statement = statement.where(
                EsquemaCotizacion.estado
                == estado
            )

        if moneda_codigo is not None:
            statement = statement.where(
                EsquemaCotizacion.moneda_codigo
                == moneda_codigo
            )

        statement = statement.order_by(
            EsquemaCotizacion.fecha_inicio.desc(),
            EsquemaCotizacion
            .esquema_cotizacion_id
            .desc(),
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def obtener_por_id(
        self,
        esquema_cotizacion_id: int,
    ) -> EsquemaCotizacion | None:
        statement = (
            select(EsquemaCotizacion)
            .options(
                selectinload(
                    EsquemaCotizacion.proveedor
                ).selectinload(
                    Proveedor.aduana
                ),
                selectinload(
                    EsquemaCotizacion.zonas
                ),
                selectinload(
                    EsquemaCotizacion
                    .adicionales_camiones
                ),
                selectinload(
                    EsquemaCotizacion
                    .tarifas_adicionales_dia_hora
                ),
            )
            .where(
                EsquemaCotizacion
                .esquema_cotizacion_id
                == esquema_cotizacion_id
            )
        )

        return self.session.scalar(
            statement
        )

    def crear(
        self,
        proveedor_id: int,
        fecha_inicio: date,
        moneda_codigo: str,
        observaciones: str | None,
    ) -> EsquemaCotizacion:
        esquema = EsquemaCotizacion(
            proveedor_id=proveedor_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=None,
            estado="BORRADOR",
            moneda_codigo=moneda_codigo,
            observaciones=observaciones,
        )

        self.session.add(esquema)
        self.session.flush()

        return esquema

    def actualizar(
        self,
        esquema: EsquemaCotizacion,
        proveedor_id: int,
        fecha_inicio: date,
        moneda_codigo: str,
        observaciones: str | None,
    ) -> EsquemaCotizacion:
        esquema.proveedor_id = proveedor_id
        esquema.fecha_inicio = fecha_inicio
        esquema.moneda_codigo = moneda_codigo
        esquema.observaciones = observaciones

        self.session.flush()

        return esquema

    def cambiar_estado(
        self,
        esquema: EsquemaCotizacion,
        estado: str,
    ) -> EsquemaCotizacion:
        esquema.estado = estado

        self.session.flush()

        return esquema

    def eliminar(
        self,
        esquema: EsquemaCotizacion,
    ) -> None:
        self.session.delete(esquema)
        self.session.flush()