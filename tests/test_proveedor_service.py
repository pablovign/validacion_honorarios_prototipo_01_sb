import pytest

from validacion_honorarios.services.exceptions import (
    ValidationError,
)
from validacion_honorarios.services.proveedor_service import (
    ProveedorService,
)


@pytest.fixture
def service() -> ProveedorService:
    return ProveedorService()


@pytest.mark.parametrize(
    "cuit",
    [
        "",
        " ",
        "123",
        "3012345678",
        "301234567890",
        "30-1234567-A",
        "ABCDEFGHIJK",
    ],
)
def test_normalizar_cuit_rechaza_valores_invalidos(
    service: ProveedorService,
    cuit: str,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_cuit(
            cuit
        )


@pytest.mark.parametrize(
    (
        "entrada",
        "resultado",
    ),
    [
        (
            "30123456789",
            "30123456789",
        ),
        (
            "30-12345678-9",
            "30123456789",
        ),
        (
            " 30 12345678 9 ",
            "30123456789",
        ),
    ],
)
def test_normalizar_cuit_acepta_formatos_validos(
    service: ProveedorService,
    entrada: str,
    resultado: str,
) -> None:
    assert (
        service._normalizar_cuit(
            entrada
        )
        == resultado
    )


def test_normalizar_razon_social() -> None:
    resultado = (
        ProveedorService
        ._normalizar_razon_social(
            "  Proveedor   de prueba  SRL  "
        )
    )

    assert (
        resultado
        == "Proveedor de prueba SRL"
    )


@pytest.mark.parametrize(
    "razon_social",
    [
        "",
        " ",
        "    ",
    ],
)
def test_rechaza_razon_social_vacia(
    service: ProveedorService,
    razon_social: str,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_razon_social(
            razon_social
        )


@pytest.mark.parametrize(
    "identificador",
    [
        0,
        -1,
        True,
        False,
    ],
)
def test_rechaza_identificadores_invalidos(
    service: ProveedorService,
    identificador: int,
) -> None:
    with pytest.raises(ValidationError):
        service._validar_id_positivo(
            identificador,
            "proveedor",
        )