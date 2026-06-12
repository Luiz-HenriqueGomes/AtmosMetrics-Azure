# ============================================================
# AtmosMetrics — etl/openweather_etl.py
# Pipeline ETL para dados de qualidade do ar (OpenWeatherMap)
# Requer chave de API (OPENWEATHER_API_KEY no .env)
# ============================================================

import httpx
from datetime import date

from app.database import SessionLocal
from app.config import get_settings
from app.models.dim_tempo import DimTempo
from app.models.dim_localidade import DimLocalidade
from app.models.fato_qualidade_ar import FatoQualidadeAr
from etl.transformers import construir_dim_tempo

# URL base da API de poluição atmosférica do OpenWeatherMap
OPENWEATHER_AIR_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

# Timeout para requisições HTTP
REQUEST_TIMEOUT = 30.0


def _get_ou_criar_dim_tempo(db, data: date) -> int:
    """Retorna o id_tempo para a data. Cria o registro se não existir."""
    registro = db.query(DimTempo).filter(DimTempo.data_completa == data).first()
    if registro:
        return registro.id_tempo

    novo = DimTempo(**construir_dim_tempo(data))
    db.add(novo)
    db.flush()
    return novo.id_tempo


def _buscar_qualidade_ar(lat: float, lon: float, api_key: str) -> dict | None:
    """
    Consulta a API OpenWeatherMap Air Pollution para a localidade.
    Retorna dicionário com os componentes ou None se falhar.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
    }

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(OPENWEATHER_AIR_URL, params=params)
            response.raise_for_status()

        dados = response.json()
        lista = dados.get("list", [])

        if not lista:
            return None

        item = lista[0]
        main = item.get("main", {})
        components = item.get("components", {})

        return {
            "aqi":   main.get("aqi"),
            "co":    _safe_val(components.get("co")),
            "no":    _safe_val(components.get("no")),
            "no2":   _safe_val(components.get("no2")),
            "o3":    _safe_val(components.get("o3")),
            "so2":   _safe_val(components.get("so2")),
            "pm2_5": _safe_val(components.get("pm2_5")),
            "pm10":  _safe_val(components.get("pm10")),
            "nh3":   _safe_val(components.get("nh3")),
        }

    except Exception as e:
        print(f"[ETL-QualidadeAr] ⚠️  Erro ao buscar dados para ({lat}, {lon}): {e}")
        return None


def executar_pipeline_qualidade_ar(data: date) -> int:
    """
    Executa o pipeline ETL de qualidade do ar para a data informada.
    Consulta OpenWeatherMap para todas as localidades com coordenadas.

    Returns:
        Número de registros inseridos.
    """
    settings = get_settings()
    api_key = settings.openweather_api_key

    if not api_key:
        print("[ETL-QualidadeAr] ⚠️  OPENWEATHER_API_KEY não configurada. Pulando pipeline.")
        return 0

    print(f"\n{'='*60}")
    print(f"[ETL-QualidadeAr] Iniciando pipeline para {data}")
    print(f"{'='*60}")

    db = SessionLocal()
    inseridos = 0

    try:
        # Busca localidades com coordenadas de referência
        localidades = (
            db.query(DimLocalidade)
            .filter(
                DimLocalidade.latitude_ref.isnot(None),
                DimLocalidade.longitude_ref.isnot(None),
            )
            .all()
        )

        if not localidades:
            print("[ETL-QualidadeAr] Nenhuma localidade com coordenadas encontrada.")
            return 0

        print(f"[ETL-QualidadeAr] {len(localidades)} localidades para processar.")

        # Resolve id_tempo
        id_tempo = _get_ou_criar_dim_tempo(db, data)

        for loc in localidades:
            try:
                # Verifica se já existe registro para esta localidade/data
                existe = (
                    db.query(FatoQualidadeAr)
                    .filter(
                        FatoQualidadeAr.id_tempo == id_tempo,
                        FatoQualidadeAr.id_localidade == loc.id_localidade,
                    )
                    .first()
                )
                if existe:
                    continue

                # Consulta API OpenWeatherMap
                qualidade = _buscar_qualidade_ar(
                    float(loc.latitude_ref),
                    float(loc.longitude_ref),
                    api_key,
                )
                if not qualidade:
                    continue

                fato = FatoQualidadeAr(
                    id_tempo=id_tempo,
                    id_localidade=loc.id_localidade,
                    **qualidade,
                )
                db.add(fato)
                inseridos += 1

                # Commit a cada 50 registros
                if inseridos % 50 == 0:
                    db.commit()
                    print(f"[ETL-QualidadeAr] {inseridos} registros inseridos...")

            except Exception as e:
                print(f"[ETL-QualidadeAr] ⚠️  Erro ao processar {loc.municipio}: {e}")
                continue

        db.commit()
        print(f"\n[ETL-QualidadeAr] ✅ Pipeline concluído! {inseridos} registros para {data}.")

    except Exception as e:
        db.rollback()
        print(f"\n[ETL-QualidadeAr] ❌ Falha crítica no pipeline: {e}")
        raise
    finally:
        db.close()

    return inseridos


# ---- Utilitários -----------------------------------------------------------

def _safe_val(value) -> float | None:
    """Converte para float, retorna None se inválido."""
    try:
        if value is None:
            return None
        v = float(value)
        return None if v != v else v
    except (TypeError, ValueError):
        return None
