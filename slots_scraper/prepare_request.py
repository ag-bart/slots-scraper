
import requests

from slots_scraper.parsing.parser import AuthParser, ParamsParser
from slots_scraper.cache import CacheManager, FileCache, ModelStore
from slots_scraper.models import _Token, DoctorParams
from slots_scraper.constants import CachePrefixes
from slots_scraper import utils


def setup_cache_manager():
    filecache = FileCache()
    store = ModelStore()

    store.register_model_type(prefix=CachePrefixes.TOKEN, model_type=_Token)
    store.register_model_type(prefix=CachePrefixes.PARAMS, model_type=DoctorParams)

    cache_manager = CacheManager(cache=filecache, model_store=store)
    return cache_manager


cache = setup_cache_manager()

_TOKEN_KEY = "auth_token.json"


def load_cached_values(url: str) -> tuple[str, DoctorParams]:
    url_key = utils.cache_key_from_url(url=url)

    cached_params: DoctorParams | None = cache.load_model_data(url_key)
    cached_token: _Token | None = cache.load_model_data(key=_TOKEN_KEY)

    if cached_params and cached_token and not cached_token.is_expired():
        return cached_token.token, cached_params

    if cached_params:
        response = requests.get(url)
        token_ = _get_token_from_response(response=response)
        cache.dump_model(token_, key=_TOKEN_KEY)
        return token_.token, cached_params

    return refresh_cache(url=url)


def refresh_cache(url: str) -> tuple[str, DoctorParams]:
    params_key = utils.cache_key_from_url(url=url)

    response = requests.get(url)

    params = _get_params_from_response(response=response)
    token_ = _get_token_from_response(response=response)

    cache.dump_model(params, key=params_key)
    cache.dump_model(token_, key=_TOKEN_KEY)

    return token_.token, params


def _get_token_from_response(response: requests.Response) -> _Token:
    return AuthParser(response.text).token


def _get_params_from_response(response: requests.Response) -> DoctorParams:
    return ParamsParser(response.text).get_doctor_params()
