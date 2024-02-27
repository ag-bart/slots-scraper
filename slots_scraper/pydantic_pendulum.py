from pydantic import GetCoreSchemaHandler
from pydantic_core import PydanticCustomError, core_schema
from pendulum import DateTime as _DateTime
import pendulum
import datetime


class DateTime(_DateTime):

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source,
            handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:

        return core_schema.no_info_wrap_validator_function(
            cls._validate, core_schema.datetime_schema())

    @classmethod
    def _validate(cls, value,
                  handler: core_schema.ValidatorFunctionWrapHandler):

        if isinstance(value, _DateTime):
            return handler(value)

        if isinstance(value, datetime.datetime):
            dt = pendulum.instance(value)
            return handler(dt)

        try:
            data = pendulum.parse(value)
        except Exception as exc:
            raise PydanticCustomError('value_error',
                                      'value is not a valid timestamp') from exc
        return handler(data)
