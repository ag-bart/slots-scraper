from __future__ import annotations

import pendulum

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    computed_field,
    field_validator,
    PositiveInt
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
    doctor_id: str
    address_id: str

    @field_validator("doctor_id", "address_id", mode='before')
    @classmethod
    def transform_id_to_str(cls, value) -> str:
        return str(value)


class QueryParams(BaseModel):
    start_date: DateTime
    end_date: DateTime


class Arguments(BaseModel):
    url: str
    weeks_offset: PositiveInt
