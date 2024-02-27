from __future__ import annotations

from pydantic import RootModel

from slots_scraper.models import _Token, DoctorParams
from slots_scraper.caching import cache, utils
from slots_scraper.parsing import get_token_and_params


_TOKEN_KEY = "slotsScraper_token.json"


def load_cached_values(url: str):
    doc_params_key = utils.cache_key_from_url(url=url)
    doc_params = _cached_doctor_params(doc_params_key)

    if doc_params:
        if (cached_token := _cached_token()) and not cached_token.is_expired():
            return cached_token.token, doc_params

    token_, params = get_token_and_params(url=url)

    _refresh_cache(token=token_, params=params, params_key=doc_params_key)
    return token_.token, params


def _cached_token() -> _Token | None:
    if cached := cache.get(_TOKEN_KEY):
        return RootModel[_Token].model_validate_json(cached).root
    return None


def _store_token(token: _Token) -> None:
    cache.store((RootModel[_Token](token).model_dump_json()), key=_TOKEN_KEY)


def _cached_doctor_params(params_key) -> DoctorParams | None:
    if cached := cache.get(params_key):
        return DoctorParams.model_validate_json(cached)
    return None


def _store_doctor_params(params: DoctorParams, params_key) -> None:
    cache.store(params.model_dump_json(), key=params_key)


def _refresh_cache(token, params, params_key) -> None:
    _store_token(token)
    _store_doctor_params(params, params_key)
