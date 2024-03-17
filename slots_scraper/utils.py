from typing import TypeGuard

import pendulum
from slots_scraper.constants import CachePrefixes


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
