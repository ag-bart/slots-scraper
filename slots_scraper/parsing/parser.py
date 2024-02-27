import json
from bs4 import BeautifulSoup


from slots_scraper.parsing.config import soup_config
from slots_scraper.parsing.helpers import _extract_api_credentials
from slots_scraper.parsing.exceptions import (
    NoActiveCalendarError,
    NoAddressError,
    NoDoctorError,
    TokenNotFoundError
)

from slots_scraper.models import _AuthResponse


class HtmlParser:
    def __init__(self, html_content, config=soup_config):
        self.config = config
        self._html_content = html_content
        self.soup = self._parse_html()

    @property
    def html_content(self):
        return self._html_content

    @html_content.setter
    def html_content(self, new_html_content):
        self._html_content = new_html_content
        self.soup = self._parse_html()

    def find_auth_credentials(self) -> _AuthResponse:
        credentials = self.soup.find(
            lambda tag: tag.name == self.config.AUTH_TAG
            and self.config.AUTH_KEY in tag.text)

        if not credentials:
            raise TokenNotFoundError()

        credentials_dict = _extract_api_credentials(credentials)
        return _AuthResponse(**credentials_dict)

    def find_active_address_id(self) -> str:
        addresses_json = self._find_calendars()
        active_addresses_ids = [
            addr[self.config.ADDRESS_ID_KEY] for addr in addresses_json
            if addr[self.config.ADDRESS_IS_ACTIVE_KEY]
        ]
        if len(active_addresses_ids) < 1:
            raise NoActiveCalendarError()

        return active_addresses_ids[0]  # TODO: multiple active addresses

    def find_doctor_id(self):
        doctor_id = self.soup.find(name=self.config.DOCTOR_ID_TAG)
        if not doctor_id:
            raise NoDoctorError()

        return doctor_id[self.config.DOCTOR_ID_KEY]

    def _find_calendars(self) -> list[dict]:
        calendars = self.soup.find(
            name=self.config.CALENDAR_TAG)[self.config.CALENDAR_ADDRESSES_KEY]

        if not calendars:
            raise NoAddressError()

        calendar_addresses = json.loads(calendars)
        return calendar_addresses

    def _parse_html(self):
        return BeautifulSoup(self._html_content, self.config.PARSER)
