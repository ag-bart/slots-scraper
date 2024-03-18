import argparse
import sys

import requests
from tabulate import tabulate

from urllib.parse import urlparse

from .models import Arguments, SlotsAdapter
from .prepare_request import prepare_request


def main() -> int:
    arguments = _parse_args()
    request_data = prepare_request(arguments)

    session = requests.Session()
    response = session.get(url=request_data.url,
                           headers=request_data.headers,
                           params=request_data.params)

    response.raise_for_status()

    data = _process_response(response=response)

    print(tabulate(data, headers='keys', tablefmt='pipe', showindex=True))

    return 0


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


def _process_response(response: requests.Response) -> list[dict]:
    data = response.json()['_items']
    slots = SlotsAdapter.validate_python(data)
    return SlotsAdapter.dump_python(slots)


if __name__ == "__main__":
    sys.exit(main())
