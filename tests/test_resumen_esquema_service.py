from decimal import Decimal

from validacion_honorarios.services.resumen_esquema_service import (
    ResumenEsquemaService,
)


class PosicionFalsa:
    def __init__(
        self,
        dia: int,
        nombre_dia: str,
        hora: int,
    ) -> None:
        self.dia = dia
        self.nombre_dia = nombre_dia
        self.hora = hora


class TarifaFalsa:
    def __init__(
        self,
        dia: int,
        nombre_dia: str,
        hora: int,
        monto: str,
    ) -> None:
        self.dia_hora = PosicionFalsa(
            dia,
            nombre_dia,
            hora,
        )
        self.monto = Decimal(monto)


def test_agrupa_horas_contiguas_con_mismo_monto() -> None:
    tarifas = [
        TarifaFalsa(1, "Lunes", 8, "200.00"),
        TarifaFalsa(1, "Lunes", 9, "200.00"),
        TarifaFalsa(1, "Lunes", 10, "300.00"),
    ]

    bloques = ResumenEsquemaService.agrupar_bloques_horarios(
        tarifas
    )

    assert bloques == [
        {
            "dia": 1,
            "nombre_dia": "Lunes",
            "hora_desde": 8,
            "hora_hasta": 10,
            "monto": Decimal("200.00"),
        },
        {
            "dia": 1,
            "nombre_dia": "Lunes",
            "hora_desde": 10,
            "hora_hasta": 11,
            "monto": Decimal("300.00"),
        },
    ]


def test_no_agrupa_dias_distintos() -> None:
    tarifas = [
        TarifaFalsa(1, "Lunes", 23, "500.00"),
        TarifaFalsa(2, "Martes", 0, "500.00"),
    ]

    bloques = ResumenEsquemaService.agrupar_bloques_horarios(
        tarifas
    )

    assert len(bloques) == 2


def test_omite_importes_en_cero() -> None:
    tarifas = [
        TarifaFalsa(1, "Lunes", 8, "0.00"),
        TarifaFalsa(1, "Lunes", 9, "200.00"),
    ]

    bloques = ResumenEsquemaService.agrupar_bloques_horarios(
        tarifas
    )

    assert len(bloques) == 1
    assert bloques[0]["hora_desde"] == 9
