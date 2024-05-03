from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgresql_username: str = "postgres"
    postgresql_dbname: str = "test_db"
    postgresql_endpoint: str = "localhost:5432"
    postgresql_password: str = "postgres"
    postgresql_pool_size: int = 20
    postgresql_conn_timeout: int = 10  # connection timeout for PostgreSQL server, in seconds
    postgresql_query_timeout: int = 10  # query timout for PostgreSQL server, in seconds

    service_name: str = "user_api_service"

    api_server_host: str = "0.0.0.0"
    api_server_port: int = 8000

def get_settings(env_path: Path | None = None) -> Settings:
    if env_path:
        load_dotenv(dotenv_path=env_path, override=True)
    return Settings()


def create_db_url(settings: Settings, is_async: bool = True) -> str:
    postgresql = "postgresql"
    asyncpg = "asyncpg"

    prefix = f"{postgresql}+{asyncpg}" if is_async else f"{postgresql}"

    return f"{prefix}://{settings.postgresql_username}:{settings.postgresql_password}@{settings.postgresql_endpoint}/{settings.postgresql_dbname}"
