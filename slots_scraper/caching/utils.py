from urllib.parse import urlparse
import re


def cache_key_from_url(url: str, pattern=r'^/([a-zA-Z0-9-]+)/'):
    path = urlparse(url).path
    match = re.match(pattern, path)
    if match:
        return match.group(1)
    return None
