import re
import json

from bs4.element import Tag


CREDENTIALS_REGEX: str = r'APICredentials\s*=\s*({.*?});'


def _extract_api_credentials(script_tag: Tag) -> dict:
    js_content = script_tag.get_text(strip=True)

    match = re.search(CREDENTIALS_REGEX, js_content, re.DOTALL)

    credentials_json = match.group(1).replace("'", '"')
    credentials = json.loads(credentials_json)
    return credentials
