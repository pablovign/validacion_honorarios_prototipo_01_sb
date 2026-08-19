from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from sqlalchemy import func, inspect, select
from sqlalchemy.orm import selectinload

from validacion_honorarios.db.connection import (
    engine,
    session_scope,
)
from validacion_honorarios.db.models import (
    AdicionalCamiones,
    Aduana,
    CanalSelectividad,
    DiaHora,
    EsquemaCotizacion,
    Proveedor,
    TarifaAdicionalCamionesZona,
    TarifaAdicionalDiaHora,
    TarifaZonaCanalSelectividad,
    Zona,
)


EXPECTED_TABLES = {
    "aduana",
    "proveedor",
    "esquema_cotizacion",
    "zona",
    "canal_selectividad",
    "tarifa_zona_canal_selectividad",
    "adicional_camiones",
    "tarifa_adicional_camiones_zona",
    "dia_hora",
    "tarifa_adicional_dia_hora",
}


def show_table_information() -> None:
    inspector = inspect(engine)

    existing_tables = set(
        inspector.get_table_names(
            schema="public",
        )
    )

    print("Tablas verificadas:")

    for table_name in sorted(EXPECTED_TABLES):
        exists = table_name in existing_tables
        status = "OK" if exists else "NO ENCONTRADA"

        print(f"  {table_name}: {status}")


def show_record_counts() -> None:
    model_descriptions = (
        (
            "Aduanas",
            Aduana,
            Aduana.aduana_id,
        ),
        (
            "Proveedores",
            Proveedor,
            Proveedor.proveedor_id,
        ),
        (
            "Esquemas",
            EsquemaCotizacion,
            EsquemaCotizacion.esquema_cotizacion_id,
        ),
        (
            "Zonas",
            Zona,
            Zona.zona_id,
        ),
        (
            "Canales",
            CanalSelectividad,
            CanalSelectividad.canal_selectividad_id,
        ),
        (
            "Tarifas zona-canal",
            TarifaZonaCanalSelectividad,
            TarifaZonaCanalSelectividad
            .tarifa_zona_canal_selectividad_id,
        ),
        (
            "Tramos adicionales de camiones",
            AdicionalCamiones,
            AdicionalCamiones.adicional_camiones_id,
        ),
        (
            "Tarifas adicionales camión-zona",
            TarifaAdicionalCamionesZona,
            TarifaAdicionalCamionesZona
            .tarifa_adicional_camiones_zona_id,
        ),
        (
            "Posiciones día-hora",
            DiaHora,
            DiaHora.dia_hora_id,
        ),
        (
            "Tarifas adicionales día-hora",
            TarifaAdicionalDiaHora,
            TarifaAdicionalDiaHora
            .tarifa_adicional_dia_hora_id,
        ),
    )

    print()
    print("Cantidad de registros:")

    with session_scope() as session:
        for label, model, primary_key in model_descriptions:
            count = session.scalar(
                select(
                    func.count(primary_key)
                ).select_from(model)
            )

            print(f"  {label}: {count}")


def show_channels() -> None:
    with session_scope() as session:
        channels = session.scalars(
            select(CanalSelectividad).order_by(
                CanalSelectividad.nombre,
            )
        ).all()

        print()
        print("Canales de selectividad:")

        if not channels:
            print("  No hay canales cargados.")
            return

        for channel in channels:
            print(
                f"  {channel.canal_selectividad_id}: "
                f"{channel.nombre}"
            )


def show_day_hour_information() -> None:
    with session_scope() as session:
        count = session.scalar(
            select(
                func.count(DiaHora.dia_hora_id)
            )
        )

        first_positions = session.scalars(
            select(DiaHora)
            .order_by(
                DiaHora.dia,
                DiaHora.hora,
            )
            .limit(3)
        ).all()

        last_positions = session.scalars(
            select(DiaHora)
            .order_by(
                DiaHora.dia.desc(),
                DiaHora.hora.desc(),
            )
            .limit(3)
        ).all()

        print()
        print("Catálogo Día-Hora:")
        print(f"  Cantidad: {count}")

        print("  Primeras posiciones:")

        for position in first_positions:
            print(
                f"    {position.descripcion}"
            )

        print("  Últimas posiciones:")

        for position in reversed(last_positions):
            print(
                f"    {position.descripcion}"
            )


def show_quotes_sample() -> None:
    with session_scope() as session:
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
                )
                .selectinload(
                    Zona.tarifas_por_canal
                )
                .selectinload(
                    TarifaZonaCanalSelectividad
                    .canal_selectividad
                ),
                selectinload(
                    EsquemaCotizacion.adicionales_camiones
                )
                .selectinload(
                    AdicionalCamiones.tarifas_por_zona
                )
                .selectinload(
                    TarifaAdicionalCamionesZona.zona
                ),
                selectinload(
                    EsquemaCotizacion
                    .tarifas_adicionales_dia_hora
                )
                .selectinload(
                    TarifaAdicionalDiaHora.dia_hora
                ),
            )
            .order_by(
                EsquemaCotizacion.fecha_inicio.desc(),
            )
            .limit(5)
        )

        quotes = session.scalars(
            statement
        ).all()

        print()
        print("Muestra de esquemas:")

        if not quotes:
            print("  No hay esquemas cargados.")
            return

        for quote in quotes:
            provider = quote.proveedor
            customs_office = provider.aduana

            print(
                f"  Esquema "
                f"{quote.esquema_cotizacion_id}"
            )

            print(
                f"    Proveedor: "
                f"{provider.razon_social}"
            )

            print(
                f"    Aduana: "
                f"{customs_office.codigo} - "
                f"{customs_office.nombre}"
            )

            print(
                f"    Estado: {quote.estado}"
            )

            print(
                f"    Moneda: {quote.moneda_codigo}"
            )

            print(
                f"    Zonas: {len(quote.zonas)}"
            )

            for zone in quote.zonas:
                print(
                    f"      Zona: {zone.nombre}"
                )

                for tariff in zone.tarifas_por_canal:
                    print(
                        "        "
                        f"{tariff.canal_selectividad.nombre}: "
                        f"{tariff.monto}"
                    )

            print(
                "    Tramos de camiones: "
                f"{len(quote.adicionales_camiones)}"
            )

            for additional in quote.adicionales_camiones:
                print(
                    "      "
                    f"{additional.descripcion_rango}"
                )

                for tariff in additional.tarifas_por_zona:
                    print(
                        "        "
                        f"{tariff.zona.nombre}: "
                        f"{tariff.monto} por camión"
                    )

            schedule_values = (
                quote.tarifas_adicionales_dia_hora
            )

            print(
                "    Tarifas día-hora: "
                f"{len(schedule_values)}"
            )

            print(
                "    Configuración horaria completa: "
                f"{quote.configuracion_horaria_completa}"
            )

            tariffs_with_surcharge = [
                tariff
                for tariff in schedule_values
                if tariff.tiene_adicional
            ]

            print(
                "    Horas con adicional: "
                f"{len(tariffs_with_surcharge)}"
            )

            for tariff in tariffs_with_surcharge[:10]:
                print(
                    "      "
                    f"{tariff.dia_hora.descripcion}: "
                    f"{tariff.monto}"
                )

            if len(tariffs_with_surcharge) > 10:
                print(
                    "      ..."
                )


def main() -> None:
    show_table_information()
    show_record_counts()
    show_channels()
    show_day_hour_information()
    show_quotes_sample()


if __name__ == "__main__":
    main()