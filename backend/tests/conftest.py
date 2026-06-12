# ============================================================
# AtmosMetrics — tests/conftest.py
# Configuração central de fixtures para todos os testes.
# Utiliza SQLite em memória para evitar dependência de PostgreSQL.
# ============================================================

import os
import sys
import types
from datetime import date, time
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# ---------------------------------------------------------------------------
# Garantir que o diretório backend/ está no path
# ---------------------------------------------------------------------------
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# ---------------------------------------------------------------------------
# Configurar variáveis de ambiente ANTES de importar qualquer módulo da app
# ---------------------------------------------------------------------------
os.environ["POSTGRES_DB"] = "test"
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"

# ---------------------------------------------------------------------------
# Monkey-patch geoalchemy2.Geometry ANTES de importar os modelos
# ---------------------------------------------------------------------------
import geoalchemy2
from sqlalchemy import String as _SAString

class _FakeGeometry(_SAString):
    """Substitui Geometry do PostGIS por String para testes com SQLite."""
    def __init__(self, *args, **kwargs):
        super().__init__(length=255)

geoalchemy2.Geometry = _FakeGeometry

# ---------------------------------------------------------------------------
# Criar engine e session de teste (SQLite em memória)
# ---------------------------------------------------------------------------
SQLALCHEMY_TEST_URL = "sqlite:///file::memory:?cache=shared&uri=true"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

# ---------------------------------------------------------------------------
# Pré-registrar o módulo app.database em sys.modules com objetos SQLite.
# Isso evita que o import real tente se conectar ao PostgreSQL via psycopg2.
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM (versão teste)."""
    pass

def get_db():
    """Dependency injection para testes."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_connection():
    """Sempre retorna True nos testes."""
    return True

# Garante que o pacote 'app' existe em sys.modules
if "app" not in sys.modules:
    app_pkg = types.ModuleType("app")
    app_pkg.__path__ = [os.path.join(backend_dir, "app")]
    app_pkg.__package__ = "app"
    sys.modules["app"] = app_pkg

# Cria o módulo database substituto
db_module = types.ModuleType("app.database")
db_module.__file__ = os.path.join(backend_dir, "app", "database.py")
db_module.__package__ = "app"
db_module.engine = test_engine
db_module.SessionLocal = TestSessionLocal
db_module.Base = Base
db_module.get_db = get_db
db_module.check_connection = check_connection

# Registra no sys.modules para interceptar qualquer import futuro
sys.modules["app.database"] = db_module

# Também seta como atributo do pacote app
import app as _app_pkg
_app_pkg.database = db_module

# ---------------------------------------------------------------------------
# Agora importamos config (que não depende de database)
# ---------------------------------------------------------------------------
import app.config
app.config.get_settings.cache_clear()

# ---------------------------------------------------------------------------
# Agora podemos importar os modelos — eles usarão nosso Base do SQLite
# ---------------------------------------------------------------------------
from app.models.dim_tempo import DimTempo
from app.models.dim_localidade import DimLocalidade
from app.models.dim_satelite import DimSatelite
from app.models.fato_clima import FatoClima
from app.models.fato_qualidade_ar import FatoQualidadeAr
from app.models.fato_anomalia_termica import FatoAnomaliaTermica

# Importa o app FastAPI
from app.main import app as fastapi_app

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Cria todas as tabelas no início da sessão de testes."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session(create_tables):
    """Fornece uma sessão de banco de dados limpa para cada teste."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """
    TestClient do FastAPI com a dependência get_db sobrescrita
    para usar o banco SQLite em memória.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def seed_data(db_session):
    """
    Popula o banco de testes com dados mínimos.
    """
    # --- DimTempo ---
    tempo = DimTempo(
        id_tempo=1,
        data_completa=date(2025, 6, 10),
        ano=2025,
        semestre=1,
        trimestre=2,
        mes=6,
        nome_mes="Junho",
        semana_do_ano=23,
        dia=10,
        dia_da_semana=1,
        nome_dia="Terça-feira",
        e_fim_de_semana=False,
    )
    db_session.add(tempo)

    # --- DimLocalidade ---
    local = DimLocalidade(
        id_localidade=1,
        municipio="São Paulo",
        codigo_ibge="3550308",
        uf="SP",
        estado="São Paulo",
        regiao="Sudeste",
        bioma="Mata Atlântica",
        pais="Brasil",
        continente="América do Sul",
        latitude_ref=Decimal("-23.550520"),
        longitude_ref=Decimal("-46.633308"),
        codigo_iso="BRA",
    )
    db_session.add(local)

    # --- DimSatelite ---
    satelite = DimSatelite(
        id_satelite=1,
        nome_satelite="AQUA_M-T",
        agencia="NASA",
        descricao="Satélite AQUA para monitoramento térmico.",
    )
    db_session.add(satelite)

    db_session.flush()

    # --- FatoClima ---
    clima = FatoClima(
        id_clima=1,
        id_tempo=1,
        id_localidade=1,
        temperatura_media=Decimal("22.50"),
        temperatura_max=Decimal("28.00"),
        temperatura_min=Decimal("17.00"),
        umidade_media=Decimal("65.00"),
        precipitacao_mm=Decimal("5.20"),
        velocidade_vento=Decimal("12.30"),
        direcao_vento=180,
        pressao_hpa=Decimal("1013.25"),
        radiacao_solar=Decimal("250.00"),
    )
    db_session.add(clima)

    # --- FatoQualidadeAr ---
    qualidade = FatoQualidadeAr(
        id_qualidade_ar=1,
        id_tempo=1,
        id_localidade=1,
        aqi=2,
        co=Decimal("201.94"),
        no=Decimal("0.10"),
        no2=Decimal("5.30"),
        o3=Decimal("68.50"),
        so2=Decimal("1.20"),
        pm2_5=Decimal("12.40"),
        pm10=Decimal("18.60"),
        nh3=Decimal("3.10"),
    )
    db_session.add(qualidade)

    # --- FatoAnomaliaTermica (geom=None para SQLite) ---
    anomalia = FatoAnomaliaTermica(
        id_anomalia=1,
        id_tempo=1,
        id_localidade=1,
        id_satelite=1,
        latitude=Decimal("-23.550520"),
        longitude=Decimal("-46.633308"),
        geom=None,
        frp_megawatts=Decimal("15.70"),
        risco_fogo=Decimal("0.80"),
        precipitacao_mm=Decimal("0.00"),
        dias_sem_chuva=5,
        hora_utc=time(14, 30),
    )
    db_session.add(anomalia)

    db_session.commit()

    return {
        "tempo": tempo,
        "local": local,
        "satelite": satelite,
        "clima": clima,
        "qualidade": qualidade,
        "anomalia": anomalia,
    }
