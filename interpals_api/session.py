import yaml
import requests

from .cookie import Cookie
from .utils import find_csrf_token


class SessionError(Exception):
    pass


class Session:
    def __init__(self, username, interpals_sessid, csrf_cookieV2):
        self.username = username
        self.interpals_sessid = interpals_sessid
        self.csrf_cookieV2 = csrf_cookieV2

    def cookie(self):
        return {
            'interpals_sessid': self.interpals_sessid,
            'csrf_cookieV2': self.csrf_cookieV2
        }

    def save(self, path):
        with open(path, 'w') as f:
            data = {
                'username': self.username,
                'interpals_sessid': self.interpals_sessid,
                'csrf_cookieV2': self.csrf_cookieV2
            }
            yaml.dump(data, f)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            data = yaml.load(f)
        return cls(data['username'], data['interpals_sessid'], data['csrf_cookieV2'])

    @classmethod
    def extract_set_cookies(cls, response_headers):
        set_cookies = {}
        for key, value in response_headers.items():
            if key.lower() == "set-cookie":
                for val in value.split("HttpOnly,"):
                    cookie_key, cookie_value = Cookie.parse_set_cookie(val)
                    set_cookies[cookie_key] = cookie_value
        return set_cookies

    @classmethod
    def login(cls, username, password):
        response = requests.get("https://www.interpals.net/")
        set_cookies = cls.extract_set_cookies(response.headers)
        csrf_token = find_csrf_token(response.text)

        cookie = Cookie()
        cookie.update(set_cookies)
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
        response = requests.post(
            "https://www.interpals.net/app/auth/login",
            data=data,
            headers=headers,
            allow_redirects=False
        )
        set_cookies = cls.extract_set_cookies(response.headers)
        cookie.update(set_cookies)

        if response.status_code == 302 and response.reason == 'Found':
            return cls(username, cookie['interpals_sessid'], cookie['csrf_cookieV2'])

        if response.status_code == 200 and response.reason == 'OK':
            raise SessionError("Wrong username or password")

        raise SessionError("An error has occurred during logging in")
