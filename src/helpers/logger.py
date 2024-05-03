import json
import logging
from functools import wraps
from inspect import getcallargs

from fastapi import Depends
from starlette_context import context

from src.configs.settings import Settings, get_settings
from src.models.base_entity import BaseEntity

default_format = {
    "level": "levelname",
    "logger_name": "name",
    "timestamp": "asctime",
}


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        service_name: str,
        fmt_dict: dict = None,
        time_format: str = "%Y-%m-%dT%H:%M:%S",
        msec_format: str = "%s.%03dZ",
    ):
        self.service_name = service_name
        self.fmt_dict = fmt_dict if fmt_dict is not None else default_format
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def formatMessage(self, record: logging.LogRecord) -> dict:
        message_dict = {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

        message_dict["service_name"] = self.service_name

        if isinstance(record.msg, dict):
            message_dict.update(record.msg)
        elif isinstance(record.msg, BaseEntity):
            message_dict.update(record.msg.dict())
        elif isinstance(record.msg, str):
            message_dict["message"] = record.msg

        if context.exists():
            if message_dict.get("trace_id") is None:
                message_dict["trace_id"] = context["trace_id"]

            if message_dict.get("tenant_id") is None:
                message_dict["tenant_id"] = context["tenant_id"]

            if message_dict.get("operation_name") is None:
                message_dict["operation_name"] = context["operation_name"]

        return message_dict

    def format(self, record: logging.LogRecord) -> str:
        record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


def log(logger: logging.Logger):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            method_name = f"{fn.__module__}.{fn.__qualname__}"
            log_entity = {
                "method_name": method_name,
                "message": "Method called.",
            }

            if logger.level < logging.INFO:
                log_entity["args"] = getcallargs(fn, *args, **kwargs)

            logger.info(log_entity)

            result = None
            try:
                result = await fn(*args, **kwargs)
            except Exception as e:
                log_entity["error"] = e
                log_entity["message"] = "Method call failed with error."

                logger.exception(log_entity)
                raise e

            if logger.level < logging.INFO:
                log_entity["result"] = result

            log_entity["message"] = "Method executed successfully."

            logger.info(log_entity)
            return result

        return wrapper

    return decorator


def log_failure(logger: logging.Logger):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                result = await fn(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    {
                        "method_name": f"{fn.__module__}.{fn.__qualname__}",
                        "error": e,
                        "message": "Method call failed with error.",
                    }
                )
                raise e
            return result

        return wrapper

    return decorator


def get_logger(settings: Settings = Depends(get_settings)) -> logging.Logger:
    logger = logging.getLogger(name=settings.logger_name)
    logger.setLevel(level=settings.logger_level)
    ch = logging.StreamHandler()
    ch.setLevel(level=settings.logger_level)
    formatter = JsonFormatter(service_name=settings.service_name)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


logger = get_logger(get_settings())
