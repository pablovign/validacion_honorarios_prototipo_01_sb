from decimal import Decimal

import pytest

from validacion_honorarios.services.exceptions import (
    BusinessRuleError,
    ValidationError,
)
from validacion_honorarios.services.zona_tarifa_service import (
    ZonaTarifaService,
)


@pytest.fixture
def service() -> ZonaTarifaService:
    return ZonaTarifaService()


@pytest.mark.parametrize(
    (
        "entrada",
        "resultado",
    ),
    [
        (
            "38000",
            Decimal("38000.00"),
        ),
        (
            "38000.50",
            Decimal("38000.50"),
        ),
        (
            "38000,50",
            Decimal("38000.50"),
        ),
        (
            "38.000,50",
            Decimal("38000.50"),
        ),
        (
            38000,
            Decimal("38000.00"),
        ),
        (
            Decimal("38000.10"),
            Decimal("38000.10"),
        ),
    ],
)
def test_normalizar_monto_valido(
    service: ZonaTarifaService,
    entrada,
    resultado: Decimal,
) -> None:
    assert (
        service._normalizar_monto(
            entrada
        )
        == resultado
    )


@pytest.mark.parametrize(
    "monto",
    [
        "",
        " ",
        "texto",
        "-1",
        -10,
        "NaN",
        "Infinity",
    ],
)
def test_rechaza_monto_invalido(
    service: ZonaTarifaService,
    monto,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_monto(
            monto
        )


def test_normalizar_nombre_zona() -> None:
    resultado = (
        ZonaTarifaService
        ._normalizar_nombre_zona(
            "  Zona   Norte  "
        )
    )

    assert resultado == "Zona Norte"


@pytest.mark.parametrize(
    "nombre",
    [
        "",
        " ",
        "    ",
    ],
)
def test_rechaza_nombre_zona_vacio(
    service: ZonaTarifaService,
    nombre: str,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_nombre_zona(
            nombre
        )


def test_rechaza_esquema_no_editable() -> None:
    with pytest.raises(BusinessRuleError):
        ZonaTarifaService._validar_esquema_editable(
            "APROBADO"
        )