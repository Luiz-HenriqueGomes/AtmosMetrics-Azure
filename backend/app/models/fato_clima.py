# ============================================================
# AtmosMetrics — models/fato_clima.py
# ORM: Tabela Fato de Dados Climáticos (Open-Meteo)
# ============================================================

from sqlalchemy import (
    Column, BigInteger, Integer, SmallInteger, Numeric,
    TIMESTAMP, ForeignKey, func,
)
from sqlalchemy.orm import relationship
from app.database import Base


class FatoClima(Base):
    """Cada registro representa dados climáticos diários de uma localidade."""
    __tablename__ = "fato_clima"

    id_clima        = Column(BigInteger, primary_key=True, autoincrement=True)

    # Chaves Estrangeiras
    id_tempo        = Column(Integer, ForeignKey("dim_tempo.id_tempo"),         nullable=False)
    id_localidade   = Column(Integer, ForeignKey("dim_localidade.id_localidade"), nullable=False)

    # Métricas climáticas
    temperatura_media   = Column(Numeric(5, 2))   # °C
    temperatura_max     = Column(Numeric(5, 2))   # °C
    temperatura_min     = Column(Numeric(5, 2))   # °C
    umidade_media       = Column(Numeric(5, 2))   # %
    precipitacao_mm     = Column(Numeric(7, 2))   # mm
    velocidade_vento    = Column(Numeric(6, 2))   # km/h
    direcao_vento       = Column(SmallInteger)     # graus (0-360)
    pressao_hpa         = Column(Numeric(7, 2))   # hPa
    radiacao_solar      = Column(Numeric(8, 2))   # W/m²

    # Auditoria
    criado_em           = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relacionamentos
    tempo               = relationship("DimTempo",      lazy="joined")
    localidade          = relationship("DimLocalidade",  lazy="joined")

    def __repr__(self) -> str:
        return f"<FatoClima(id={self.id_clima}, temp_media={self.temperatura_media})>"
