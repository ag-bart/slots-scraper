
class HtmlParserError(Exception):
    """Base exception class for HtmlParser errors."""


class ActiveCalendarNotFoundError(HtmlParserError):
    def __init__(self):
        super().__init__("The requested doctor has no active calendars!")


class TagNotFoundError(HtmlParserError):
    def __init__(self, tag: str):
        super().__init__(f"Unable to find {tag} in the HTML document. "
                         "Check Parser configuration and page source.")


class CalendarNotFoundError(TagNotFoundError):
    def __init__(self):
        super().__init__("address calendar")


class DoctorNotFoundError(TagNotFoundError):
    def __init__(self):
        super().__init__("doctor ID")


class CredentialsNotFoundError(TagNotFoundError):
    def __init__(self):
        super().__init__("authentication token")
