from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from validacion_honorarios.db.models import (
    Aduana,
    Proveedor,
)


class ProveedorRepository:
    """Acceso a datos de la entidad Proveedor."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(
        self,
        busqueda: str | None = None,
        aduana_id: int | None = None,
    ):
        statement = (
            select(Proveedor)
            .join(
                Proveedor.aduana
            )
            .options(
                selectinload(
                    Proveedor.aduana
                )
            )
        )

        if busqueda:
            termino = f"%{busqueda.strip()}%"

            statement = statement.where(
                or_(
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
                )
            )

        if aduana_id is not None:
            statement = statement.where(
                Proveedor.aduana_id
                == aduana_id
            )

        statement = statement.order_by(
            Proveedor.razon_social,
            Proveedor.cuit,
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def obtener_por_id(
        self,
        proveedor_id: int,
    ) -> Proveedor | None:
        statement = (
            select(Proveedor)
            .options(
                selectinload(
                    Proveedor.aduana
                ),
                selectinload(
                    Proveedor.esquemas_cotizacion
                ),
            )
            .where(
                Proveedor.proveedor_id
                == proveedor_id
            )
        )

        return self.session.scalar(
            statement
        )

    def obtener_por_cuit(
        self,
        cuit: str,
    ) -> Proveedor | None:
        statement = (
            select(Proveedor)
            .options(
                selectinload(
                    Proveedor.aduana
                )
            )
            .where(
                Proveedor.cuit == cuit
            )
        )

        return self.session.scalar(
            statement
        )

    def existe_cuit(
        self,
        cuit: str,
        excluir_proveedor_id: int | None = None,
    ) -> bool:
        statement = select(
            func.count(
                Proveedor.proveedor_id
            )
        ).where(
            Proveedor.cuit == cuit
        )

        if excluir_proveedor_id is not None:
            statement = statement.where(
                Proveedor.proveedor_id
                != excluir_proveedor_id
            )

        cantidad = self.session.scalar(
            statement
        )

        return bool(cantidad)

    def existe_razon_social(
        self,
        razon_social: str,
        excluir_proveedor_id: int | None = None,
    ) -> bool:
        statement = select(
            func.count(
                Proveedor.proveedor_id
            )
        ).where(
            func.lower(
                Proveedor.razon_social
            )
            == razon_social.lower()
        )

        if excluir_proveedor_id is not None:
            statement = statement.where(
                Proveedor.proveedor_id
                != excluir_proveedor_id
            )

        cantidad = self.session.scalar(
            statement
        )

        return bool(cantidad)

    def crear(
        self,
        aduana_id: int,
        razon_social: str,
        cuit: str,
    ) -> Proveedor:
        proveedor = Proveedor(
            aduana_id=aduana_id,
            razon_social=razon_social,
            cuit=cuit,
        )

        self.session.add(
            proveedor
        )

        self.session.flush()

        return proveedor

    def actualizar(
        self,
        proveedor: Proveedor,
        aduana_id: int,
        razon_social: str,
        cuit: str,
    ) -> Proveedor:
        proveedor.aduana_id = aduana_id
        proveedor.razon_social = razon_social
        proveedor.cuit = cuit

        self.session.flush()

        return proveedor

    def eliminar(
        self,
        proveedor: Proveedor,
    ) -> None:
        self.session.delete(
            proveedor
        )

        self.session.flush()