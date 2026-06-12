from app.models.dim_tempo import DimTempo
from app.models.dim_satelite import DimSatelite
from app.models.dim_localidade import DimLocalidade
from app.models.fato_anomalia_termica import FatoAnomaliaTermica
from app.models.fato_qualidade_ar import FatoQualidadeAr
from app.models.fato_clima import FatoClima

__all__ = [
    "DimTempo", "DimSatelite", "DimLocalidade",
    "FatoAnomaliaTermica", "FatoQualidadeAr", "FatoClima",
]

