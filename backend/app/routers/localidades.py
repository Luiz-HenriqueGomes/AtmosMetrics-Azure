# ============================================================
# AtmosMetrics — routers/localidades.py
# Endpoints: /api/v1/localidades
# Expandido com filtros globais (países, continentes)
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func
from typing import Optional

from app.database import get_db
from app.models.dim_localidade import DimLocalidade
from app.schemas.localidade import LocalidadeOut, EstadoOut, BiomaOut, PaisOut, ContinenteOut

router = APIRouter(prefix="/api/v1/localidades", tags=["Localidades"])


@router.get("/", response_model=list[LocalidadeOut], summary="Listar localidades")
def listar_localidades(
    pais:       Optional[str] = Query(None, description="Filtrar por país"),
    continente: Optional[str] = Query(None, description="Filtrar por continente"),
    db: Session = Depends(get_db),
):
    """Retorna todas as localidades cadastradas no banco, com filtros opcionais."""
    query = db.query(DimLocalidade)
    if pais:
        query = query.filter(DimLocalidade.pais.ilike(f"%{pais}%"))
    if continente:
        query = query.filter(DimLocalidade.continente.ilike(f"%{continente}%"))
    return query.order_by(DimLocalidade.pais, DimLocalidade.municipio).all()


@router.get("/estados", response_model=list[EstadoOut], summary="Listar estados brasileiros")
def listar_estados(db: Session = Depends(get_db)):
    """Retorna a lista de estados únicos — útil para filtros no frontend."""
    rows = (
        db.query(
            DimLocalidade.uf,
            func.min(DimLocalidade.estado).label("estado"),
            func.min(DimLocalidade.regiao).label("regiao"),
        )
        .filter(DimLocalidade.uf.isnot(None))
        .group_by(DimLocalidade.uf)
        .order_by(func.min(DimLocalidade.estado))
        .all()
    )
    return [EstadoOut(uf=r.uf, estado=r.estado, regiao=r.regiao) for r in rows]


@router.get("/biomas", response_model=list[BiomaOut], summary="Listar biomas")
def listar_biomas(db: Session = Depends(get_db)):
    """Retorna a lista de biomas únicos — útil para filtros no frontend."""
    rows = (
        db.query(distinct(DimLocalidade.bioma).label("bioma"))
        .filter(DimLocalidade.bioma.isnot(None))
        .order_by(DimLocalidade.bioma)
        .all()
    )
    return [BiomaOut(bioma=r.bioma) for r in rows]


@router.get("/paises", response_model=list[PaisOut], summary="Listar países")
def listar_paises(db: Session = Depends(get_db)):
    """Retorna a lista de países únicos com seus continentes e códigos ISO."""
    rows = (
        db.query(
            DimLocalidade.pais,
            func.min(DimLocalidade.continente).label("continente"),
            func.min(DimLocalidade.codigo_iso).label("codigo_iso"),
        )
        .filter(DimLocalidade.pais.isnot(None))
        .group_by(DimLocalidade.pais)
        .order_by(DimLocalidade.pais)
        .all()
    )
    return [PaisOut(pais=r.pais, continente=r.continente, codigo_iso=r.codigo_iso) for r in rows]


@router.get("/continentes", response_model=list[ContinenteOut], summary="Listar continentes")
def listar_continentes(db: Session = Depends(get_db)):
    """Retorna a lista de continentes únicos."""
    rows = (
        db.query(distinct(DimLocalidade.continente).label("continente"))
        .filter(DimLocalidade.continente.isnot(None))
        .order_by(DimLocalidade.continente)
        .all()
    )
    return [ContinenteOut(continente=r.continente) for r in rows]
