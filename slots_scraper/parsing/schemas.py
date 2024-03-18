from pydantic import (
    BaseModel,
    ConfigDict,
    AliasGenerator,
    TypeAdapter,
    computed_field
)
from pydantic.alias_generators import to_snake, to_camel

from slots_scraper import utils


alias_config = ConfigDict(alias_generator=AliasGenerator(
    validation_alias=to_camel,
    serialization_alias=to_snake))


class _AuthCredentials(BaseModel):
    model_config = ConfigDict(alias_generator=lambda x: x.upper())

    access_token: str
    access_token_expiration_time: int
    refresh_token: str | None
    refresh_token_expiration_time: str | None
    token_url: str

    @computed_field
    @property
    def expires_at(self) -> str:
        return utils.dt_from_timestamp(
            self.access_token_expiration_time).to_datetime_string()


class Services(BaseModel):
    model_config = alias_config

    id: int
    is_default: bool
    name: str


class AddressCalendar(BaseModel):
    model_config = alias_config

    id: int
    facility_id: int | None
    has_active_calendar: bool
    is_online_only: bool
    city_name: str | None
    street: str | None
    services: list[Services] | None


AddressCalendarList = TypeAdapter(list[AddressCalendar])
