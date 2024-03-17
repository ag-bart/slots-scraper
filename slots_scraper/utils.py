import re

from typing import TypeGuard
import datetime
from urllib.parse import urlparse

from pydantic import GetCoreSchemaHandler
from pydantic_core import PydanticCustomError, core_schema

import pendulum
from pendulum import DateTime as _DateTime

from slots_scraper.constants import CachePrefixes


class DateTime(_DateTime):

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source,
            handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:

        return core_schema.no_info_wrap_validator_function(
            cls._validate, core_schema.datetime_schema())

    @classmethod
    def _validate(cls, value,
                  handler: core_schema.ValidatorFunctionWrapHandler):

        if isinstance(value, _DateTime):
            return handler(value)

        if isinstance(value, datetime.datetime):
            dt = pendulum.instance(value)
            return handler(dt)

        try:
            data = pendulum.parse(value)
        except Exception as exc:
            raise PydanticCustomError('value_error',
                                      'value is not a valid timestamp') from exc
        return handler(data)


def to_datetime(raw: str) -> pendulum.DateTime | None:
    """Convert raw string to a `pendulum.DateTime`.

    Args:
        raw (str): The raw datetime string.

    Returns:
        Parsed instance, or `None` if the string has an invalid format.
    """
    dt = pendulum.parse(raw)
    if _is_datetime(dt):
        return dt
    return None


def dt_from_timestamp(ts: int, timezone='local') -> pendulum.DateTime | None:
    dt = pendulum.from_timestamp(timestamp=ts, tz=timezone)
    if _is_datetime(dt):
        return dt
    return None


def _is_datetime(
    val: pendulum.Date | pendulum.Time | pendulum.Duration
) -> TypeGuard[pendulum.DateTime]:
    return isinstance(val, pendulum.DateTime)


def cache_key_from_url(url: str, pattern=r'^/([a-zA-Z0-9-]+)/') -> str | None:
    path = urlparse(url).path
    match = re.match(pattern, path)
    if match:
        return f"{CachePrefixes.PARAMS}_{match.group(1)}.json"
    return None
