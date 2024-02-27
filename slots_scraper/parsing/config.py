from pydantic_settings import BaseSettings


class SoupConfig(BaseSettings):
    PARSER: str = "html.parser"

    AUTH_TAG: str = "script"
    AUTH_KEY: str = "'ACCESS_TOKEN'"

    CALENDAR_TAG: str = "calendar-app"
    CALENDAR_ADDRESSES_KEY: str = ":calendar-addresses"
    ADDRESS_ID_KEY: str = "id"
    ADDRESS_IS_ACTIVE_KEY: str = "hasActiveCalendar"

    DOCTOR_ID_TAG: str = "save-doctor-app"
    DOCTOR_ID_KEY: str = ":doctor-id"


soup_config = SoupConfig()
