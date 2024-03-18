from __future__ import annotations
from typing_extensions import Annotated

import pendulum

from pydantic import (
    BaseModel,
    ConfigDict,
    TypeAdapter,
    Field,
    PositiveInt,
    AfterValidator,
    AliasChoices,
    field_validator
)

from src.slots_scraper.utils import DateTime, to_datetime


class _Token(BaseModel):
    token: str = Field(validation_alias=AliasChoices('access_token', 'token'))
    expires_at: str

    def is_expired(self) -> bool:
        if dt := to_datetime(self.expires_at):
            return dt <= pendulum.now()
        return True


class DoctorParams(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    doctor_id: str
    address_id: str


IsoStr = Annotated[DateTime,
                   AfterValidator(lambda x: x.isoformat(timespec='seconds'))]


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
        dt = to_datetime(value)
        if dt is not None:
            return dt.format("dddd DD MMMM, HH:mm", locale='pl')
        return ""


SlotsAdapter = TypeAdapter(list[Slot])
