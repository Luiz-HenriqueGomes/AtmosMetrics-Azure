# ============================================================
# AtmosMetrics — tests/test_helpers.py
# Testes unitários para funções auxiliares dos módulos ETL
# ============================================================

import os, sys, math
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")

# Importa as funções auxiliares dos módulos ETL
from etl.loader import _safe_float, _safe_int
from etl.nasa_firms_etl import _estimar_continente


class TestSafeFloat:
    """Testes para a função _safe_float do loader."""

    def test_safe_float_valor_valido(self):
        """Valor numérico válido deve retornar float."""
        assert _safe_float(3.14) == 3.14
        assert _safe_float(42) == 42.0
        assert _safe_float("7.5") == 7.5

    def test_safe_float_none(self):
        """None deve retornar None."""
        assert _safe_float(None) is None

    def test_safe_float_nan(self):
        """NaN deve retornar None (tratamento especial)."""
        assert _safe_float(float("nan")) is None

    def test_safe_float_string_invalida(self):
        """String não numérica deve retornar None."""
        assert _safe_float("abc") is None
        assert _safe_float("") is None


class TestSafeInt:
    """Testes para a função _safe_int do loader."""

    def test_safe_int_valor_valido(self):
        """Valor numérico válido deve retornar int."""
        assert _safe_int(42) == 42
        assert _safe_int(3.7) == 3    # trunca para int
        assert _safe_int("10") == 10

    def test_safe_int_none(self):
        """None deve retornar None."""
        assert _safe_int(None) is None

    def test_safe_int_string_invalida(self):
        """String não numérica deve retornar None."""
        assert _safe_int("abc") is None


class TestEstimarContinente:
    """Testes para a função _estimar_continente do nasa_firms_etl."""

    def test_estimar_continente_brasil(self):
        """Coordenadas de São Paulo devem retornar América do Sul."""
        resultado = _estimar_continente(-23.55, -46.63)
        assert resultado == "América do Sul"

    def test_estimar_continente_europa(self):
        """Coordenadas de Paris devem retornar Europa."""
        resultado = _estimar_continente(48.86, 2.35)
        assert resultado == "Europa"

    def test_estimar_continente_asia(self):
        """Coordenadas de Tóquio devem retornar Ásia."""
        resultado = _estimar_continente(35.68, 139.69)
        assert resultado == "Ásia"

    def test_estimar_continente_africa(self):
        """Coordenadas de Nairobi devem retornar África."""
        resultado = _estimar_continente(-1.29, 36.82)
        assert resultado == "África"

    def test_estimar_continente_america_norte(self):
        """Coordenadas de Nova York devem retornar América do Norte."""
        resultado = _estimar_continente(40.71, -74.01)
        assert resultado == "América do Norte"
