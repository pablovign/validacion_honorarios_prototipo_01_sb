import pytest

from validacion_honorarios.services.canal_selectividad_service import (
    CanalSelectividadService,
)
from validacion_honorarios.services.exceptions import (
    ValidationError,
)


@pytest.fixture
def service() -> CanalSelectividadService:
    return CanalSelectividadService()


@pytest.mark.parametrize(
    "nombre",
    [
        "",
        " ",
        "    ",
    ],
)
def test_rechaza_nombre_vacio(
    service: CanalSelectividadService,
    nombre: str,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_nombre(
            nombre
        )


def test_normaliza_nombre() -> None:
    resultado = (
        CanalSelectividadService
        ._normalizar_nombre(
            "  canal   especial  "
        )
    )

    assert resultado == "CANAL ESPECIAL"


def test_rechaza_nombre_demasiado_largo(
    service: CanalSelectividadService,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_nombre(
            "A" * 51
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
def test_rechaza_identificador_invalido(
    service: CanalSelectividadService,
    identificador: int,
) -> None:
    with pytest.raises(ValidationError):
        service._validar_id(
            identificador
        )