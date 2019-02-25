import re


re_csfr_token = re.compile(r'<meta name="csrf-token" content="(.*?)"')


def find_csrf_token(html):
    match = re_csfr_token.search(html)
    if match is not None:
        return match.group(1)
    else:
        return None
