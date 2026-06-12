# ============================================================
# AtmosMetrics — models/fato_qualidade_ar.py
# ORM: Tabela Fato de Qualidade do Ar (OpenWeatherMap)
# ============================================================

from sqlalchemy import (
    Column, BigInteger, Integer, SmallInteger, Numeric,
    TIMESTAMP, ForeignKey, func,
)
from sqlalchemy.orm import relationship
from app.database import Base


class FatoQualidadeAr(Base):
    """Cada registro representa uma medição de qualidade do ar para uma localidade."""
    __tablename__ = "fato_qualidade_ar"

    id_qualidade_ar = Column(BigInteger, primary_key=True, autoincrement=True)

    # Chaves Estrangeiras
    id_tempo        = Column(Integer, ForeignKey("dim_tempo.id_tempo"),         nullable=False)
    id_localidade   = Column(Integer, ForeignKey("dim_localidade.id_localidade"), nullable=False)

    # Índice de Qualidade do Ar (1-5 conforme OpenWeatherMap)
    aqi             = Column(SmallInteger)

    # Componentes da poluição atmosférica (µg/m³)
    co              = Column(Numeric(10, 2))   # Monóxido de carbono
    no              = Column(Numeric(10, 2))   # Óxido nítrico
    no2             = Column(Numeric(10, 2))   # Dióxido de nitrogênio
    o3              = Column(Numeric(10, 2))   # Ozônio
    so2             = Column(Numeric(10, 2))   # Dióxido de enxofre
    pm2_5           = Column(Numeric(10, 2))   # Partículas finas (PM2.5)
    pm10            = Column(Numeric(10, 2))   # Partículas grossas (PM10)
    nh3             = Column(Numeric(10, 2))   # Amônia

    # Auditoria
    criado_em       = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relacionamentos
    tempo           = relationship("DimTempo",      lazy="joined")
    localidade      = relationship("DimLocalidade",  lazy="joined")

    def __repr__(self) -> str:
        return f"<FatoQualidadeAr(id={self.id_qualidade_ar}, aqi={self.aqi})>"
