from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    AUTH_KEY: str = "'ACCESS_TOKEN'"
    AUTH_REGEX: str = r'APICredentials\s*=\s*({.*?});'


class ParamsConfig(BaseSettings):
    CALENDAR_TAG: str = "calendar-app"
    CALENDAR_ADDRESSES_KEY: str = ":calendar-addresses"

    DOCTOR_ID_TAG: str = "save-doctor-app"
    DOCTOR_ID_KEY: str = ":doctor-id"





