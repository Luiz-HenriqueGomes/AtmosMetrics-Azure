# ============================================================
# AtmosMetrics — schemas/qualidade_ar.py
# Pydantic: serialização de qualidade do ar para a API
# ============================================================

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class QualidadeArOut(BaseModel):
    """Resposta de uma medição de qualidade do ar com dados das dimensões."""

    model_config = ConfigDict(from_attributes=True)

    id_qualidade_ar: int
    aqi:             Optional[int]     = None
    co:              Optional[Decimal] = None
    no:              Optional[Decimal] = None
    no2:             Optional[Decimal] = None
    o3:              Optional[Decimal] = None
    so2:             Optional[Decimal] = None
    pm2_5:           Optional[Decimal] = None
    pm10:            Optional[Decimal] = None
    nh3:             Optional[Decimal] = None

    # Dados das dimensões (preenchidos pela query com JOIN)
    data_completa:   Optional[date]    = None
    municipio:       Optional[str]     = None
    pais:            Optional[str]     = None
    continente:      Optional[str]     = None
    latitude:        Optional[Decimal] = None
    longitude:       Optional[Decimal] = None


class ResumoQualidadeArOut(BaseModel):
    """Resumo agregado de qualidade do ar para o dashboard."""

    aqi_medio:       Optional[float]   = None
    pm25_medio:      Optional[float]   = None
    pm10_medio:      Optional[float]   = None
    co_medio:        Optional[float]   = None
    no2_medio:       Optional[float]   = None
    o3_medio:        Optional[float]   = None
    so2_medio:       Optional[float]   = None
    total_medicoes:  int               = 0
    data_inicio:     Optional[date]    = None
    data_fim:        Optional[date]    = None
