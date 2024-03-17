import json
import re
from typing import Any, Literal
from bs4 import BeautifulSoup
from bs4.element import Tag
from pydantic_settings import BaseSettings

from slots_scraper.parsing.exceptions import (
    ActiveCalendarNotFoundError,
    CalendarNotFoundError,
    DoctorNotFoundError,
    CredentialsNotFoundError
)
from slots_scraper.parsing.schemas import (
    _AuthCredentials,
    AddressCalendar,
    AddressCalendarList,
)

from slots_scraper.parsing.config import auth_config, params_config
from slots_scraper.models import _Token, DoctorParams


class BaseSoupInteractor:
    def __init__(self, html_content: str | bytes, search_config: BaseSettings):
        self._html_content = html_content
        self.soup = self._parse_markup()
        self.config = search_config

    @property
    def html_content(self):
        return self._html_content

    @html_content.setter
    def html_content(self, new_html_content: str | bytes):
        self._html_content = new_html_content
        self.soup = self._parse_markup()

    def _parse_markup(self) -> BeautifulSoup:
        return BeautifulSoup(self._html_content, 'html.parser')


class AuthParser(BaseSoupInteractor):
    def __init__(self, html_content: str | bytes, search_config=auth_config):
        super().__init__(html_content, search_config)

    @property
    def auth_credentials(self) -> dict[str, Any]:
        credentials = self.soup.find(self._find_token_tag)

        if not credentials:
            raise CredentialsNotFoundError()

        auth_credentials = self._extract_api_credentials(credentials)
        return auth_credentials.model_dump()

    @property
    def token(self) -> _Token:
        return _Token(**self.auth_credentials)

    def _extract_api_credentials(self, script_tag: Tag) -> _AuthCredentials:
        js_content = script_tag.get_text(strip=True)

        match = re.search(self.config.AUTH_REGEX, js_content, re.DOTALL)

        credentials = json.loads(match.group(1).replace("'", '"'))
        return _AuthCredentials(**credentials)

    def _find_token_tag(self, tag):
        return tag.name == 'script' and self.config.AUTH_KEY in tag.text


class ParamsParser(BaseSoupInteractor):
    def __init__(self, html_content: str | bytes, search_config=params_config):
        super().__init__(html_content, search_config)
        self._address_id = None


    @property
    def doctor_id(self) -> str:
        doctor_id = self.soup.find(name=self.config.DOCTOR_ID_TAG)
        if not doctor_id:
            raise DoctorNotFoundError()

        return doctor_id[self.config.DOCTOR_ID_KEY]

    @property
    def address_id(self) -> str:
        return self._address_id

    @address_id.setter
    def address_id(self, value: int | Literal['auto']):
        if value == 'auto':
            self._address_id = self.get_active_calendars()[0].id
        else:
            self._address_id = value

    def get_doctor_params(self):
        if self.address_id is None:
            self.address_id = 'auto'

        return DoctorParams(doctor_id=self.doctor_id,
                            address_id=self.address_id)

    def get_active_calendars(self) -> list[AddressCalendar]:
        active = [
            addr for addr in self.booking_calendars if addr.has_active_calendar
        ]
        if len(active) == 0:
            raise ActiveCalendarNotFoundError()

        return active

    @property
    def booking_calendars(self) -> list[AddressCalendar]:
        calendars = self.soup.find(
            name=self.config.CALENDAR_TAG)[self.config.CALENDAR_ADDRESSES_KEY]

        if not calendars:
            raise CalendarNotFoundError()

        return AddressCalendarList.validate_python(json.loads(calendars))
