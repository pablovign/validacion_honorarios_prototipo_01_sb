from decimal import Decimal

import pytest

from validacion_honorarios.services.exceptions import (
    BusinessRuleError,
    ValidationError,
)
from validacion_honorarios.services.tarifa_dia_hora_service import (
    TarifaDiaHoraService,
)


@pytest.mark.parametrize(
    (
        "entrada",
        "resultado",
    ),
    [
        (
            [1],
            [1],
        ),
        (
            [1, 2, 3],
            [1, 2, 3],
        ),
        (
            [1, 1, 2],
            [1, 2],
        ),
        (
            (1, 2),
            [1, 2],
        ),
        (
            {1, 2},
            [1, 2],
        ),
    ],
)
def test_normalizar_ids_posiciones(
    entrada,
    resultado: list[int],
) -> None:
    normalizados = (
        TarifaDiaHoraService
        ._normalizar_ids_posiciones(
            entrada
        )
    )

    assert sorted(normalizados) == sorted(
        resultado
    )


@pytest.mark.parametrize(
    "entrada",
    [
        [],
        (),
        set(),
        "1,2,3",
        None,
    ],
)
def test_rechaza_coleccion_vacia_o_invalida(
    entrada,
) -> None:
    with pytest.raises(ValidationError):
        (
            TarifaDiaHoraService
            ._normalizar_ids_posiciones(
                entrada
            )
        )


@pytest.mark.parametrize(
    "entrada",
    [
        [0],
        [-1],
        [True],
        ["1"],
    ],
)
def test_rechaza_ids_invalidos(
    entrada,
) -> None:
    with pytest.raises(ValidationError):
        (
            TarifaDiaHoraService
            ._normalizar_ids_posiciones(
                entrada
            )
        )


def test_rechaza_esquema_no_editable() -> None:
    with pytest.raises(BusinessRuleError):
        (
            TarifaDiaHoraService
            ._validar_esquema_editable(
                "APROBADO"
            )
        )


def test_constante_cantidad_posiciones() -> None:
    assert (
        TarifaDiaHoraService
        .CANTIDAD_POSICIONES
        == 168
    )


def test_monto_cero_es_decimal() -> None:
    monto = Decimal("0.00")

    assert monto == Decimal("0.00")