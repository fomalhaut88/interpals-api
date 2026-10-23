"""
Classes that implement sync and async API calls and parsing. To create an
instance session object is required.
"""

import json
import asyncio
from time import sleep
from urllib.parse import urljoin, urlencode
from typing import Iterator, Any

import aiohttp
import requests

from .config import HOST, HTTP_TIMEOUT, USER_AGENT
from .session import Session
from .errors import APIError, APIAuthError, NoCSRFTokenError, ParseError
from .utils import parse_uid, find_csrf_token
from .schemas import Profile, Album, Picture, SearchOptions
from .parsers.profile import ProfileParser
from .parsers.userdata import UserDataParser
from .parsers.pictures import AlbumsParser, PicturesParser


class ApiSync:
    """
    Class for synchronous API.
    """

    def __init__(self, session: Session):
        """
        Create an API instance.
        """
        self._session = session

    def check_auth(self) -> bool:
        """
        Check whether the session is authorized.
        """
        try:
            self._get(self._session.username)
        except APIAuthError:
            return False
        else:
            return True

    def view(self, user: str):
        """
        View the given user.
        """
        self._get(user)

    def profile(self, user: str) -> Profile:
        """
        Get the profile information of the user.
        """
        html = self._get(user)

        if "user not found" in html.lower():
            raise APIError("user not found")

        if (
            "this user's privacy settings do not allow you to contact them"
        ) in html.lower():
            raise APIError("blocked by user")

        return ProfileParser().parse(html)

    def get_uid(self, user: str | None = None) -> str:
        """
        Get unique user identifier `uid`.
        """
        if user is None:
            user = self._session.username
        html = self._get(user)
        uid = parse_uid(html, is_self=user == self._session.username)
        if uid is None:
            raise ParseError("uid")
        return uid

    def visitors(self) -> list[Profile]:
        """
        Get users who viewed your profile.
        """
        html = self._get("/app/views")
        return UserDataParser().parse(html)

    def albums(self, uid: str) -> list[Album]:
        """
        Get albums of the user given by `uid`.
        """
        html = self._get("/app/albums", {'uid': uid})
        return AlbumsParser().parse(html)

    def pictures(self, uid: str, aid: str) -> list[Picture]:
        """
        Get pictures of the user (given by `uid`) and his album (given by
        `aid`).
        """
        html = self._get("/app/album", {'uid': uid, 'aid': aid})
        return PicturesParser().parse(html)

    def get_citycode(self, cityname: str) -> int:
        """
        Get the code of the city in the system by its name.
        """
        content = self._get(
            "/app/async/geoAc", {"query": cityname}, check_auth=False
        )
        data = json.loads(content)
        return int(data['items'][0]['id'])

    def search(
        self, options: SearchOptions, limit: int = 1000, timeout: float = 0.0
    ) -> Iterator[Profile]:
        # Build search querystring params
        params = _prepare_search_params(options)

        # Load city code if it is required
        if 'cityName' in params and 'city' not in params:
            params['city'] = self.get_citycode(params['cityName'])

        # Load initial page to get CSFR token
        html = self._get("/app/search")
        params['csrf_token'] = find_csrf_token(html)

        if params['csrf_token'] is None:
            raise NoCSRFTokenError()

        # Search loop
        parser = UserDataParser()
        params['offset'] = 0
        while True:
            sleep(timeout)

            html = self._get("/app/search", params)
            users = parser.parse(html)

            if not users:
                return

            for user in users:
                yield user
                params['offset'] += 1
                if params['offset'] >= limit:
                    return

    def _get(
        self, path: str, params: dict | None = None, check_auth: bool = True
    ) -> str:
        # Prepare URL
        url = urljoin(HOST, path)
        if params:
            url += '?' + urlencode(params, True)

        # Request for HTML
        with requests.get(
            url,
            headers={
                'Cookie': str(self._session.cookie()),
                'User-Agent': USER_AGENT,
            },
            timeout=HTTP_TIMEOUT,
        ) as resp:
            html = resp.text

        # Check auth
        if check_auth and "/app/auth/logout" not in html:
            raise APIAuthError()

        return html


class ApiAsync:
    """
    Class for asynchronous API.
    """

    def __init__(self, session: Session):
        """
        Create an API instance.
        """
        self._session = session

    async def check_auth(self) -> bool:
        """
        Check whether the session is authorized.
        """
        try:
            await self._get(self._session.username)
        except APIAuthError:
            return False
        else:
            return True

    async def view(self, user: str):
        """
        View the given user.
        """
        await self._get(user)

    async def profile(self, user: str) -> Profile:
        """
        Get the profile information of the user.
        """
        html = await self._get(user)

        if "user not found" in html.lower():
            raise APIError("user not found")

        if (
            "this user's privacy settings do not allow you to contact them"
        ) in html.lower():
            raise APIError("blocked by user")

        return ProfileParser().parse(html)

    async def get_uid(self, user: str | None = None) -> str:
        """
        Get unique user identifier `uid`.
        """
        if user is None:
            user = self._session.username
        html = await self._get(user)
        uid = parse_uid(html, is_self=user == self._session.username)
        if uid is None:
            raise ParseError("uid")
        return uid

    async def visitors(self) -> list[Profile]:
        """
        Get users who viewed your profile.
        """
        html = await self._get("/app/views")
        return UserDataParser().parse(html)

    async def albums(self, uid: str) -> list[Album]:
        """
        Get albums of the user given by `uid`.
        """
        html = await self._get("/app/albums", {'uid': uid})
        return AlbumsParser().parse(html)

    async def pictures(self, uid: str, aid: str) -> list[Picture]:
        """
        Get pictures of the user (given by `uid`) and his album (given by
        `aid`).
        """
        html = await self._get("/app/album", {'uid': uid, 'aid': aid})
        return PicturesParser().parse(html)

    async def get_citycode(self, cityname: str) -> int:
        """
        Get the code of the city in the system by its name.
        """
        content = await self._get(
            "/app/async/geoAc", {"query": cityname}, check_auth=False
        )
        data = json.loads(content)
        return int(data['items'][0]['id'])

    async def search(
        self, options: SearchOptions, limit: int = 1000, timeout: float = 0.0
    ) -> Iterator[Profile]:
        # Build search querystring params
        params = _prepare_search_params(options)

        # Load city code if it is required
        if 'cityName' in params and 'city' not in params:
            params['city'] = await self.get_citycode(params['cityName'])

        # Load initial page to get CSFR token
        html = await self._get("/app/search")
        params['csrf_token'] = find_csrf_token(html)

        if params['csrf_token'] is None:
            raise NoCSRFTokenError()

        # Search loop
        parser = UserDataParser()
        params['offset'] = 0
        while True:
            await asyncio.sleep(timeout)

            html = await self._get("/app/search", params)
            users = parser.parse(html)

            if not users:
                return

            for user in users:
                yield user
                params['offset'] += 1
                if params['offset'] >= limit:
                    return

    async def _get(
        self, path: str, params: dict | None = None, check_auth: bool = True
    ) -> str:
        # Prepare URL
        url = urljoin(HOST, path)
        if params:
            url += '?' + urlencode(params, True)

        # Request for HTML
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    'Cookie': str(self._session.cookie()),
                    'User-Agent': USER_AGENT,
                },
                timeout=HTTP_TIMEOUT,
            ) as resp:
                html = await resp.text()

        # Check auth
        if check_auth and "/app/auth/logout" not in html:
            raise APIAuthError()

        return html


def _prepare_search_params(options: SearchOptions) -> dict[str, Any]:
    params = {
        'offset': 0,
        'sort': 'last_login',
        'age1': options.age1,
        'age2': options.age2,
        'sex[]': options.sex,
        'continents[]': options.continents,
        'countries[]': options.countries or ['---'],
        'languages[]': ['---'],
        'lfor[]': [
            'lfor_email', 'lfor_snail', 'lfor_langex',
            'lfor_friend', 'lfor_flirt', 'lfor_relation'
        ],
        'keywords': options.keywords,
        'username': '',
        'csrf_token': 'ZjU1ZWZkM2Q=',
    }

    if options.online:
        params['online'] = '1'

    if options.city_code:
        params['city'] = options.city_code

    if options.city_name:
        params['cityName'] = options.city_name

    return params
