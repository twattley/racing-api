# db_config.py

import json

import pydantic.json
from sqlalchemy.ext.asyncio import create_async_engine


def get_engine(db_url, settings):
    return create_async_engine(
        db_url,
        json_serializer=lambda *args, **kwargs: json.dumps(
            *args, default=pydantic.json.pydantic_encoder, **kwargs
        ),
        pool_size=settings.db_pool_size,
        max_overflow=0,
        connect_args={
            "command_timeout": settings.db_query_timeout,
            "timeout": settings.db_conn_timeout,
        },
    )
