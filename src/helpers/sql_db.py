# db_config.py

import json

import pydantic.json
from sqlalchemy import Engine, create_engine
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


def create_sync_engine(config: Config) -> Engine:
    return create_engine(
        f"postgresql://{config.db_username}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
    )
