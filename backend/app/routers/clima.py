# ============================================================
# AtmosMetrics — routers/clima.py
# Endpoints: /api/v1/clima
# Dados climáticos globais (Open-Meteo)
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import date
from typing import Optional

from app.database import get_db
from app.models import FatoClima, DimTempo, DimLocalidade
from app.schemas.clima import ClimaOut, ResumoClimaOut

router = APIRouter(prefix="/api/v1/clima", tags=["Clima"])


# ---- Helpers ---------------------------------------------------------------

def _base_query(db: Session):
    """Query base com JOINs das dimensões."""
    return (
        db.query(
            FatoClima.id_clima,
            FatoClima.temperatura_media,
            FatoClima.temperatura_max,
            FatoClima.temperatura_min,
            FatoClima.umidade_media,
            FatoClima.precipitacao_mm,
            FatoClima.velocidade_vento,
            FatoClima.direcao_vento,
            FatoClima.pressao_hpa,
            FatoClima.radiacao_solar,
            DimTempo.data_completa,
            DimLocalidade.municipio,
            DimLocalidade.pais,
            DimLocalidade.continente,
            DimLocalidade.latitude_ref.label("latitude"),
            DimLocalidade.longitude_ref.label("longitude"),
        )
        .join(DimTempo,      FatoClima.id_tempo      == DimTempo.id_tempo)
        .join(DimLocalidade, FatoClima.id_localidade == DimLocalidade.id_localidade)
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

@router.get("/", response_model=list[ClimaOut], summary="Listar dados climáticos")
def listar_clima(
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim:    Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    pais:        Optional[str]  = Query(None, description="Filtrar por país"),
    continente:  Optional[str]  = Query(None, description="Filtrar por continente"),
    limit:       int            = Query(100, ge=1, le=1000, description="Máx. de registros"),
    offset:      int            = Query(0, ge=0, description="Paginação: início"),
    db: Session = Depends(get_db),
):
    """
    Retorna uma lista paginada de dados climáticos com dados das dimensões.
    Filtre por período, país ou continente.
    """
    query = _base_query(db)
    query = _apply_filters(query, data_inicio, data_fim, pais, continente)
    rows = query.order_by(DimTempo.data_completa.desc()).offset(offset).limit(limit).all()
    return [ClimaOut(
        id_clima=r.id_clima,
        temperatura_media=r.temperatura_media,
        temperatura_max=r.temperatura_max,
        temperatura_min=r.temperatura_min,
        umidade_media=r.umidade_media,
        precipitacao_mm=r.precipitacao_mm,
        velocidade_vento=r.velocidade_vento,
        direcao_vento=r.direcao_vento,
        pressao_hpa=r.pressao_hpa,
        radiacao_solar=r.radiacao_solar,
        data_completa=r.data_completa,
        municipio=r.municipio,
        pais=r.pais,
        continente=r.continente,
        latitude=r.latitude,
        longitude=r.longitude,
    ) for r in rows]


@router.get("/resumo", response_model=ResumoClimaOut, summary="Resumo climático global")
def resumo_clima(
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim:    Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    pais:        Optional[str]  = Query(None, description="Filtrar por país"),
    continente:  Optional[str]  = Query(None, description="Filtrar por continente"),
    db: Session = Depends(get_db),
):
    """
    Retorna métricas agregadas de clima para os cards do dashboard:
    temperatura média global, máxima, mínima, umidade, precipitação.
    """
    base = (
        db.query(FatoClima)
        .join(DimTempo,      FatoClima.id_tempo      == DimTempo.id_tempo)
        .join(DimLocalidade, FatoClima.id_localidade == DimLocalidade.id_localidade)
    )

    filters = _build_filters(data_inicio, data_fim, pais, continente)
    base = base.filter(*filters)

    total = base.count()
    agg = base.with_entities(
        func.avg(FatoClima.temperatura_media).label("temp_media"),
        func.max(FatoClima.temperatura_max).label("temp_max"),
        func.min(FatoClima.temperatura_min).label("temp_min"),
        func.avg(FatoClima.umidade_media).label("umidade_media"),
        func.avg(FatoClima.precipitacao_mm).label("precipitacao_media"),
        func.avg(FatoClima.velocidade_vento).label("vento_medio"),
        func.min(DimTempo.data_completa).label("data_inicio"),
        func.max(DimTempo.data_completa).label("data_fim"),
    ).first()

    return ResumoClimaOut(
        temp_media_global=float(agg.temp_media) if agg and agg.temp_media else None,
        temp_max_global=float(agg.temp_max) if agg and agg.temp_max else None,
        temp_min_global=float(agg.temp_min) if agg and agg.temp_min else None,
        umidade_media=float(agg.umidade_media) if agg and agg.umidade_media else None,
        precipitacao_media=float(agg.precipitacao_media) if agg and agg.precipitacao_media else None,
        vento_medio=float(agg.vento_medio) if agg and agg.vento_medio else None,
        total_registros=total,
        data_inicio=agg.data_inicio if agg else None,
        data_fim=agg.data_fim if agg else None,
    )


@router.get("/extremas", response_model=list[ClimaOut], summary="Listar Temperaturas Extremas")
def listar_extremas(
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim:    Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    pais:        Optional[str]  = Query(None, description="Filtrar por país"),
    continente:  Optional[str]  = Query(None, description="Filtrar por continente"),
    limit:       int            = Query(100, ge=1, le=1000, description="Máx. de registros"),
    offset:      int            = Query(0, ge=0, description="Paginação: início"),
    db: Session = Depends(get_db),
):
    """
    Retorna todos os registros climáticos ordenados por extremidade:
    temperaturas mais distantes de 20°C aparecem primeiro.
    """
    query = _base_query(db)
    query = _apply_filters(query, data_inicio, data_fim, pais, continente)
    
    # Ordena por extremidade (distância da temperatura média em relação a 20°C)
    # Ex: 40°C = abs(20) = 20 de distância. -10°C = abs(-30) = 30 de distância.
    query = query.order_by(
        func.abs(FatoClima.temperatura_media - 20).desc(),
        DimTempo.data_completa.desc()
    )
    
    rows = query.offset(offset).limit(limit).all()
    return [ClimaOut(
        id_clima=r.id_clima,
        temperatura_media=r.temperatura_media,
        temperatura_max=r.temperatura_max,
        temperatura_min=r.temperatura_min,
        umidade_media=r.umidade_media,
        precipitacao_mm=r.precipitacao_mm,
        velocidade_vento=r.velocidade_vento,
        direcao_vento=r.direcao_vento,
        pressao_hpa=r.pressao_hpa,
        radiacao_solar=r.radiacao_solar,
        data_completa=r.data_completa,
        municipio=r.municipio,
        pais=r.pais,
        continente=r.continente,
        latitude=r.latitude,
        longitude=r.longitude,
    ) for r in rows]

