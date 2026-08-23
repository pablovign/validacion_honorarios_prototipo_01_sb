from datetime import date

import pytest

from validacion_honorarios.services.esquema_cotizacion_service import (
    EsquemaCotizacionService,
)
from validacion_honorarios.services.exceptions import (
    BusinessRuleError,
    ValidationError,
)


@pytest.fixture
def service() -> EsquemaCotizacionService:
    return EsquemaCotizacionService()


@pytest.mark.parametrize(
    (
        "entrada",
        "resultado",
    ),
    [
        (
            "01/08/2026",
            date(2026, 8, 1),
        ),
        (
            "2026-08-01",
            date(2026, 8, 1),
        ),
        (
            date(2026, 8, 1),
            date(2026, 8, 1),
        ),
    ],
)
def test_normalizar_fecha_valida(
    service: EsquemaCotizacionService,
    entrada,
    resultado: date,
) -> None:
    assert (
        service._normalizar_fecha(
            entrada
        )
        == resultado
    )


@pytest.mark.parametrize(
    "fecha",
    [
        "",
        " ",
        "32/08/2026",
        "2026/08/01",
        "01-08-2026",
        "texto",
    ],
)
def test_rechaza_fecha_invalida(
    service: EsquemaCotizacionService,
    fecha: str,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_fecha(
            fecha
        )


@pytest.mark.parametrize(
    (
        "entrada",
        "resultado",
    ),
    [
        ("ars", "ARS"),
        (" ARS ", "ARS"),
        ("usd", "USD"),
        (" USD ", "USD"),
    ],
)
def test_normalizar_moneda_valida(
    service: EsquemaCotizacionService,
    entrada: str,
    resultado: str,
) -> None:
    assert (
        service._normalizar_moneda(
            entrada
        )
        == resultado
    )


@pytest.mark.parametrize(
    "moneda",
    [
        "",
        "EUR",
        "AAA",
        "PESOS",
    ],
)
def test_rechaza_moneda_invalida(
    service: EsquemaCotizacionService,
    moneda: str,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_moneda(
            moneda
        )


@pytest.mark.parametrize(
    (
        "entrada",
        "resultado",
    ),
    [
        ("borrador", "BORRADOR"),
        (" APROBADO ", "APROBADO"),
        ("rechazado", "RECHAZADO"),
    ],
)
def test_normalizar_estado_valido(
    service: EsquemaCotizacionService,
    entrada: str,
    resultado: str,
) -> None:
    assert (
        service._normalizar_estado(
            entrada
        )
        == resultado
    )


def test_rechaza_estado_invalido(
    service: EsquemaCotizacionService,
) -> None:
    with pytest.raises(ValidationError):
        service._normalizar_estado(
            "PENDIENTE"
        )


def test_normalizar_observaciones_vacias() -> None:
    assert (
        EsquemaCotizacionService
        ._normalizar_observaciones(
            "   "
        )
        is None
    )


def test_normalizar_observaciones() -> None:
    resultado = (
        EsquemaCotizacionService
        ._normalizar_observaciones(
            "  Documento recibido por correo.  "
        )
    )

    assert (
        resultado
        == "Documento recibido por correo."
    )


class EsquemaFalso:
    estado = "APROBADO"


def test_impide_editar_esquema_no_borrador() -> None:
    with pytest.raises(BusinessRuleError):
        EsquemaCotizacionService._validar_editable(
            EsquemaFalso()
        )

class EsquemaAprobableFalso:
    estado = "BORRADOR"
    zonas = [object()]
    tarifas_adicionales_dia_hora = []


class EsquemaSinZonasFalso:
    estado = "BORRADOR"
    zonas = []
    tarifas_adicionales_dia_hora = []


class EsquemaHorarioIncompletoFalso:
    estado = "BORRADOR"
    zonas = [object()]
    tarifas_adicionales_dia_hora = [object()]


def test_permite_aprobar_integridad_minima() -> None:
    EsquemaCotizacionService._validar_aprobable(
        EsquemaAprobableFalso()
    )


def test_impide_aprobar_sin_zonas() -> None:
    with pytest.raises(BusinessRuleError):
        EsquemaCotizacionService._validar_aprobable(
            EsquemaSinZonasFalso()
        )


def test_impide_aprobar_configuracion_horaria_incompleta() -> None:
    with pytest.raises(BusinessRuleError):
        EsquemaCotizacionService._validar_aprobable(
            EsquemaHorarioIncompletoFalso()
        )
