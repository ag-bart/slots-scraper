import argparse
import sys

import pendulum
import requests
from tabulate import tabulate

from urllib.parse import urlparse

from slots_scraper.models import QueryParams, Arguments, DoctorParams, adapter
from slots_scraper.constants import USER_AGENT, BASE_HEADERS
from slots_scraper.prepare_request import load_cached_values


def main() -> int:
    headers, url, params = _prepare_request()

    session = requests.Session()
    response = session.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()['_items']
    slots = adapter.validate_python(data)

    print(tabulate(adapter.dump_python(slots),
                   headers='keys',
                   tablefmt='pipe',
                   showindex=True))

    return 0


def _prepare_request():
    args = _parse_args()
    url = args.url
    domain = args.url_domain

    params = _construct_query_params(weeks_offset=args.weeks_offset)

    access_token, doctor_params = load_cached_values(url)

    headers = _construct_request_headers(url=url,
                                         domain=domain,
                                         access_token=access_token)

    request_url = _construct_request_url(
        path_params=doctor_params, domain=domain)

    return headers, request_url, params


def _parse_args() -> Arguments:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        "--url",
        required=True,
        type=str,
        help="URL for the doctor profile."
    )
    parser.add_argument(
        "--weeks",
        required=False,
        type=int,
        default=1,
        help="Search time range from today (in weeks). Default: 1 week."
    )

    args = parser.parse_args()
    domain = urlparse(url=args.url).netloc
    return Arguments(url=args.url, weeks_offset=args.weeks, url_domain=domain)


def _construct_request_headers(url: str, access_token: str, domain: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Host": domain,
        "Referer": url,
        "User-Agent": USER_AGENT
    }

    return BASE_HEADERS | headers


def _construct_request_url(path_params: DoctorParams, domain: str):
    doctor_id, address_id = path_params.doctor_id, path_params.address_id,
    url = f"https://{domain}/api/v3/doctors/{doctor_id}/addresses/{address_id}/slots"
    return url


def _construct_query_params(weeks_offset: int):
    start = pendulum.now()
    end = start.add(weeks=weeks_offset)
    query_params = QueryParams(start_date=start, end_date=end).dict()

    params = {
        "start": query_params["start_date"],
        "end": query_params["end_date"],
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

    return params


if __name__ == "__main__":
    sys.exit(main())
