# ============================================================
# AtmosMetrics — schemas/localidade.py
# Pydantic: serialização de localidades para a API
# Expandido para suporte global (país, continente, etc.)
# ============================================================

from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional


class LocalidadeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_localidade: int
    municipio:     str
    codigo_ibge:   str | None = None
    uf:            Optional[str] = None
    estado:        Optional[str] = None
    regiao:        Optional[str] = None
    bioma:         Optional[str] = None

    # Campos globais
    pais:          Optional[str]     = None
    continente:    Optional[str]     = None
    latitude_ref:  Optional[Decimal] = None
    longitude_ref: Optional[Decimal] = None
    codigo_iso:    Optional[str]     = None


class EstadoOut(BaseModel):
    """Lista simplificada de estados para filtros no frontend."""
    uf:    str
    estado: str
    regiao: str


class BiomaOut(BaseModel):
    """Lista de biomas únicos para filtros no frontend."""
    bioma: str


class PaisOut(BaseModel):
    """Lista de países para filtros globais no frontend."""
    pais:       str
    continente: Optional[str] = None
    codigo_iso: Optional[str] = None


class ContinenteOut(BaseModel):
    """Lista de continentes para filtros globais no frontend."""
    continente: str

