from __future__ import annotations

import requests

from slots_scraper.constants import USER_AGENT
from slots_scraper.models import _Token, DoctorParams
from slots_scraper.parsing.parser import HtmlParser


def get_response(url: str) -> requests.Response:
    headers = {'User-agent': USER_AGENT}
    response = requests.get(url, headers=headers)
    return response


def get_token_and_params(url: str) -> tuple[_Token, DoctorParams]:
    response = get_response(url=url)
    parser = HtmlParser(response.text)
    token = _get_token(parser)
    doctor_params = _get_doctor_params(parser)
    return token, doctor_params


def _get_doctor_params(soup: HtmlParser) -> DoctorParams:
    doc_id = soup.find_doctor_id()
    addr_id = soup.find_active_address_id()
    return DoctorParams(doctor_id=doc_id, address_id=addr_id)


def _get_token(soup: HtmlParser) -> _Token:
    auth = soup.find_auth_credentials()
    return _Token.from_auth_response(auth)
