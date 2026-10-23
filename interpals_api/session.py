"""
Session instance keeps the necessary cookie parameters so API calls work
correctly. Session can be created from raw cookie data or emulate the login
process using username and password.
"""

from typing import Self
from dataclasses import dataclass
from urllib.parse import urlencode

import requests
import aiohttp
from yarl import URL

from .config import HOST, USER_AGENT, HTTP_TIMEOUT
from .errors import (
    NoCSRFTokenError, WrongUsernameOrPasswordError, TooManyLoginAttemptsError
)
from .utils import find_csrf_token
from .cookie import Cookie


@dataclass
class Session:
    username: str
    """
    `username`
    """

    interpals_sessid: str
    """
    `interpals_sessid` cookie
    """

    csrf_cookieV2: str
    """
    `csrf_cookieV2` cookie
    """

    def cookie(self) -> Cookie:
        """
        Get cookie data as a cookie object.
        """
        return Cookie({
            'username': self.username,
            'interpals_sessid': self.interpals_sessid,
            'csrf_cookieV2': self.csrf_cookieV2,
        })

    def dumps(self) -> str:
        """
        Serialize session into a string.
        """
        return " ".join([
            self.username, self.interpals_sessid, self.csrf_cookieV2
        ])

    @classmethod
    def loads(cls, s: str) -> Self:
        """
        Deserialize session from the string.
        """
        username, interpals_sessid, csrf_cookieV2 = s.split(" ", 2)
        return cls(
            username=username,
            interpals_sessid=interpals_sessid,
            csrf_cookieV2=csrf_cookieV2,
        )


def login_sync(username: str, password: str) -> Session:
    """
    Emulate the login process. It will return a session instance on success.
    """
    if not username:
        raise ValueError("No username provided")

    if not password:
        raise ValueError("No password provided")

    with requests.Session() as session:
        # Step 1. Visit landing page
        with session.get(f"{HOST}/", timeout=HTTP_TIMEOUT) as resp:
            csrf_token = find_csrf_token(resp.text)

        if csrf_token is None:
            raise NoCSRFTokenError()

        # Step 2. Activate login form
        with session.post(
            f"{HOST}/app/auth/login",
            data=urlencode({
                'csrf_token': csrf_token,
                'username': username,
                'password': password,
            }),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': USER_AGENT,
                'Referer': HOST,
            },
            timeout=HTTP_TIMEOUT,
        ) as resp:
            if "too many unsuccessful login attempts" in resp.text.lower():
                raise TooManyLoginAttemptsError()

        if 'lt' not in session.cookies:
            raise WrongUsernameOrPasswordError()

        # Return session
        return Session(
            username=username,
            interpals_sessid=session.cookies['interpals_sessid'],
            csrf_cookieV2=session.cookies['csrf_cookieV2'],
        )


async def login_async(username: str, password: str) -> Session:
    """
    Emulate the login process. It will return a session instance on success.
    """
    if not username:
        raise ValueError("No username provided")

    if not password:
        raise ValueError("No password provided")

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        # Step 1. Visit landing page
        async with session.get(f"{HOST}/", timeout=HTTP_TIMEOUT) as resp:
            html = await resp.text()
            csrf_token = find_csrf_token(html)

        if csrf_token is None:
            raise NoCSRFTokenError()

        # Step 2. Activate login form
        async with session.post(
            f"{HOST}/app/auth/login",
            data=urlencode({
                'csrf_token': csrf_token,
                'username': username,
                'password': password,
            }),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': USER_AGENT,
                'Referer': HOST,
            },
            timeout=HTTP_TIMEOUT,
        ) as resp:
            html = await resp.text()
            if "too many unsuccessful login attempts" in html.lower():
                raise TooManyLoginAttemptsError()

        cookies = session.cookie_jar.filter_cookies(URL(HOST))

        if 'lt' not in cookies:
            raise WrongUsernameOrPasswordError()

        # Return session
        return Session(
            username=username,
            interpals_sessid=cookies['interpals_sessid'].value,
            csrf_cookieV2=cookies['csrf_cookieV2'].value,
        )
