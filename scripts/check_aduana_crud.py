from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from sqlalchemy import select

from validacion_honorarios.db.connection import (
    SessionFactory,
)
from validacion_honorarios.db.models import Aduana
from validacion_honorarios.repositories.aduana_repository import (
    AduanaRepository,
)


TEST_CODE = "999"
TEST_NAME = "ADUANA TEMPORAL DE PRUEBA"


def main() -> None:
    session = SessionFactory()

    try:
        repository = AduanaRepository(session)

        existente = repository.obtener_por_codigo(
            TEST_CODE
        )

        if existente is not None:
            raise RuntimeError(
                "Ya existe una aduana con el código "
                f"{TEST_CODE}. El script no eliminará "
                "ni modificará datos preexistentes."
            )

        print("Creando aduana temporal...")

        aduana = repository.crear(
            codigo=TEST_CODE,
            nombre=TEST_NAME,
        )

        print(
            "Creada:",
            aduana.aduana_id,
            aduana.codigo,
            aduana.nombre,
        )

        aduana_encontrada = (
            repository.obtener_por_id(
                aduana.aduana_id
            )
        )

        assert aduana_encontrada is not None
        assert aduana_encontrada.codigo == TEST_CODE

        print("Consulta por ID: correcta.")

        repository.actualizar(
            aduana=aduana_encontrada,
            codigo=TEST_CODE,
            nombre=(
                "ADUANA TEMPORAL MODIFICADA"
            ),
        )

        assert (
            aduana_encontrada.nombre
            == "ADUANA TEMPORAL MODIFICADA"
        )

        print("Actualización: correcta.")

        cantidad = session.scalar(
            select(Aduana)
            .where(
                Aduana.aduana_id
                == aduana.aduana_id
            )
            .with_only_columns(
                Aduana.aduana_id
            )
        )

        assert cantidad is not None

        print("Persistencia en sesión: correcta.")

        print()
        print(
            "Revirtiendo la transacción de prueba..."
        )

        session.rollback()

        print(
            "Rollback completado. "
            "No se conservaron datos de prueba."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()