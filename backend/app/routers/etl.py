# ============================================================
# AtmosMetrics — routers/etl.py
# Endpoints: /api/v1/etl
# Disparo manual de pipelines de ingestão de dados
# ============================================================

from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from pydantic import BaseModel

from app.database import get_db

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])


class ETLResponse(BaseModel):
    status:    str
    mensagem:  str
    data:      str
    registros: int = 0


# ---- INPE (focos de calor Brasil) ------------------------------------------

@router.post("/executar", response_model=ETLResponse, summary="Executar ETL INPE (background)")
def executar_etl(
    background_tasks: BackgroundTasks,
    data: date = Query(
        default=None,
        description="Data para ingestão (YYYY-MM-DD). Padrão: ontem.",
    ),
    db: Session = Depends(get_db),
):
    """
    Dispara o pipeline ETL para baixar e carregar os focos de calor
    do INPE referentes à data informada.

    - Se `data` não for informada, usa o dia anterior (ontem).
    - O processamento ocorre em background para não bloquear a resposta.
    """
    from etl.loader import executar_pipeline

    if data is None:
        data = date.today() - timedelta(days=1)

    if data > date.today():
        raise HTTPException(
            status_code=400,
            detail=f"Data {data} é no futuro. Use uma data passada.",
        )

    background_tasks.add_task(executar_pipeline, data)

    return ETLResponse(
        status="iniciado",
        mensagem=f"ETL INPE para {data} iniciado em background. Verifique os logs do container.",
        data=str(data),
    )


@router.post("/executar-sync", response_model=ETLResponse, summary="ETL INPE síncrono")
def executar_etl_sync(
    data: date = Query(default=None, description="Data para ingestão (YYYY-MM-DD). Padrão: ontem."),
    db: Session = Depends(get_db),
):
    """
    Igual ao /executar, mas aguarda o processamento terminar antes de responder.
    Útil para testes e validação.
    """
    from etl.loader import executar_pipeline

    if data is None:
        data = date.today() - timedelta(days=1)

    if data > date.today():
        raise HTTPException(
            status_code=400,
            detail=f"Data {data} é no futuro. Use uma data passada.",
        )

    try:
        registros = executar_pipeline(data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no ETL INPE: {str(e)}",
        )

    return ETLResponse(
        status="concluído",
        mensagem=f"ETL INPE para {data} concluído com sucesso.",
        data=str(data),
        registros=registros,
    )


# ---- Open-Meteo (clima global) --------------------------------------------

@router.post("/executar-clima-sync", response_model=ETLResponse, summary="ETL Clima síncrono (Open-Meteo)")
def executar_clima_sync(
    data: date = Query(default=None, description="Data para ingestão (YYYY-MM-DD). Padrão: ontem."),
    db: Session = Depends(get_db),
):
    """
    Executa o pipeline de dados climáticos da Open-Meteo para todas as
    localidades com coordenadas de referência. Não requer API key.
    """
    from etl.openmeteo_etl import executar_pipeline_clima
    from app.models.dim_localidade import DimLocalidade

    # Cadastra as 27 referências estaduais do Brasil para ter dados de clima no mapa
    estados_brasil = [
        {"estado": "AC", "nome": "Acre", "lat": -9.97, "lon": -67.81, "regiao": "Norte", "bioma": "Amazônia"},
        {"estado": "AL", "nome": "Alagoas", "lat": -9.66, "lon": -35.73, "regiao": "Nordeste", "bioma": "Mata Atlântica"},
        {"estado": "AP", "nome": "Amapá", "lat": 0.03, "lon": -51.06, "regiao": "Norte", "bioma": "Amazônia"},
        {"estado": "AM", "nome": "Amazonas", "lat": -3.10, "lon": -60.02, "regiao": "Norte", "bioma": "Amazônia"},
        {"estado": "BA", "nome": "Bahia", "lat": -12.97, "lon": -38.51, "regiao": "Nordeste", "bioma": "Caatinga"},
        {"estado": "CE", "nome": "Ceará", "lat": -3.71, "lon": -38.54, "regiao": "Nordeste", "bioma": "Caatinga"},
        {"estado": "DF", "nome": "Distrito Federal", "lat": -15.78, "lon": -47.93, "regiao": "Centro-Oeste", "bioma": "Cerrado"},
        {"estado": "ES", "nome": "Espírito Santo", "lat": -20.31, "lon": -40.31, "regiao": "Sudeste", "bioma": "Mata Atlântica"},
        {"estado": "GO", "nome": "Goiás", "lat": -16.68, "lon": -49.25, "regiao": "Centro-Oeste", "bioma": "Cerrado"},
        {"estado": "MA", "nome": "Maranhão", "lat": -2.53, "lon": -44.30, "regiao": "Nordeste", "bioma": "Cerrado"},
        {"estado": "MT", "nome": "Mato Grosso", "lat": -15.59, "lon": -56.09, "regiao": "Centro-Oeste", "bioma": "Cerrado"},
        {"estado": "MS", "nome": "Mato Grosso do Sul", "lat": -20.44, "lon": -54.64, "regiao": "Centro-Oeste", "bioma": "Pantanal"},
        {"estado": "MG", "nome": "Minas Gerais", "lat": -19.92, "lon": -43.93, "regiao": "Sudeste", "bioma": "Cerrado"},
        {"estado": "PA", "nome": "Pará", "lat": -1.45, "lon": -48.50, "regiao": "Norte", "bioma": "Amazônia"},
        {"estado": "PB", "nome": "Paraíba", "lat": -7.11, "lon": -34.86, "regiao": "Nordeste", "bioma": "Caatinga"},
        {"estado": "PR", "nome": "Paraná", "lat": -25.42, "lon": -49.27, "regiao": "Sul", "bioma": "Mata Atlântica"},
        {"estado": "PE", "nome": "Pernambuco", "lat": -8.04, "lon": -34.87, "regiao": "Nordeste", "bioma": "Caatinga"},
        {"estado": "PI", "nome": "Piauí", "lat": -5.08, "lon": -42.80, "regiao": "Nordeste", "bioma": "Caatinga"},
        {"estado": "RJ", "nome": "Rio de Janeiro", "lat": -22.90, "lon": -43.20, "regiao": "Sudeste", "bioma": "Mata Atlântica"},
        {"estado": "RN", "nome": "Rio Grande do Norte", "lat": -5.79, "lon": -35.20, "regiao": "Nordeste", "bioma": "Caatinga"},
        {"estado": "RS", "nome": "Rio Grande do Sul", "lat": -30.03, "lon": -51.23, "regiao": "Sul", "bioma": "Pampa"},
        {"estado": "RO", "nome": "Rondônia", "lat": -8.76, "lon": -63.90, "regiao": "Norte", "bioma": "Amazônia"},
        {"estado": "RR", "nome": "Roraima", "lat": 2.82, "lon": -60.67, "regiao": "Norte", "bioma": "Amazônia"},
        {"estado": "SC", "nome": "Santa Catarina", "lat": -27.59, "lon": -48.54, "regiao": "Sul", "bioma": "Mata Atlântica"},
        {"estado": "SP", "nome": "São Paulo", "lat": -23.55, "lon": -46.63, "regiao": "Sudeste", "bioma": "Mata Atlântica"},
        {"estado": "SE", "nome": "Sergipe", "lat": -10.94, "lon": -37.07, "regiao": "Nordeste", "bioma": "Caatinga"},
        {"estado": "TO", "nome": "Tocantins", "lat": -10.21, "lon": -48.36, "regiao": "Norte", "bioma": "Cerrado"},
    ]
    
    for st in estados_brasil:
        existing = db.query(DimLocalidade).filter(
            DimLocalidade.municipio == st["nome"],
            DimLocalidade.estado == st["estado"]
        ).first()
        if existing:
            if not existing.latitude_ref:
                existing.latitude_ref = str(st["lat"])
                existing.longitude_ref = str(st["lon"])
                existing.pais = "Brasil"
                existing.continente = "América do Sul"
                existing.codigo_iso = "BR"
        else:
            loc = DimLocalidade(
                municipio=st["nome"],
                estado=st["estado"],
                uf=st["estado"],
                regiao=st["regiao"],
                bioma=st["bioma"],
                pais="Brasil",
                continente="América do Sul",
                latitude_ref=str(st["lat"]),
                longitude_ref=str(st["lon"]),
                codigo_iso="BR"
            )
            db.add(loc)
    db.commit()

    if data is None:
        data = date.today() - timedelta(days=1)

    if data > date.today():
        raise HTTPException(status_code=400, detail=f"Data {data} é no futuro.")

    try:
        registros = executar_pipeline_clima(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no ETL Clima: {str(e)}",
        )

    return ETLResponse(
        status="concluído",
        mensagem=f"ETL Clima para {data} concluído com sucesso.",
        data=str(data),
        registros=registros,
    )


# ---- OpenWeatherMap (qualidade do ar) --------------------------------------

@router.post("/executar-qualidade-ar-sync", response_model=ETLResponse, summary="ETL Qualidade do Ar (OpenWeatherMap)")
def executar_qualidade_ar_sync(
    data: date = Query(default=None, description="Data para ingestão (YYYY-MM-DD). Padrão: hoje."),
    db: Session = Depends(get_db),
):
    """
    Executa o pipeline de qualidade do ar via OpenWeatherMap.
    Requer OPENWEATHER_API_KEY configurada no .env.
    """
    from etl.openweather_etl import executar_pipeline_qualidade_ar

    if data is None:
        data = date.today()

    try:
        registros = executar_pipeline_qualidade_ar(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no ETL Qualidade do Ar: {str(e)}",
        )

    return ETLResponse(
        status="concluído",
        mensagem=f"ETL Qualidade do Ar para {data} concluído. Registros: {registros}",
        data=str(data),
        registros=registros,
    )


# ---- NASA FIRMS (focos de calor globais) -----------------------------------

@router.post("/executar-firms-sync", response_model=ETLResponse, summary="ETL NASA FIRMS (focos globais)")
def executar_firms_sync(
    data: date = Query(default=None, description="Data para ingestão (YYYY-MM-DD). Padrão: ontem."),
    db: Session = Depends(get_db),
):
    """
    Executa o pipeline de focos de calor globais via NASA FIRMS (VIIRS/SNPP).
    Requer NASA_FIRMS_MAP_KEY configurada no .env.
    """
    from etl.nasa_firms_etl import executar_pipeline_firms

    if data is None:
        data = date.today() - timedelta(days=1)

    if data > date.today():
        raise HTTPException(status_code=400, detail=f"Data {data} é no futuro.")

    try:
        registros = executar_pipeline_firms(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no ETL FIRMS: {str(e)}",
        )

    return ETLResponse(
        status="concluído",
        mensagem=f"ETL FIRMS para {data} concluído. Registros: {registros}",
        data=str(data),
        registros=registros,
    )


# ---- Pipeline Global (todos os ETLs) --------------------------------------

@router.post("/executar-global-sync", response_model=dict, summary="Executar TODOS os ETLs")
def executar_global_sync(
    data: date = Query(default=None, description="Data para ingestão (YYYY-MM-DD). Padrão: ontem."),
    db: Session = Depends(get_db),
):
    """
    Executa todos os pipelines ETL em sequência:
    1. INPE (focos Brasil)
    2. Open-Meteo (clima global)
    3. OpenWeatherMap (qualidade do ar)
    4. NASA FIRMS (focos globais)

    Retorna o resultado de cada pipeline individualmente.
    """
    from etl.loader import executar_pipeline
    from etl.openmeteo_etl import executar_pipeline_clima
    from etl.openweather_etl import executar_pipeline_qualidade_ar
    from etl.nasa_firms_etl import executar_pipeline_firms

    if data is None:
        data = date.today() - timedelta(days=1)

    resultados = {}

    # 1. INPE
    try:
        resultados["inpe"] = {"status": "concluído", "registros": executar_pipeline(data)}
    except Exception as e:
        resultados["inpe"] = {"status": "erro", "detalhe": str(e)}

    # 2. Open-Meteo (clima)
    try:
        resultados["clima"] = {"status": "concluído", "registros": executar_pipeline_clima(data)}
    except Exception as e:
        resultados["clima"] = {"status": "erro", "detalhe": str(e)}

    # 3. OpenWeatherMap (qualidade do ar)
    try:
        resultados["qualidade_ar"] = {"status": "concluído", "registros": executar_pipeline_qualidade_ar(data)}
    except Exception as e:
        resultados["qualidade_ar"] = {"status": "erro", "detalhe": str(e)}

    # 4. NASA FIRMS (focos globais)
    try:
        resultados["firms"] = {"status": "concluído", "registros": executar_pipeline_firms(data)}
    except Exception as e:
        resultados["firms"] = {"status": "erro", "detalhe": str(e)}

    return {
        "data": str(data),
        "pipelines": resultados,
    }

