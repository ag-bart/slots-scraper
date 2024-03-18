from collections import namedtuple

import requests
import pendulum

from slots_scraper.models import DoctorParams, QueryParams, Arguments, _Token
from slots_scraper.cache import setup_cache_manager
from slots_scraper.parsing.parsers import AuthParser, ParamsParser

from slots_scraper.constants import (
    CachePrefixes,
    _TOKEN_KEY,
    BASE_HEADERS,
    BASE_PARAMS,
    USER_AGENT
)

from slots_scraper import utils


_models_to_cache = {
    CachePrefixes.PARAMS: DoctorParams,
    CachePrefixes.TOKEN: _Token
}

CACHE = setup_cache_manager(_models_to_cache)

PreparedRequest = namedtuple('PreparedRequest', ['headers', 'url', 'params'])


def load_cached_values(url: str) -> tuple[str, DoctorParams]:
    url_key = utils.cache_key_from_url(url=url)

    cached_params: DoctorParams | None = CACHE.load_model_data(url_key)
    cached_token: _Token | None = CACHE.load_model_data(key=_TOKEN_KEY)

    if cached_params and cached_token and not cached_token.is_expired():
        return cached_token.token, cached_params

    if cached_params:
        response = requests.get(url)
        token_ = _get_token_from_response(response=response)
        CACHE.dump_model(token_, key=_TOKEN_KEY)
        return token_.token, cached_params

    return refresh_cache(url=url)


def refresh_cache(url: str) -> tuple[str, DoctorParams]:
    params_key = utils.cache_key_from_url(url=url)

    response = requests.get(url)

    params = _get_params_from_response(response=response)
    token_ = _get_token_from_response(response=response)

    CACHE.dump_model(params, key=params_key)
    CACHE.dump_model(token_, key=_TOKEN_KEY)

    return token_.token, params


def prepare_request(args: Arguments) -> PreparedRequest:
    url = args.url
    domain = args.url_domain
    weeks = args.weeks_offset

    search_range = _calculate_search_range(weeks_offset=weeks)
    params = _construct_query_params(search_range=search_range)

    access_token, doctor_params = load_cached_values(url)

    headers = _construct_request_headers(url=url,
                                         domain=domain,
                                         access_token=access_token)

    request_url = _construct_request_url(
        path_params=doctor_params, domain=domain)

    return PreparedRequest(headers=headers, url=request_url, params=params)


def _get_token_from_response(response: requests.Response) -> _Token:
    return AuthParser(response.text).token


def _get_params_from_response(response: requests.Response) -> DoctorParams:
    return ParamsParser(response.text).get_doctor_params()


def _construct_request_headers(url: str, access_token: str, domain: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Host": domain,
        "Referer": url,
        "User-Agent": USER_AGENT
    }

    return BASE_HEADERS | headers


def _construct_request_url(path_params: DoctorParams, domain: str):
    doctor_id, address_id = path_params.doctor_id, path_params.address_id,
    url = f"https://{domain}/api/v3/doctors/{doctor_id}/addresses/{address_id}/slots"
    return url


def _construct_query_params(search_range: QueryParams):
    date_params = {
        "start": search_range.start_date,
        "end": search_range.end_date
    }

    return BASE_PARAMS | date_params


def _calculate_search_range(weeks_offset) -> QueryParams:
    start_date = pendulum.now()
    end_date = start_date.add(weeks=weeks_offset)
    return QueryParams(start_date=start_date, end_date=end_date)
