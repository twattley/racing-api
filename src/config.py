import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    db_name: str
    db_username: str
    db_host: str
    db_port: str
    db_password: str
    db_pool_size: int
    db_conn_timeout: int
    db_query_timeout: int
    service_name: str
    api_host: str
    api_port: int
    bf_username: str
    bf_password: str
    bf_app_key: str
    bf_certs_path: str


def load_config() -> Config:
    env = os.environ.get("ENV", "DEV")
    if env == "DEV":
        env_file = ".env"
    elif env == "TEST":
        env_file = "./tests/.test.env"
    load_dotenv(env_file, override=True)
    return Config()




def create_db_url(config: Config) -> str:
    return (
        "postgresql"
        + "+"
        + "asyncpg"
        + "://"
    db_usernam: stre
        + ":"
    db_passwor: strd
        + "@"
    db_hos: strt
        + ":"
    db_por: strt
        + "/"
    db_nam: stre
    )


config = load_config()
db_url = create_db_url(config)