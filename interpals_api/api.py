"""
Classes that implement sync and async API calls and parsing. To create an
instance session object is required.
"""

import json
import asyncio
from urllib.parse import urlencode, urlparse, parse_qs
from time import sleep
from typing import List, Dict, Any, Generator, Optional

import requests
import aiohttp
from bs4 import BeautifulSoup

from .errors import *
from .cookie import Cookie
from .utils import find_csrf_token
from .parsers.profile_parser import ProfileParser
from .parsers.chat_parser import ChatParser
from .parsers.friends_parser import FriendsParser
from .parsers.pictures_parser import PicturesParser
from .session import Session, SessionAsync


class Api:
    """
    Class for synchronous API.
    """

    timeout = 3.0
    """
    Timeout for HTTP calls. Override it if needed.
    """

    host = "interpals.net"
    """
    Host address.
    """

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    """
    `User-Agent` header in each HTTP call. Override it if needed.
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
        if self._session:
            response = self._get(self._session.username)
            return self._check_body_for_auth(response.text)
        else:
            return False

    def view(self, user: str):
        """
        View the given user.
        """
        self._get(user, check_auth=True)

    def profile(self, user: str) -> Dict[str, Any]:
        """
        Get the profile information of the user.
        """
        response = self._get(user, check_auth=True)

        if "User not found." in response.text:
            raise APIError("user not found")

        parser = ProfileParser()
        data = parser.parse(response.text)

        return data

    def visitors(self) -> List[str]:
        """
        Get users who viewed your profile.
        """
        response = self._get("/app/views", check_auth=True)
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.find_all('div', class_='vBottomTxt')
        users = []
        for item in items:
            user = item.find('a')['href'][1:].split('?')[0]
            users.append(user)
        return users

    def search(self, options: dict, limit: int = 1000, 
               timeout: float = 0.0) -> Generator[str, None, None]:
        """
        Search for users according to the search `options`. The total number
        of users is `limit`. Since users are requested as pages, `timeout`
        is a timeout between page loading.
        """
        response = self._get("/app/search", check_auth=True)
        csrf_token = find_csrf_token(response.text)

        offset = 0
        params = self._prepare_search_params(options)
        params['csrf_token'] = csrf_token
        while True:
            params['offset'] = str(offset)

            response = self._get("/app/search", params, check_auth=True)
            users = self._parse_search_result(response.text)

            if not users:
                return

            for user in users:
                yield user
                offset += 1
                if offset >= limit:
                    return

            sleep(timeout)

    def get_uid(self, user: str) -> str:
        """
        Get unique user identifier `uid`.
        """
        profile_info = self.profile(user)
        return profile_info['uid']

    def get_thread_id(self, uid: str) -> str:
        """
        Get a chat thread_id with a user given as `uid`.
        """
        params = {'action': 'send', 'uid': uid}
        response = self._get("/pm.php", params)
        assert response.status_code == 301

        location = response.headers['Location']
        thread_id = parse_qs(urlparse(location).query)['thread_id'][0]

        return thread_id

    def chat(self, count: int = 9, offset: int = 0) -> Dict[str, Any]:
        """
        Get general chat information in count `count` with the offset `offset`.
        """
        chat_parser = ChatParser()

        response = self._get("/pm.php", check_auth=True)
        maxmsgid = chat_parser.parse_maxmsgid(response.text)
        unread = chat_parser.parse_unread(response.text)

        chats = []
        while len(chats) < count:
            params = {
                'action': 'more_threads',
                'from': str(offset),
                'filter': 'all',
                'max_msg_id': maxmsgid,
            }
            response = self._post("/pm.php", params)
            body = response.json()['body']

            items = chat_parser.parse_chat(body)
            if not items:
                break

            for item in items:
                chats.append(item)
                if len(chats) >= count:
                    break

            offset += len(items)

        return {
            'chats': chats,
            'unread': unread
        }

    def chat_messages(self, thread_id: str, 
                      last_msg_id: Optional[str] = None
                      ) -> List[Dict[str, Any]]:
        """
        Get chat messages by `thread_id` and `last_msg_id` (so history can be 
        loaded).
        """
        params = {
            'action': 'load_messages',
            'thread': thread_id
        }
        if last_msg_id:
            params['last_msg_id'] = last_msg_id

        response = self._post("/pm.php", params)
        body = response.json()['body']

        chat_parser = ChatParser()
        messages = chat_parser.parse_messages(body)

        return messages

    def chat_send(self, thread_id: str, message: str):
        """
        Send a new message into the `thread_id` that identifies the chat with
        the user.
        """
        params = {
            'action': 'send_message',
            'thread': thread_id,
            'message': message
        }
        response = self._post("/pm.php", params)
        assert '"error"' not in response.text, response.text

    def chat_delete(self, thread_id: str):
        """
        Delete the chat with `thread_id`.
        """
        params = {
            'action': 'delete_thread',
            'thread': thread_id,
            'block_user': '0'
        }
        self._post("/pm.php", params)

    def friends(self, uid: str) -> List[Dict[str, Any]]:
        """
        Get friends of the user given as `uid`.
        """
        url = "/app/friends?uid={}".format(uid)
        response = self._get(url, check_auth=True)
        friends_parser = FriendsParser()
        items = friends_parser.parse(response.text)
        return items

    def friend_add(self, uid: str):
        """
        Send friend request to the user given by `uid`.
        """
        url = "/app/friends/add?uid={}".format(uid)
        response = self._get(url)
        if response.status_code != 302:
            raise APIError("could not add user")

    def friend_remove(self, uid: str):
        """
        Remove friend given by `uid`.
        """
        url = "/app/friends/delete?uid={}".format(uid)
        response = self._get(url)
        if response.status_code != 302:
            raise APIError("could not delete user")

    def albums(self, uid: str) -> List[Dict[str, Any]]:
        """
        Get albums of the user given by `uid`.
        """
        response = self._get("/app/albums", {'uid': uid}, check_auth=True)
        pictures_parser = PicturesParser()
        items = pictures_parser.parse_albums(response.text)
        return items

    def pictures(self, uid: str, aid: str):
        """
        Get pictures of the user (given by `uid`) and his album (given by 
        `aid`).
        """
        response = self._get("/app/album", {'uid': uid, 'aid': aid}, 
                             check_auth=True)
        pictures_parser = PicturesParser()
        items = pictures_parser.parse_pictures(response.text)
        return items

    @classmethod
    def _get_full_url(cls, url, params=None):
        if not url.startswith("/"):
            url = "/" + url
        url = "https://{}{}".format(cls.host, url)
        if params is not None:
            url += '?' + urlencode(params, True)
        return url

    def _get(self, url, params=None, check_auth=False):
        headers = self._get_headers()
        if params is not None:
            url = url + '?' + urlencode(params, True)
        full_url = self._get_full_url(url)
        response = requests.get(full_url, headers=headers, timeout=self.timeout, 
                                allow_redirects=False)
        if check_auth and not self._check_body_for_auth(response.text):
            raise APIAuthError()
        return response

    def _post(self, url, params, check_auth=False):
        headers = self._get_headers()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        full_url = self._get_full_url(url)
        response = requests.post(full_url, data=params, headers=headers, 
                                 timeout=self.timeout, allow_redirects=False)
        if check_auth and not self._check_body_for_auth(response.text):
            raise APIAuthError()
        return response

    def _get_headers(self):
        cookie = Cookie()
        cookie.update(self._session.cookie())
        headers = {
            'Cookie': cookie.as_string(),
            'User-Agent': self.user_agent
        }
        return headers

    def _check_body_for_auth(self, body):
        return "/app/auth/logout" in body

    def _prepare_search_params(self, options):
        params = {
            'offset': '',
            'sort': 'last_login',
            'age1': options.get('age1', '16'),
            'age2': options.get('age2', '110'),
            'sex[]': options.get('sex', ['male', 'female']),
            'continents[]': options.get('continents', ['AF', 'AS', 'EU', 'NA', 
                                                       'OC', 'SA']),
            'countries[]': options.get('countries', ['---']),
            'languages[]': ['---'],
            'lfor[]': [
                'lfor_email', 'lfor_snail', 'lfor_langex',
                'lfor_friend', 'lfor_flirt', 'lfor_relation'
            ],
            'keywords': options.get('keywords', ''),
            'username': '',
            'csrf_token': 'ZjU1ZWZkM2Q=',
        }

        if options.get('online'):
            params['online'] = '1'

        if options.get('cityName'):
            citycode = options.get('city')
            cityname = options.get('cityName')
            if not citycode:
                citycode = self._get_citycode(cityname)
            params['city'] = citycode
            params['cityName'] = cityname

        return params

    def _parse_search_result(self, body):
        users = []
        soup = BeautifulSoup(body, "lxml")
        items = soup.find_all('div', class_='sResMain')
        for item in items:
            user = item.find('a').text
            users.append(user)
        return users

    def _get_citycode(self, cityname):
        response = self._get("/app/async/geoAc", {"query": cityname})
        data = response.json()
        return data['items'][0]['id']


class ApiAsync(Api):
    """
    Class for asynchronous API. It is inherited from [Api](#Api).
    """

    def __init__(self, session: SessionAsync):
        """
        Create an API instance.
        """
        self._session = session

    async def check_auth(self) -> bool:
        """
        Check whether the session is authorized.
        """
        if self._session:
            try:
                await self._request(self._session.username)
            except APIAuthError:
                return False
            else:
                return True
        else:
            return False

    async def view(self, user: str):
        """
        View the given user.
        """
        await self._request(user)

    async def profile(self, user: str) -> List[Dict[str, Any]]:
        """
        Get the profile information of the user.
        """
        html = await self._request(user)

        if "User not found." in html:
            raise APIError("User not found")

        if "Sorry, this user's privacy settings do not allow " \
                "you to contact them." in html:
            raise APIError("Blocked by user")

        parser = ProfileParser()
        data = parser.parse(html)

        return data

    async def visitors(self) -> List[str]:
        """
        Get users who viewed your profile.
        """
        html = await self._request("/app/views")
        soup = BeautifulSoup(html, "lxml")
        items = soup.find_all('div', class_='vBottomTxt')
        users = []
        for item in items:
            user = item.find('a')['href'].split('?')[0][1:]
            users.append(user)
        return users

    async def search(self, options: dict, limit: int = 1000, 
                     timeout: float = 0.0) -> Generator[str, None, None]:
        """
        Search for users according to the search `options`. The total number
        of users is `limit`. Since users are requested as pages, `timeout`
        is a timeout between page loading.
        """
        html = await self._request("/app/search")
        csrf_token = find_csrf_token(html)

        offset = 0
        params = self._prepare_search_params(options)
        params['csrf_token'] = csrf_token
        while True:
            params['offset'] = str(offset)

            html = await self._request("/app/search", params=params)
            users = self._parse_search_result(html)

            if not users:
                return

            for user in users:
                yield user
                offset += 1
                if offset >= limit:
                    return

            await asyncio.sleep(timeout)

    async def get_uid(self, user: str) -> str:
        """
        Get unique user identifier `uid`.
        """
        profile_info = await self.profile(user)
        return profile_info['uid']

    async def get_thread_id(self, uid: str) -> str:
        """
        Get a chat thread_id with a user given as `uid`.
        """
        params = {'action': 'send', 'uid': uid}

        try:
            await self._request("/pm.php", params=params)
        except APIRedirectError as exc:
            location = exc.args[1]
            thread_id = parse_qs(urlparse(location).query)['thread_id'][0]
            return thread_id
        else:
            raise APIError("Could not load thread_id")

    async def chat(self, count: int = 9, offset: int = 0) -> Dict[str, Any]:
        """
        Get general chat information in count `count` with the offset `offset`.
        """
        chat_parser = ChatParser()

        html = await self._request("/pm.php")
        maxmsgid = chat_parser.parse_maxmsgid(html)
        unread = chat_parser.parse_unread(html)

        chats = []
        while len(chats) < count:
            params = {
                'action': 'more_threads',
                'from': str(offset),
                'filter': 'all',
                'max_msg_id': maxmsgid,
            }

            text = await self._request("/pm.php", params=params, method='post', 
                                       check_auth=False)
            body = json.loads(text)['body']

            items = chat_parser.parse_chat(body)
            if not items:
                break

            for item in items:
                chats.append(item)
                if len(chats) >= count:
                    break

            offset += len(items)

        return {
            'chats': chats,
            'unread': unread
        }

    async def chat_messages(self, thread_id: str, 
                            last_msg_id: Optional[str] = None
                            ) -> List[Dict[str, Any]]:
        """
        Get chat messages by `thread_id` and `last_msg_id` (so history can be 
        loaded).
        """
        params = {
            'action': 'load_messages',
            'thread': thread_id
        }
        if last_msg_id:
            params['last_msg_id'] = last_msg_id

        text = await self._request("/pm.php", params=params, method='post', 
                                   check_auth=False)
        body = json.loads(text)['body']

        chat_parser = ChatParser()
        messages = chat_parser.parse_messages(body)

        return messages

    async def chat_send(self, thread_id: str, message: str):
        """
        Send a new message into the `thread_id` that identifies the chat with
        the user.
        """
        params = {
            'action': 'send_message',
            'thread': thread_id,
            'message': message
        }
        text = await self._request("/pm.php", params=params, method='post', 
                                   check_auth=False)
        if '"error"' in text:
            raise APIError(text)

    async def chat_delete(self, thread_id: str):
        """
        Delete the chat with `thread_id`.
        """
        params = {
            'action': 'delete_thread',
            'thread': thread_id,
            'block_user': '0'
        }
        await self._request("/pm.php", params=params, method='post', 
                            check_auth=False)

    async def friends(self, uid: str) -> List[Dict[str, Any]]:
        """
        Get friends of the user given as `uid`.
        """
        url = "/app/friends?uid={}".format(uid)
        html = await self._request(url)
        friends_parser = FriendsParser()
        items = friends_parser.parse(html)
        return items

    async def friend_add(self, uid: str):
        """
        Send friend request to the user given by `uid`.
        """
        url = "/app/friends/add?uid={}".format(uid)
        try:
            await self._request(url)
        except APIRedirectError:
            pass
        else:
            raise APIError("Could not add friend")

    async def friend_remove(self, uid: str):
        """
        Remove friend given by `uid`.
        """
        url = "/app/friends/delete?uid={}".format(uid)
        try:
            await self._request(url)
        except APIRedirectError:
            pass
        else:
            raise APIError("Could not delete friend")

    async def albums(self, uid: str) -> List[Dict[str, Any]]:
        """
        Get albums of the user given by `uid`.
        """
        html = await self._request("/app/albums", params={'uid': uid})
        pictures_parser = PicturesParser()
        items = pictures_parser.parse_albums(html)
        return items

    async def pictures(self, uid: str, aid: str):
        """
        Get pictures of the user (given by `uid`) and his album (given by 
        `aid`).
        """
        html = await self._request("/app/album", 
                                   params={'uid': uid, 'aid': aid})
        pictures_parser = PicturesParser()
        items = pictures_parser.parse_pictures(html)
        return items

    async def _request(self, url, method='get', params=None, check_auth=True):
        assert method in ('get', 'post')

        full_url = self._get_full_url(url, params if method == 'get' else None)
        headers = self._get_headers()

        if method == 'post':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        kwargs = {
            'url': full_url,
            'headers': headers,
            'timeout': self.timeout,
            'allow_redirects': False,
        }

        if method == 'post':
            kwargs['data'] = params

        async with aiohttp.ClientSession() as session:
            request_func = session.post if method == 'post' else session.get
            async with request_func(**kwargs) as resp:
                if resp.status in (301, 302):
                    raise APIRedirectError(
                        resp.status, resp.headers['Location']
                    )
                body = await resp.text()

        if check_auth and not self._check_body_for_auth(body):
            raise APIAuthError()
        
        return body
