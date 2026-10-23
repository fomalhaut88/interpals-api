"""
Useful functions.
"""

import re
import json
from typing import Any


regex_csfr_token = re.compile(r'<meta name="csrf_token" content="(.*?)"')
"""
Regex for CSRF token meta tag, it selects its value.
"""

regex_uid = re.compile(r'<input type="hidden" name="uid" value="(\d+)">')
"""
Regex for user `uid` in HTML content.
"""

regex_uid_self = re.compile(
    r'<div class="hidden-uid" style="display: none;">(\d+)</div>'
)
"""
Regex for self `uid` in HTML content.
"""

regex_data_react_data = re.compile(
    r'<script .*? data-react-data>(.*?)</script>'
)
"""
Regex for React data stored in <script data-react-data>...
"""


def find_csrf_token(html: str) -> str | None:
    """
    Extract the content of CSRF token in the meta tag from HTML.
    """
    if match := regex_csfr_token.search(html):
        return match.group(1)
    else:
        return None


def parse_uid(html: str, is_self: bool = False) -> int | None:
    """
    Extract `uid` from HTML.
    """
    regex = regex_uid_self if is_self else regex_uid
    if match := regex.search(html):
        return int(match.group(1))
    else:
        return None


def find_react_data(html: str) -> Any | None:
    """
    Extract React JSON data as a Python object from data-react-data.
    """
    if match := regex_data_react_data.search(html):
        return json.loads(match.group(1))
    else:
        return None
