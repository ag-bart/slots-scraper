import argparse
import sys
import pendulum
import requests
from urllib.parse import urlparse
from slots_scraper.models import QueryParams, Arguments, DoctorParams
from slots_scraper.constants import USER_AGENT, BASE_HEADERS
from slots_scraper import caching


def main():
    headers, url, params = _prepare_request()

    session = requests.Session()
    response = session.get(url, headers=headers, params=params)

    print(response.json())

    return 0


def _prepare_request():
    args = _parse_args()
    url = args.url
    domain = args.url_domain

    start = pendulum.today()
    end = start.add(weeks=args.weeks_offset)

    access_token, doctor_params = caching.load_cached_values(url)
    query_params = QueryParams(start_date=start, end_date=end)

    headers = _construct_request_headers(url=url,
                                         domain=domain,
                                         access_token=access_token)

    request_url = _construct_request_url(
        path_params=doctor_params, domain=domain)

    params = {
        "start": query_params.start_date.isoformat(),
        "end": query_params.end_date.isoformat(),
        "includingSaasOnlyCalendar": "false",
        "with[]": [
            "address.nearest_slot_after_end",
            "slot.with_booked",
        ]
    }
    return headers, request_url, params


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--url", required=True, type=str,
                        help="URL for the doctor profile.")
    parser.add_argument("--weeks", required=True, type=int,
                        help="Search time range from today (in weeks).")

    args = parser.parse_args()
    domain = urlparse(url=args.url).netloc
    return Arguments(url=args.url, weeks_offset=args.weeks, url_domain=domain)


def _construct_request_headers(url, access_token, domain):
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


if __name__ == "__main__":
    sys.exit(main())