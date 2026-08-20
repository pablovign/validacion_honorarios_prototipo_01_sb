from datetime import date
from decimal import Decimal
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
from validacion_honorarios.repositories.canal_selectividad_repository import (
    CanalSelectividadRepository,
)
from validacion_honorarios.repositories.esquema_cotizacion_repository import (
    EsquemaCotizacionRepository,
)
from validacion_honorarios.repositories.proveedor_repository import (
    ProveedorRepository,
)
from validacion_honorarios.repositories.tarifa_zona_canal_repository import (
    TarifaZonaCanalRepository,
)
from validacion_honorarios.repositories.zona_repository import (
    ZonaRepository,
)


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

        zona_repository = ZonaRepository(
            session
        )

        canal_repository = (
            CanalSelectividadRepository(
                session
            )
        )

        tarifa_repository = (
            TarifaZonaCanalRepository(
                session
            )
        )

        aduana = aduana_repository.crear(
            codigo="996",
            nombre="ADUANA TEMPORAL ZONAS",
        )

        proveedor = proveedor_repository.crear(
            aduana_id=aduana.aduana_id,
            razon_social=(
                "Proveedor temporal zonas SRL"
            ),
            cuit="30666666666",
        )

        esquema = esquema_repository.crear(
            proveedor_id=(
                proveedor.proveedor_id
            ),
            fecha_inicio=date(
                2026,
                10,
                1,
            ),
            moneda_codigo="ARS",
            observaciones=None,
        )

        zona = zona_repository.crear(
            esquema_cotizacion_id=(
                esquema.esquema_cotizacion_id
            ),
            nombre="GENERAL",
        )

        canal = canal_repository.obtener_por_nombre(
            "VERDE"
        )

        if canal is None:
            raise RuntimeError(
                "No existe el canal VERDE."
            )

        tarifa = tarifa_repository.crear(
            zona_id=zona.zona_id,
            canal_selectividad_id=(
                canal.canal_selectividad_id
            ),
            monto=Decimal("100000.00"),
        )

        print(
            "Zona creada:",
            zona.zona_id,
            zona.nombre,
        )

        print(
            "Tarifa creada:",
            canal.nombre,
            tarifa.monto,
        )

        tarifa_repository.actualizar(
            tarifa=tarifa,
            monto=Decimal("125000.00"),
        )

        assert (
            tarifa.monto
            == Decimal("125000.00")
        )

        print(
            "Actualización: correcta."
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