# db_config.py

import json

import pydantic.json
from api_helpers.db_client import PsqlConnection, SQLDatabase
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import Config


def get_engine(db_url, config: Config):
    return create_async_engine(
        db_url,
        json_serializer=lambda *args, **kwargs: json.dumps(
            *args, default=pydantic.json.pydantic_encoder, **kwargs
        ),
        pool_size=config.db_pool_size,
        max_overflow=0,
        connect_args={
            "command_timeout": config.db_query_timeout,
            "timeout": config.db_conn_timeout,
        },
    )


def get_db():
    config = Config()
    return SQLDatabase(
        PsqlConnection(
            user=config.db_username,
            password=config.db_password,
            host=config.db_host,
            port=config.db_port,
            db=config.db_name,
        )
    )
