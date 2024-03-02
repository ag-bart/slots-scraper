from __future__ import annotations
from typing_extensions import Annotated

import pendulum

from pydantic import (
    BaseModel,
    ConfigDict,
    TypeAdapter,
    Field,
    PositiveInt,
    PlainSerializer,
    computed_field,
    field_validator
)
from pydantic.dataclasses import dataclass

from slots_scraper import utils
from slots_scraper.pydantic_pendulum import DateTime


class _AuthResponse(BaseModel):
    model_config = ConfigDict(alias_generator=lambda x: x.upper())

    access_token: str
    access_token_expiration_time: int
    refresh_token: str | None
    refresh_token_expiration_time: str | None
    token_url: str = Field(exclude=True)

    @computed_field
    @property
    def expires_at(self) -> str:
        return utils.dt_from_timestamp(
            self.access_token_expiration_time).to_datetime_string()


@dataclass
class _Token:
    token: str
    expires_at: str

    def is_expired(self) -> bool:
        if dt := utils.to_datetime(self.expires_at):
            return dt <= pendulum.now()
        return True

    @classmethod
    def from_auth_response(cls, auth_response: _AuthResponse) -> _Token:
        return _Token(
            token=auth_response.access_token,
            expires_at=auth_response.expires_at)


class DoctorParams(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    doctor_id: str
    address_id: str


IsoStr = Annotated[
    DateTime, PlainSerializer(lambda x: x.isoformat(timespec='seconds'),
                              return_type=str)
]


class QueryParams(BaseModel):
    start_date: IsoStr
    end_date: IsoStr


class Arguments(BaseModel):
    url: str
    weeks_offset: PositiveInt
    url_domain: str


class Slot(BaseModel):
    start: str
    booked: bool
    booking_url: str | None

    @field_validator('start', mode='before')
    @classmethod
    def format_date(cls, value) -> str:
        dt = utils.to_datetime(value)
        if dt is not None:
            return dt.format("dddd DD MMMM, HH:mm", locale='pl')
        return ""


adapter = TypeAdapter(list[Slot])
