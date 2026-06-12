# ============================================================
# AtmosMetrics — main.py
# Ponto de entrada da aplicação FastAPI
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import check_connection
from app.routers import anomalias, localidades, satelites, etl, clima, qualidade_ar
from app.config import get_settings

settings = get_settings()


# ---- Lifespan (startup / shutdown) -----------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa ações no startup e shutdown da aplicação."""
    # Startup
    db_ok = check_connection()
    status = "✅ conectado" if db_ok else "❌ FALHOU — verifique o serviço db no Docker"
    print(f"\n🚀 AtmosMetrics API iniciando...")
    print(f"   Banco de dados: {status}")
    print(f"   Docs:           http://localhost:8000/docs\n")
    yield
    # Shutdown
    print("\n🛑 AtmosMetrics API encerrada.")


# ---- Aplicação -------------------------------------------------------------

app = FastAPI(
    title="AtmosMetrics API",
    description=(
        "API de monitoramento socioambiental global. "
        "Fornece dados de focos de calor (INPE/FIRMS), clima (Open-Meteo) "
        "e qualidade do ar (OpenWeatherMap) processados via Star Schema PostGIS."
    ),
    version="2.0.0",
    contact={
        "name": "Luiz Henrique Gomes de Oliveira & Kaio Correia",
    },
    lifespan=lifespan,
)

# ---- CORS ------------------------------------------------------------------
# Permite que o frontend (qualquer origem em dev) consuma a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # em produção: restringir para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Routers ---------------------------------------------------------------
app.include_router(anomalias.router)
app.include_router(localidades.router)
app.include_router(satelites.router)
app.include_router(etl.router)
app.include_router(clima.router)
app.include_router(qualidade_ar.router)


import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ---- Health Check ----------------------------------------------------------

@app.get("/api/health", tags=["Health"], summary="Status da API")
def health_check():
    """Verifica se a API e o banco de dados estão operacionais."""
    db_ok = check_connection()
    return {
        "status":    "online",
        "api":       "AtmosMetrics",
        "versao":    "2.0.0",
        "banco":     "conectado" if db_ok else "desconectado",
        "docs":      "/docs",
        "endpoints": {
            "anomalias":     "/api/v1/anomalias",
            "resumo":        "/api/v1/anomalias/resumo",
            "localidades":   "/api/v1/localidades",
            "estados":       "/api/v1/localidades/estados",
            "biomas":        "/api/v1/localidades/biomas",
            "paises":        "/api/v1/localidades/paises",
            "continentes":   "/api/v1/localidades/continentes",
            "satelites":     "/api/v1/satelites",
            "clima":         "/api/v1/clima",
            "qualidade_ar":  "/api/v1/qualidade-ar",
            "etl":           "/api/v1/etl/executar",
        },
    }

# ---- Frontend (SPA) --------------------------------------------------------

# Cria a pasta static caso não exista (evita erro se rodar antes do build do Vite)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Monta os assets estáticos do Vite (js, css, imagens)
app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

# Catch-all para o frontend (qualquer rota que não seja /api ou /docs cai aqui)
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not built yet. Run 'npm run build' in /frontend"}
