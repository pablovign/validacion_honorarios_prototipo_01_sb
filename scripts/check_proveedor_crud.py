from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR),
    )


from validacion_honorarios.db.connection import (
    SessionFactory,
)
from validacion_honorarios.repositories.aduana_repository import (
    AduanaRepository,
)
from validacion_honorarios.repositories.proveedor_repository import (
    ProveedorRepository,
)


TEST_CUSTOMS_CODE = "998"
TEST_CUSTOMS_NAME = "ADUANA TEMPORAL PROVEEDOR"
TEST_CUIT = "30999999999"


def main() -> None:
    session = SessionFactory()

    try:
        aduana_repository = AduanaRepository(
            session
        )

        proveedor_repository = (
            ProveedorRepository(session)
        )

        aduana_existente = (
            aduana_repository
            .obtener_por_codigo(
                TEST_CUSTOMS_CODE
            )
        )

        if aduana_existente is not None:
            raise RuntimeError(
                "Ya existe una aduana con el "
                f"código {TEST_CUSTOMS_CODE}."
            )

        proveedor_existente = (
            proveedor_repository
            .obtener_por_cuit(
                TEST_CUIT
            )
        )

        if proveedor_existente is not None:
            raise RuntimeError(
                "Ya existe un proveedor con "
                f"el CUIT {TEST_CUIT}."
            )

        print(
            "Creando aduana temporal..."
        )

        aduana = aduana_repository.crear(
            codigo=TEST_CUSTOMS_CODE,
            nombre=TEST_CUSTOMS_NAME,
        )

        print(
            "Aduana creada:",
            aduana.aduana_id,
            aduana.codigo,
            aduana.nombre,
        )

        print(
            "Creando proveedor temporal..."
        )

        proveedor = proveedor_repository.crear(
            aduana_id=aduana.aduana_id,
            razon_social=(
                "Proveedor temporal SRL"
            ),
            cuit=TEST_CUIT,
        )

        print(
            "Proveedor creado:",
            proveedor.proveedor_id,
            proveedor.razon_social,
            proveedor.cuit,
        )

        encontrado = (
            proveedor_repository
            .obtener_por_id(
                proveedor.proveedor_id
            )
        )

        assert encontrado is not None
        assert encontrado.cuit == TEST_CUIT
        assert (
            encontrado.aduana.codigo
            == TEST_CUSTOMS_CODE
        )

        print(
            "Consulta y relación con aduana: "
            "correctas."
        )

        proveedor_repository.actualizar(
            proveedor=encontrado,
            aduana_id=aduana.aduana_id,
            razon_social=(
                "Proveedor temporal modificado SRL"
            ),
            cuit=TEST_CUIT,
        )

        assert (
            encontrado.razon_social
            == (
                "Proveedor temporal "
                "modificado SRL"
            )
        )

        print(
            "Actualización: correcta."
        )

        print()
        print(
            "Revirtiendo la transacción "
            "de prueba..."
        )

        session.rollback()

        print(
            "Rollback completado. "
            "No se conservaron datos."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()