import os
import re
from urllib.parse import urljoin

import requests

from interpals_api.config import HOST, HTTP_TIMEOUT, USER_AGENT
from interpals_api.session import login_sync, Session


TEST_SESSION_PATH = "./test.session"

INTERPALS_USERNAME = os.getenv('INTERPALS_USERNAME')
INTERPALS_PASSWORD = os.getenv('INTERPALS_PASSWORD')


def ensure_session_sync() -> Session:
    if os.path.exists(TEST_SESSION_PATH):
        with open(TEST_SESSION_PATH, 'r') as f:
            content = f.read()
        session = Session.loads(content)
    else:
        session = login_sync(
            INTERPALS_USERNAME, INTERPALS_PASSWORD
        )
        content = session.dumps()
        with open(TEST_SESSION_PATH, 'w') as f:
            f.write(content)
    return session


def ensure_html_sync(path: str, session: Session | None = None) -> str:
    filename = re.sub(r'\W', '_', path)
    filepath = f"./tmp/{filename}.html"
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            html = f.read()
    else:
        with requests.get(
            urljoin(HOST, path),
            headers={
                'Cookie': str(session.cookie()) if session else '',
                'User-Agent': USER_AGENT,
            },
            timeout=HTTP_TIMEOUT,
        ) as resp:
            html = resp.text
        with open(filepath, 'w') as f:
            f.write(html)
    return html
