import re


def is_valid_type(url: str) -> dict:
    url_pattern = r'https://open\.spotify\.com/(track|album)/([a-zA-Z0-9]+)'
    match = re.match(url_pattern, url)
    if match:
        return {'type': match.group(1), 'id': match.group(2)}
    return {'type': None, 'id': None}
