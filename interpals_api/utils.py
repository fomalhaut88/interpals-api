"""
Useful functions.
"""

import re
from typing import Optional


re_csfr_token = re.compile(r'<meta name="csrf_token" content="(.*?)"')
"""
Regex for CSRF token meta tag, it selects its value.
"""


def find_csrf_token(html: str) -> Optional[str]:
    """
    Extract the content of CSRF token in the meta tag from HTML.
    """
    match = re_csfr_token.search(html)
    if match is not None:
        return match.group(1)
    else:
        return None
