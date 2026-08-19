from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from validacion_honorarios.db.models import Aduana


class AduanaRepository:
    """Acceso a datos de la entidad Aduana."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(
        self,
        busqueda: str | None = None,
    ):
        statement = select(Aduana)

        if busqueda:
            termino = f"%{busqueda.strip()}%"

            statement = statement.where(
                or_(
                    Aduana.codigo.ilike(termino),
                    Aduana.nombre.ilike(termino),
                )
            )

        statement = statement.order_by(
            Aduana.codigo,
            Aduana.nombre,
        )

        return list(
            self.session.scalars(statement).all()
        )

    def obtener_por_id(
        self,
        aduana_id: int,
    ) -> Aduana | None:
        return self.session.get(
            Aduana,
            aduana_id,
        )

    def obtener_por_codigo(
        self,
        codigo: str,
    ) -> Aduana | None:
        statement = select(Aduana).where(
            Aduana.codigo == codigo
        )

        return self.session.scalar(statement)

    def obtener_por_nombre(
        self,
        nombre: str,
    ) -> Aduana | None:
        statement = select(Aduana).where(
            func.lower(Aduana.nombre)
            == nombre.lower()
        )

        return self.session.scalar(statement)

    def existe_codigo(
        self,
        codigo: str,
        excluir_aduana_id: int | None = None,
    ) -> bool:
        statement = select(
            func.count(Aduana.aduana_id)
        ).where(
            Aduana.codigo == codigo
        )

        if excluir_aduana_id is not None:
            statement = statement.where(
                Aduana.aduana_id
                != excluir_aduana_id
            )

        cantidad = self.session.scalar(statement)

        return bool(cantidad)

    def existe_nombre(
        self,
        nombre: str,
        excluir_aduana_id: int | None = None,
    ) -> bool:
        statement = select(
            func.count(Aduana.aduana_id)
        ).where(
            func.lower(Aduana.nombre)
            == nombre.lower()
        )

        if excluir_aduana_id is not None:
            statement = statement.where(
                Aduana.aduana_id
                != excluir_aduana_id
            )

        cantidad = self.session.scalar(statement)

        return bool(cantidad)

    def crear(
        self,
        codigo: str,
        nombre: str,
    ) -> Aduana:
        aduana = Aduana(
            codigo=codigo,
            nombre=nombre,
        )

        self.session.add(aduana)
        self.session.flush()

        return aduana

    def actualizar(
        self,
        aduana: Aduana,
        codigo: str,
        nombre: str,
    ) -> Aduana:
        aduana.codigo = codigo
        aduana.nombre = nombre

        self.session.flush()

        return aduana

    def eliminar(
        self,
        aduana: Aduana,
    ) -> None:
        self.session.delete(aduana)
        self.session.flush()