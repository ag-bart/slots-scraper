class CachePrefixes:
    TOKEN: str = 'auth'
    PARAMS: str = 'doc'


_TOKEN_KEY = "auth_token.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/116.0"

BASE_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

BASE_PARAMS = {
        "includingSaasOnlyCalendar": "false",
        "with[]": [
            "address.nearest_slot_after_end",
            "links.book.patient",
            "slot.doctor_id",
            "slot.address_id",
            "slot.address",
            "slot.with_booked"
        ],
    }
