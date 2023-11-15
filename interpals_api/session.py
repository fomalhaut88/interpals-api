import json
from urllib.parse import urljoin

import requests
import aiohttp

from .utils import find_csrf_token
from .errors import (NoCSRFTokenError, WrongUsernameOrPasswordError,
                     SessionError, TooManyLoginAttemptsError)
from .cookie import Cookie


class Session:
    def __init__(self, username, interpals_sessid, csrf_cookieV2):
        self.username = username
        self.interpals_sessid = interpals_sessid
        self.csrf_cookieV2 = csrf_cookieV2

    def __repr__(self):
        return f"Session(username={self.username}, " \
               f"interpals_sessid={self.interpals_sessid}, " \
               f"csrf_cookieV2={self.csrf_cookieV2})"

    def cookie(self):
        return {
            'interpals_sessid': self.interpals_sessid,
            'csrf_cookieV2': self.csrf_cookieV2
        }

    def dump(self, f):
        kwargs = {
            'username': self.username,
            'interpals_sessid': self.interpals_sessid,
            'csrf_cookieV2': self.csrf_cookieV2,
        }
        json.dump(kwargs, f)

    @classmethod
    def load(cls, f):
        kwargs = json.load(f)
        return cls(**kwargs)

    @classmethod
    def login(cls, username, password):
        # Cookie object
        cookie = Cookie()

        # Request initial page
        csrf_token = cls._request_initial_page(cookie)

        # Request login endpoint
        cls._request_login_endpoint(username, password, cookie, csrf_token)

        # Create and return session instance
        return cls(username=username,
                   interpals_sessid=cookie['interpals_sessid'],
                   csrf_cookieV2=cookie['csrf_cookieV2'])

    @classmethod
    def _request_initial_page(cls, cookie):
        with requests.get("https://www.interpals.net/") as resp:
            # Get initial cookie
            set_cookie = Cookie.from_response_headers(resp.headers)
            cookie.update(set_cookie)

            # Extract CSRF token from the HTML
            csrf_token = find_csrf_token(resp.text)

            # Raise error if no token found
            if csrf_token is None:
                raise NoCSRFTokenError()

        return csrf_token

    @classmethod
    def _request_login_endpoint(cls, username, password, cookie, csrf_token):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie.as_string(),
            'Referer': 'https://www.interpals.net/',
        }
        data = {
            'username': username,
            'password': password,
            'csrf_token': csrf_token
        }

        # Request login entry point
        with requests.post("https://www.interpals.net/app/auth/login",
                           data=data, headers=headers, 
                           allow_redirects=False) as resp:
            # Update cookie
            set_cookie = Cookie.from_response_headers(resp.headers)
            cookie.update(set_cookie)

            # Check status
            if resp.status_code == 200:
                raise WrongUsernameOrPasswordError()
            elif resp.status_code == 302:
                location = resp.headers['Location']
            else:
                raise SessionError(
                    f"Unknown response status while login: {resp.status_code}"
                )

        # Request the location to check success
        url = urljoin("https://www.interpals.net", location)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie.as_string(),
        }
        with requests.get(url, headers=headers) as resp:
            if "Too many unsuccessful login attempts." in resp.text:
                raise TooManyLoginAttemptsError()


class SessionAsync(Session):
    @classmethod
    async def login(cls, username, password):
        # Cookie object
        cookie = Cookie()

        # Request initial page
        csrf_token = await cls._request_initial_page(cookie)

        # Request login endpoint
        await cls._request_login_endpoint(
            username, password, cookie, csrf_token
        )

        # Create and return session instance
        return cls(username=username,
                   interpals_sessid=cookie['interpals_sessid'],
                   csrf_cookieV2=cookie['csrf_cookieV2'])

    @classmethod
    async def _request_initial_page(cls, cookie):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.interpals.net/") as resp:
                # Get initial cookie
                set_cookie = Cookie.from_response_headers(resp.headers)
                cookie.update(set_cookie)

                # Extract CSRF token from the HTML
                text = await resp.text()
                csrf_token = find_csrf_token(text)

                # Raise error if no token found
                if csrf_token is None:
                    raise NoCSRFTokenError()

        return csrf_token

    @classmethod
    async def _request_login_endpoint(cls, username, password, cookie, 
                                      csrf_token):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie.as_string(),
            'Referer': 'https://www.interpals.net/',
        }
        data = {
            'username': username,
            'password': password,
            'csrf_token': csrf_token
        }

        # Request login entry point
        async with aiohttp.ClientSession() as session:
            async with session.post("https://www.interpals.net/app/auth/login",
                                    data=data, headers=headers, 
                                    allow_redirects=False) as resp:
                # Update cookie
                set_cookie = Cookie.from_response_headers(resp.headers)
                cookie.update(set_cookie)

                # Check status
                if resp.status == 200:
                    raise WrongUsernameOrPasswordError()
                elif resp.status == 302:
                    location = resp.headers['Location']
                else:
                    raise SessionError(
                        f"Unknown response status while login: {resp.status}"
                    )

        # Request the location to check success
        url = urljoin("https://www.interpals.net", location)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie.as_string(),
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                text = await resp.text()
                if "Too many unsuccessful login attempts." in text:
                    raise TooManyLoginAttemptsError()
