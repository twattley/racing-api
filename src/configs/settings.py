from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

"""
DB_NAME=test_db
DB_ENDPOINT=localhost:5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_POOL_SIZE=20
DB_CONN_TIMEOUT=10
DB_QUERY_TIMEOUT=10
SERVICE_NAME=user_api_service
API_SERVER_HOST=0.0.0.0
API_SERVER_PORT=8000

"""


class Settings(BaseSettings):
    db_name: str
    db_username: str
    db_endpoint: str
    db_password: str
    db_pool_size: int
    db_conn_timeout: int
    db_query_timeout: int
    service_name: str
    api_host: str
    api_port: int


def get_settings(env_path: Path = Path(".env")) -> Settings:
    if env_path:
        load_dotenv(dotenv_path=env_path, override=True)
    return Settings()


def create_db_url(settings: Settings, is_async: bool = True) -> str:
    postgresql = "postgresql"
    asyncpg = "asyncpg"

    prefix = f"{postgresql}+{asyncpg}" if is_async else f"{postgresql}"

    return f"{prefix}://{settings.db_username}:{settings.db_password}@{settings.db_endpoint}/{settings.db_name}"


settings = get_settings()
db_url = create_db_url(settings)
