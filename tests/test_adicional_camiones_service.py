import pytest

from validacion_honorarios.services.adicional_camiones_service import (
    AdicionalCamionesService,
)
from validacion_honorarios.services.exceptions import (
    ConflictError,
    ValidationError,
)


class TramoFalso:
    def __init__(
        self,
        identificador: int,
        desde: int,
        hasta: int | None,
    ) -> None:
        self.adicional_camiones_id = identificador
        self.camion_desde = desde
        self.camion_hasta = hasta

    @property
    def descripcion_rango(self) -> str:
        return (
            AdicionalCamionesService
            ._generar_nombre(
                self.camion_desde,
                self.camion_hasta,
            )
        )


@pytest.mark.parametrize(
    (
        "desde",
        "hasta",
        "esperado",
    ),
    [
        (
            2,
            5,
            "Camiones 2 a 5",
        ),
        (
            6,
            None,
            "Desde el camión 6",
        ),
        (
            3,
            3,
            "Camión 3",
        ),
    ],
)
def test_generar_nombre(
    desde: int,
    hasta: int | None,
    esperado: str,
) -> None:
    assert (
        AdicionalCamionesService
        ._generar_nombre(
            desde,
            hasta,
        )
        == esperado
    )


@pytest.mark.parametrize(
    "valor",
    [
        "",
        "texto",
        0,
        -1,
        True,
    ],
)
def test_rechaza_numero_camion_invalido(
    valor,
) -> None:
    with pytest.raises(ValidationError):
        AdicionalCamionesService._normalizar_camion(
            valor,
            "Camión desde",
        )


def test_camion_hasta_vacio_es_nulo() -> None:
    assert (
        AdicionalCamionesService
        ._normalizar_camion_hasta("")
        is None
    )


def test_rechaza_limites_invertidos() -> None:
    with pytest.raises(ValidationError):
        AdicionalCamionesService._validar_limites(
            6,
            5,
        )


@pytest.mark.parametrize(
    (
        "desde_a",
        "hasta_a",
        "desde_b",
        "hasta_b",
        "esperado",
    ),
    [
        (
            2,
            5,
            6,
            None,
            False,
        ),
        (
            2,
            5,
            5,
            8,
            True,
        ),
        (
            6,
            None,
            10,
            12,
            True,
        ),
        (
            2,
            3,
            4,
            5,
            False,
        ),
    ],
)
def test_detectar_solapamientos(
    desde_a: int,
    hasta_a: int | None,
    desde_b: int,
    hasta_b: int | None,
    esperado: bool,
) -> None:
    assert (
        AdicionalCamionesService
        ._intervalos_se_superponen(
            desde_a,
            hasta_a,
            desde_b,
            hasta_b,
        )
        is esperado
    )


def test_rechaza_solapamiento() -> None:
    tramos = [
        TramoFalso(
            1,
            2,
            5,
        )
    ]

    with pytest.raises(ConflictError):
        AdicionalCamionesService._validar_no_solapamiento(
            camion_desde=5,
            camion_hasta=8,
            tramos_existentes=tramos,
        )


def test_permite_tramo_contiguo() -> None:
    tramos = [
        TramoFalso(
            1,
            2,
            5,
        )
    ]

    AdicionalCamionesService._validar_no_solapamiento(
        camion_desde=6,
        camion_hasta=None,
        tramos_existentes=tramos,
    )