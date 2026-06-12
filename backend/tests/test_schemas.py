# ============================================================
# AtmosMetrics — tests/test_schemas.py
# Testes unitários para os schemas Pydantic da API
# ============================================================

import os
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")

from datetime import date
from decimal import Decimal

from app.schemas.clima import ClimaOut
from app.schemas.qualidade_ar import QualidadeArOut
from app.schemas.localidade import PaisOut


class TestClimaOutSchema:
    """Testes para o schema ClimaOut."""

    def test_clima_out_dados_validos(self):
        """ClimaOut deve aceitar dados válidos e serializar corretamente."""
        dados = {
            "id_clima": 1,
            "temperatura_media": Decimal("22.50"),
            "temperatura_max": Decimal("28.00"),
            "temperatura_min": Decimal("17.00"),
            "umidade_media": Decimal("65.00"),
            "precipitacao_mm": Decimal("5.20"),
            "velocidade_vento": Decimal("12.30"),
            "direcao_vento": 180,
            "pressao_hpa": Decimal("1013.25"),
            "radiacao_solar": Decimal("250.00"),
            "data_completa": date(2025, 6, 10),
            "municipio": "São Paulo",
            "pais": "Brasil",
            "continente": "América do Sul",
            "latitude": Decimal("-23.550520"),
            "longitude": Decimal("-46.633308"),
        }
        schema = ClimaOut(**dados)
        assert schema.id_clima == 1
        assert schema.temperatura_media == Decimal("22.50")
        assert schema.municipio == "São Paulo"
        assert schema.pais == "Brasil"

    def test_clima_out_campos_opcionais_nulos(self):
        """ClimaOut deve aceitar campos opcionais como None."""
        dados = {"id_clima": 2}
        schema = ClimaOut(**dados)
        assert schema.id_clima == 2
        assert schema.temperatura_media is None
        assert schema.municipio is None


class TestQualidadeArOutSchema:
    """Testes para o schema QualidadeArOut."""

    def test_qualidade_ar_out_dados_validos(self):
        """QualidadeArOut deve aceitar dados válidos."""
        dados = {
            "id_qualidade_ar": 1,
            "aqi": 2,
            "co": Decimal("201.94"),
            "no": Decimal("0.10"),
            "no2": Decimal("5.30"),
            "o3": Decimal("68.50"),
            "so2": Decimal("1.20"),
            "pm2_5": Decimal("12.40"),
            "pm10": Decimal("18.60"),
            "nh3": Decimal("3.10"),
            "data_completa": date(2025, 6, 10),
            "municipio": "São Paulo",
            "pais": "Brasil",
            "continente": "América do Sul",
        }
        schema = QualidadeArOut(**dados)
        assert schema.id_qualidade_ar == 1
        assert schema.aqi == 2
        assert schema.pm2_5 == Decimal("12.40")

    def test_qualidade_ar_out_campos_opcionais_nulos(self):
        """QualidadeArOut deve aceitar campos opcionais como None."""
        dados = {"id_qualidade_ar": 2}
        schema = QualidadeArOut(**dados)
        assert schema.aqi is None
        assert schema.co is None


class TestPaisOutSchema:
    """Testes para o schema PaisOut."""

    def test_pais_out_dados_validos(self):
        """PaisOut deve aceitar dados válidos de um país."""
        dados = {
            "pais": "Brasil",
            "continente": "América do Sul",
            "codigo_iso": "BRA",
        }
        schema = PaisOut(**dados)
        assert schema.pais == "Brasil"
        assert schema.continente == "América do Sul"
        assert schema.codigo_iso == "BRA"

    def test_pais_out_sem_iso(self):
        """PaisOut deve aceitar país sem código ISO."""
        dados = {"pais": "Desconhecido"}
        schema = PaisOut(**dados)
        assert schema.pais == "Desconhecido"
        assert schema.codigo_iso is None
        assert schema.continente is None
