from datetime import date
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
from validacion_honorarios.repositories.esquema_cotizacion_repository import (
    EsquemaCotizacionRepository,
)
from validacion_honorarios.repositories.proveedor_repository import (
    ProveedorRepository,
)


TEST_ADUANA_CODE = "997"
TEST_ADUANA_NAME = "ADUANA TEMPORAL ESQUEMA"
TEST_CUIT = "30777777777"


def main() -> None:
    session = SessionFactory()

    try:
        aduana_repository = AduanaRepository(
            session
        )

        proveedor_repository = (
            ProveedorRepository(session)
        )

        esquema_repository = (
            EsquemaCotizacionRepository(
                session
            )
        )

        aduana = aduana_repository.crear(
            codigo=TEST_ADUANA_CODE,
            nombre=TEST_ADUANA_NAME,
        )

        proveedor = proveedor_repository.crear(
            aduana_id=aduana.aduana_id,
            razon_social=(
                "Proveedor temporal esquema SRL"
            ),
            cuit=TEST_CUIT,
        )

        print(
            "Creando esquema temporal..."
        )

        esquema = esquema_repository.crear(
            proveedor_id=(
                proveedor.proveedor_id
            ),
            fecha_inicio=date(
                2026,
                8,
                1,
            ),
            moneda_codigo="ARS",
            observaciones=(
                "Esquema transaccional de prueba"
            ),
        )

        print(
            "Esquema creado:",
            esquema.esquema_cotizacion_id,
            esquema.estado,
            esquema.fecha_inicio,
            esquema.moneda_codigo,
        )

        encontrado = (
            esquema_repository.obtener_por_id(
                esquema.esquema_cotizacion_id
            )
        )

        assert encontrado is not None
        assert encontrado.estado == "BORRADOR"
        assert encontrado.fecha_fin is None

        print(
            "Consulta: correcta."
        )

        esquema_repository.actualizar(
            esquema=encontrado,
            proveedor_id=(
                proveedor.proveedor_id
            ),
            fecha_inicio=date(
                2026,
                9,
                1,
            ),
            moneda_codigo="USD",
            observaciones=(
                "Esquema modificado"
            ),
        )

        assert (
            encontrado.fecha_inicio
            == date(2026, 9, 1)
        )

        assert (
            encontrado.moneda_codigo
            == "USD"
        )

        print(
            "Actualización: correcta."
        )

        esquema_repository.cambiar_estado(
            esquema=encontrado,
            estado="RECHAZADO",
        )

        assert (
            encontrado.estado
            == "RECHAZADO"
        )

        print(
            "Cambio de estado: correcto."
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