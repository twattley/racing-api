# db_config.py

import json

import pydantic.json
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import config

def get_engine(db_url):
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
