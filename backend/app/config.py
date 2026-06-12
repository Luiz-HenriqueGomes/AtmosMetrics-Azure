# ============================================================
# AtmosMetrics — config.py
# Lê as variáveis de ambiente do .env (raiz do projeto)
# ============================================================

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas do arquivo .env.
    Funciona tanto no Docker (env vars injetadas pelo compose)
    quanto em desenvolvimento local (lê ../.env).
    """

    # Banco de Dados (SQL Server)
    db_name: str
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 1433

    # Chaves de API opcionais para ETLs globais
    openweather_api_key: str = ""    # OpenWeatherMap — qualidade do ar
    nasa_firms_map_key: str = ""     # NASA FIRMS — focos de calor globais

    model_config = SettingsConfigDict(
        # Tenta ../.env (dev local a partir de backend/) e .env (Docker)
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        extra="ignore",          # ignora variáveis desconhecidas no .env
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        """URL de conexão no formato esperado pelo SQLAlchemy (SQL Server)."""
        return (
            f"mssql+pymssql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
