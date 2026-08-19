import pytest

from validacion_honorarios.services.aduana_service import (
    AduanaService,
)
from validacion_honorarios.services.exceptions import (
    ValidationError,
)


@pytest.fixture
def service() -> AduanaService:
    return AduanaService()


@pytest.mark.parametrize(
    ("codigo", "nombre"),
    [
        ("38", "MENDOZA"),
        ("0038", "MENDOZA"),
        ("ABC", "MENDOZA"),
        ("", "MENDOZA"),
        ("  ", "MENDOZA"),
        ("038", ""),
        ("038", "   "),
    ],
)
def test_crear_rechaza_datos_invalidos(
    service: AduanaService,
    codigo: str,
    nombre: str,
) -> None:
    with pytest.raises(ValidationError):
        service.crear(
            codigo=codigo,
            nombre=nombre,
        )


def test_normaliza_nombre() -> None:
    nombre = AduanaService._normalizar_nombre(
        "  buenos   aires  "
    )

    assert nombre == "BUENOS AIRES"


def test_normaliza_codigo() -> None:
    codigo = AduanaService._normalizar_codigo(
        " 038 "
    )

    assert codigo == "038"
