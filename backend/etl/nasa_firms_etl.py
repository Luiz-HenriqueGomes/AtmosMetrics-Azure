# ============================================================
# AtmosMetrics — etl/nasa_firms_etl.py
# Pipeline ETL para dados de incêndios globais (NASA FIRMS)
# Requer chave de API (NASA_FIRMS_MAP_KEY no .env)
# ============================================================

import httpx
import pandas as pd
from datetime import date
from io import StringIO

from app.database import SessionLocal
from app.config import get_settings
from app.models.dim_tempo import DimTempo
from app.models.dim_satelite import DimSatelite
from app.models.dim_localidade import DimLocalidade
from app.models.fato_anomalia_termica import FatoAnomaliaTermica
from etl.transformers import construir_dim_tempo

# URL base da API FIRMS (CSV por área)
FIRMS_BASE_URL = (
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
    "{map_key}/VIIRS_SNPP_NRT/-180,-90,180,90/1/{data}"
)

# Timeout longo — o download pode ser grande
REQUEST_TIMEOUT = 180.0


def _get_ou_criar_dim_tempo(db, data: date) -> int:
    """Retorna o id_tempo para a data. Cria o registro se não existir."""
    registro = db.query(DimTempo).filter(DimTempo.data_completa == data).first()
    if registro:
        return registro.id_tempo

    novo = DimTempo(**construir_dim_tempo(data))
    db.add(novo)
    db.flush()
    return novo.id_tempo


def _get_ou_criar_satelite(db, nome_satelite: str) -> int:
    """Retorna o id_satelite pelo nome. Cria se não existir."""
    nome = nome_satelite.strip().upper()
    registro = db.query(DimSatelite).filter(DimSatelite.nome_satelite == nome).first()
    if registro:
        return registro.id_satelite

    novo = DimSatelite(nome_satelite=nome, agencia="NASA")
    db.add(novo)
    db.flush()
    return novo.id_satelite


def _get_ou_criar_localidade_global(db, lat: float, lon: float, pais: str = None) -> int:
    """
    Obtém ou cria uma localidade global baseada nas coordenadas.
    Para simplificar, agrupa por quadrante de 1° x 1° (grade).
    """
    # Arredonda para grade de 1 grau para agrupar focos próximos
    lat_ref = round(lat, 0)
    lon_ref = round(lon, 0)
    nome_grid = f"Grid ({lat_ref:.0f}, {lon_ref:.0f})"

    # Tenta encontrar localidade existente no mesmo quadrante
    registro = (
        db.query(DimLocalidade)
        .filter(
            DimLocalidade.municipio == nome_grid,
            DimLocalidade.pais == (pais or "Não Identificado"),
        )
        .first()
    )
    if registro:
        return registro.id_localidade

    # Estima o continente baseado nas coordenadas
    continente = _estimar_continente(lat, lon)

    novo = DimLocalidade(
        municipio=nome_grid,
        pais=pais or "Não Identificado",
        continente=continente,
        latitude_ref=lat_ref,
        longitude_ref=lon_ref,
    )
    db.add(novo)
    db.flush()
    return novo.id_localidade


def _estimar_continente(lat: float, lon: float) -> str:
    """Estima o continente baseado em coordenadas aproximadas."""
    if lat > 66.5:
        return "Ártico"
    if lat < -60:
        return "Antártica"
    if -35 <= lat <= 12 and -82 <= lon <= -34:
        return "América do Sul"
    if 7 <= lat <= 72 and -168 <= lon <= -52:
        return "América do Norte"
    if 35 <= lat <= 71 and -25 <= lon <= 60:
        return "Europa"
    if -35 <= lat <= 37 and -18 <= lon <= 52:
        return "África"
    if -10 <= lat <= 55 and 60 <= lon <= 150:
        return "Ásia"
    if -47 <= lat <= -10 and 110 <= lon <= 180:
        return "Oceania"
    return "Não Identificado"


def executar_pipeline_firms(data: date) -> int:
    """
    Executa o pipeline ETL de incêndios globais via NASA FIRMS.
    Baixa CSV com focos de calor do mundo inteiro via VIIRS/SNPP.

    Returns:
        Número de registros inseridos.
    """
    settings = get_settings()
    map_key = settings.nasa_firms_map_key

    if not map_key:
        print("[ETL-FIRMS] ⚠️  NASA_FIRMS_MAP_KEY não configurada. Pulando pipeline.")
        return 0

    print(f"\n{'='*60}")
    print(f"[ETL-FIRMS] Iniciando pipeline global para {data}")
    print(f"{'='*60}")

    # 1. Download do CSV
    url = FIRMS_BASE_URL.format(map_key=map_key, data=data.strftime("%Y-%m-%d"))
    print(f"[ETL-FIRMS] Baixando dados de {url}")

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url)

            if response.status_code == 404:
                print(f"[ETL-FIRMS] Dados não disponíveis para {data}.")
                return 0

            response.raise_for_status()
    except Exception as e:
        print(f"[ETL-FIRMS] ❌ Erro no download: {e}")
        return 0

    conteudo = response.text
    if not conteudo.strip():
        print(f"[ETL-FIRMS] CSV vazio para {data}.")
        return 0

    # 2. Parseia CSV
    try:
        df = pd.read_csv(StringIO(conteudo), dtype=str)
    except Exception as e:
        print(f"[ETL-FIRMS] ❌ Erro ao parsear CSV: {e}")
        return 0

    print(f"[ETL-FIRMS] Download concluído: {len(df)} registros brutos.")

    # Normaliza nomes das colunas
    df.columns = [c.strip().lower() for c in df.columns]

    # Converte coordenadas
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"]  = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    else:
        print("[ETL-FIRMS] Colunas latitude/longitude não encontradas no CSV.")
        return 0

    df = df.dropna(subset=["latitude", "longitude"])

    # FRP
    if "frp" in df.columns:
        df["frp"] = pd.to_numeric(df["frp"], errors="coerce")

    # 3. Carga no banco
    db = SessionLocal()
    inseridos = 0

    try:
        id_tempo = _get_ou_criar_dim_tempo(db, data)

        # Satélite padrão para FIRMS VIIRS
        id_satelite = _get_ou_criar_satelite(db, "VIIRS_SNPP_FIRMS")

        for _, row in df.iterrows():
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])

                # Obtém ou cria localidade (agrupada por grade)
                pais_col = row.get("country_id", None)
                pais = str(pais_col).strip() if pais_col and str(pais_col) != "nan" else None
                id_localidade = _get_ou_criar_localidade_global(db, lat, lon, pais)

                frp_val = None
                if "frp" in row.index:
                    try:
                        frp_val = float(row["frp"]) if str(row["frp"]) != "nan" else None
                    except (TypeError, ValueError):
                        frp_val = None

                fato = FatoAnomaliaTermica(
                    id_tempo=id_tempo,
                    id_localidade=id_localidade,
                    id_satelite=id_satelite,
                    latitude=lat,
                    longitude=lon,
                    frp_megawatts=frp_val,
                )
                db.add(fato)
                inseridos += 1

                # Commit a cada 1000 registros
                if inseridos % 1000 == 0:
                    db.commit()
                    print(f"[ETL-FIRMS] {inseridos} registros inseridos...")

            except Exception as e:
                print(f"[ETL-FIRMS] ⚠️  Erro ao processar linha: {e}")
                continue

        db.commit()
        print(f"\n[ETL-FIRMS] ✅ Pipeline concluído! {inseridos} focos globais para {data}.")

    except Exception as e:
        db.rollback()
        print(f"\n[ETL-FIRMS] ❌ Falha crítica no pipeline: {e}")
        raise
    finally:
        db.close()

    return inseridos
