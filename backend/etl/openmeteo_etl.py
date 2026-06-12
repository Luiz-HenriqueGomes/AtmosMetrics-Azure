# ============================================================
# AtmosMetrics — etl/openmeteo_etl.py
# Pipeline ETL para dados climáticos da API Open-Meteo
# (API gratuita — não requer chave de acesso)
# ============================================================

import httpx
from datetime import date

from app.database import SessionLocal
from app.models.dim_tempo import DimTempo
from app.models.dim_localidade import DimLocalidade
from app.models.fato_clima import FatoClima
from etl.transformers import construir_dim_tempo

# URL base da API Open-Meteo (histórico)
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"

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


def _buscar_clima_openmeteo(lat: float, lon: float, data: date) -> dict | None:
    """
    Consulta a API Open-Meteo para dados climáticos diários.
    Retorna dicionário com métricas ou None se falhar.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": data.isoformat(),
        "end_date": data.isoformat(),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_max",
            "wind_direction_10m_dominant",
            "pressure_msl_mean",
            "shortwave_radiation_sum",
        ]),
        "timezone": "auto",
    }

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()

        dados = response.json()
        daily = dados.get("daily", {})

        # Verifica se há dados retornados
        if not daily or not daily.get("time"):
            return None

        return {
            "temperatura_max":   _safe_val(daily.get("temperature_2m_max", [None])[0]),
            "temperatura_min":   _safe_val(daily.get("temperature_2m_min", [None])[0]),
            "temperatura_media": _safe_val(daily.get("temperature_2m_mean", [None])[0]),
            "umidade_media":     _safe_val(daily.get("relative_humidity_2m_mean", [None])[0]),
            "precipitacao_mm":   _safe_val(daily.get("precipitation_sum", [None])[0]),
            "velocidade_vento":  _safe_val(daily.get("wind_speed_10m_max", [None])[0]),
            "direcao_vento":     _safe_int(daily.get("wind_direction_10m_dominant", [None])[0]),
            "pressao_hpa":       _safe_val(daily.get("pressure_msl_mean", [None])[0]),
            "radiacao_solar":    _safe_val(daily.get("shortwave_radiation_sum", [None])[0]),
        }

    except Exception as e:
        print(f"[ETL-Clima] ⚠️  Erro ao buscar dados para ({lat}, {lon}): {e}")
        return None


def executar_pipeline_clima(data: date) -> int:
    """
    Executa o pipeline ETL de dados climáticos para a data informada.
    Consulta Open-Meteo para todas as localidades com coordenadas de referência.

    Returns:
        Número de registros inseridos.
    """
    print(f"\n{'='*60}")
    print(f"[ETL-Clima] Iniciando pipeline para {data}")
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
            print("[ETL-Clima] Nenhuma localidade com coordenadas de referência encontrada.")
            return 0

        print(f"[ETL-Clima] {len(localidades)} localidades para processar.")

        # Resolve id_tempo
        id_tempo = _get_ou_criar_dim_tempo(db, data)

        for loc in localidades:
            try:
                # Verifica se já existe registro para esta localidade/data
                existe = (
                    db.query(FatoClima)
                    .filter(
                        FatoClima.id_tempo == id_tempo,
                        FatoClima.id_localidade == loc.id_localidade,
                    )
                    .first()
                )
                if existe:
                    continue

                # Consulta API Open-Meteo
                clima = _buscar_clima_openmeteo(
                    float(loc.latitude_ref),
                    float(loc.longitude_ref),
                    data,
                )
                if not clima:
                    continue

                fato = FatoClima(
                    id_tempo=id_tempo,
                    id_localidade=loc.id_localidade,
                    **clima,
                )
                db.add(fato)
                inseridos += 1

                # Commit a cada 50 registros
                if inseridos % 50 == 0:
                    db.commit()
                    print(f"[ETL-Clima] {inseridos} registros inseridos...")

            except Exception as e:
                print(f"[ETL-Clima] ⚠️  Erro ao processar {loc.municipio}: {e}")
                continue

        db.commit()
        print(f"\n[ETL-Clima] ✅ Pipeline concluído! {inseridos} registros inseridos para {data}.")

    except Exception as e:
        db.rollback()
        print(f"\n[ETL-Clima] ❌ Falha crítica no pipeline: {e}")
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
        return None if v != v else v  # NaN check
    except (TypeError, ValueError):
        return None


def _safe_int(value) -> int | None:
    """Converte para int, retorna None se inválido."""
    try:
        if value is None:
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None
