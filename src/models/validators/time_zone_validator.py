from datetime import datetime


def validate_has_timezone(value: datetime):
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("Timezone is missing")

    return value
