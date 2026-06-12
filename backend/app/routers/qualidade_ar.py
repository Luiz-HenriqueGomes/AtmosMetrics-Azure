# ============================================================
# AtmosMetrics — routers/qualidade_ar.py
# Endpoints: /api/v1/qualidade-ar
# Dados de qualidade do ar globais (OpenWeatherMap)
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import date
from typing import Optional

from app.database import get_db
from app.models import FatoQualidadeAr, DimTempo, DimLocalidade
from app.schemas.qualidade_ar import QualidadeArOut, ResumoQualidadeArOut

router = APIRouter(prefix="/api/v1/qualidade-ar", tags=["Qualidade do Ar"])


# ---- Helpers ---------------------------------------------------------------

def _base_query(db: Session):
    """Query base com JOINs das dimensões."""
    return (
        db.query(
            FatoQualidadeAr.id_qualidade_ar,
            FatoQualidadeAr.aqi,
            FatoQualidadeAr.co,
            FatoQualidadeAr.no,
            FatoQualidadeAr.no2,
            FatoQualidadeAr.o3,
            FatoQualidadeAr.so2,
            FatoQualidadeAr.pm2_5,
            FatoQualidadeAr.pm10,
            FatoQualidadeAr.nh3,
            DimTempo.data_completa,
            DimLocalidade.municipio,
            DimLocalidade.pais,
            DimLocalidade.continente,
            DimLocalidade.latitude_ref.label("latitude"),
            DimLocalidade.longitude_ref.label("longitude"),
        )
        .join(DimTempo,      FatoQualidadeAr.id_tempo      == DimTempo.id_tempo)
        .join(DimLocalidade, FatoQualidadeAr.id_localidade == DimLocalidade.id_localidade)
    )


def _apply_filters(query, data_inicio, data_fim, pais, continente):
    """Aplica os filtros opcionais à query."""
    if data_inicio:
        query = query.filter(DimTempo.data_completa >= data_inicio)
    if data_fim:
        query = query.filter(DimTempo.data_completa <= data_fim)
    if pais:
        query = query.filter(DimLocalidade.pais.ilike(f"%{pais}%"))
    if continente:
        query = query.filter(DimLocalidade.continente.ilike(f"%{continente}%"))
    return query


def _build_filters(data_inicio, data_fim, pais, continente):
    """Retorna lista de expressões de filtro para .filter(*filters)."""
    filters = []
    if data_inicio:
        filters.append(DimTempo.data_completa >= data_inicio)
    if data_fim:
        filters.append(DimTempo.data_completa <= data_fim)
    if pais:
        filters.append(DimLocalidade.pais.ilike(f"%{pais}%"))
    if continente:
        filters.append(DimLocalidade.continente.ilike(f"%{continente}%"))
    return filters if filters else [text("1=1")]


# ---- Endpoints -------------------------------------------------------------

@router.get("/", response_model=list[QualidadeArOut], summary="Listar qualidade do ar")
def listar_qualidade_ar(
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim:    Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    pais:        Optional[str]  = Query(None, description="Filtrar por país"),
    continente:  Optional[str]  = Query(None, description="Filtrar por continente"),
    limit:       int            = Query(100, ge=1, le=1000, description="Máx. de registros"),
    offset:      int            = Query(0, ge=0, description="Paginação: início"),
    db: Session = Depends(get_db),
):
    """
    Retorna uma lista paginada de medições de qualidade do ar com dados das dimensões.
    Filtre por período, país ou continente.
    """
    query = _base_query(db)
    query = _apply_filters(query, data_inicio, data_fim, pais, continente)
    rows = query.order_by(DimTempo.data_completa.desc()).offset(offset).limit(limit).all()
    return [QualidadeArOut(
        id_qualidade_ar=r.id_qualidade_ar,
        aqi=r.aqi,
        co=r.co,
        no=r.no,
        no2=r.no2,
        o3=r.o3,
        so2=r.so2,
        pm2_5=r.pm2_5,
        pm10=r.pm10,
        nh3=r.nh3,
        data_completa=r.data_completa,
        municipio=r.municipio,
        pais=r.pais,
        continente=r.continente,
        latitude=r.latitude,
        longitude=r.longitude,
    ) for r in rows]


@router.get("/resumo", response_model=ResumoQualidadeArOut, summary="Resumo qualidade do ar")
def resumo_qualidade_ar(
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim:    Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    pais:        Optional[str]  = Query(None, description="Filtrar por país"),
    continente:  Optional[str]  = Query(None, description="Filtrar por continente"),
    db: Session = Depends(get_db),
):
    """
    Retorna métricas agregadas de qualidade do ar para o dashboard:
    AQI médio, PM2.5, PM10, CO, NO2, O3, SO2 médios.
    """
    base = (
        db.query(FatoQualidadeAr)
        .join(DimTempo,      FatoQualidadeAr.id_tempo      == DimTempo.id_tempo)
        .join(DimLocalidade, FatoQualidadeAr.id_localidade == DimLocalidade.id_localidade)
    )

    filters = _build_filters(data_inicio, data_fim, pais, continente)
    base = base.filter(*filters)

    total = base.count()
    agg = base.with_entities(
        func.avg(FatoQualidadeAr.aqi).label("aqi_medio"),
        func.avg(FatoQualidadeAr.pm2_5).label("pm25_medio"),
        func.avg(FatoQualidadeAr.pm10).label("pm10_medio"),
        func.avg(FatoQualidadeAr.co).label("co_medio"),
        func.avg(FatoQualidadeAr.no2).label("no2_medio"),
        func.avg(FatoQualidadeAr.o3).label("o3_medio"),
        func.avg(FatoQualidadeAr.so2).label("so2_medio"),
        func.min(DimTempo.data_completa).label("data_inicio"),
        func.max(DimTempo.data_completa).label("data_fim"),
    ).first()

    return ResumoQualidadeArOut(
        aqi_medio=float(agg.aqi_medio) if agg and agg.aqi_medio else None,
        pm25_medio=float(agg.pm25_medio) if agg and agg.pm25_medio else None,
        pm10_medio=float(agg.pm10_medio) if agg and agg.pm10_medio else None,
        co_medio=float(agg.co_medio) if agg and agg.co_medio else None,
        no2_medio=float(agg.no2_medio) if agg and agg.no2_medio else None,
        o3_medio=float(agg.o3_medio) if agg and agg.o3_medio else None,
        so2_medio=float(agg.so2_medio) if agg and agg.so2_medio else None,
        total_medicoes=total,
        data_inicio=agg.data_inicio if agg else None,
        data_fim=agg.data_fim if agg else None,
    )
