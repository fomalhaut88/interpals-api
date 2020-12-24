from urllib.parse import urlencode, urlparse, parse_qs
from time import sleep

import requests
from bs4 import BeautifulSoup

from .cookie import Cookie
from .utils import find_csrf_token
from .parsers.profile_parser import ProfileParser
from .parsers.chat_parser import ChatParser
from .parsers.friends_parser import FriendsParser
from .parsers.pictures_parser import PicturesParser


class ApiError(Exception):
    pass


class ApiTimeoutError(ApiError):
    pass


class ApiAuthError(ApiError):
    pass


class Api:
    timeout = 3.0
    host = "www.interpals.net"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"

    def __init__(self, session):
        self._session = session

    def check_auth(self):
        if self._session:
            response = self._get(self._session.username)
            return self._check_body_for_auth(response.text)
        else:
            return False

    def view(self, user):
        self._get(user, check_auth=True)

    def profile(self, user):
        response = self._get(user, check_auth=True)

        if "User not found." in response.text:
            raise ApiError("user not found")

        parser = ProfileParser()
        data = parser.parse(response.text)

        return data

    def visitors(self):
        response = self._get("/app/views", check_auth=True)
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.find_all('div', class_='vBottomTxt')
        users = []
        for item in items:
            user = item.find('a')['href'][1:]
            users.append(user)
        return users

    def search(self, options, limit=1000, timeout=0.0):
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

    def get_uid(self, user):
        profile_info = self.profile(user)
        return profile_info['uid']

    def get_thread_id(self, uid):
        params = {'action': 'send', 'uid': uid}
        response = self._get("/pm.php", params)
        assert response.status_code == 301

        location = response.headers['Location']
        thread_id = parse_qs(urlparse(location).query)['thread_id'][0]

        return thread_id

    def chat(self, count=9, offset=0):
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

    def chat_messages(self, thread_id, last_msg_id=None):
        params = {
            'thread_id': thread_id,
            'view': "paged",
            'page': 1
        }
        if last_msg_id:
            params['last_msg_id'] = last_msg_id

        response = self._get("/pm.php", params)
        body = response.text

        chat_parser = ChatParser()

        number_pages = chat_parser.parse_number_pages(body)

        if number_pages > 10:
            print("Found %d pages, parsing will take a moment." % number_pages)
        
        messages = list()
        for i in range(1, number_pages+1):
            params["page"] = i
            response = self._get("/pm.php", params)
            body = response.text
            messages += chat_parser.parse_messages(body)

        return messages

    def chat_send(self, thread_id, message):
        params = {
            'action': 'send_message',
            'thread': thread_id,
            'message': message
        }
        response = self._post("/pm.php", params)
        assert '"error"' not in response.text, response.text

    def chat_delete(self, thread_id):
        params = {
            'action': 'delete_thread',
            'thread': thread_id,
            'block_user': '0'
        }
        self._post("/pm.php", params)

    def friends(self, uid):
        url = "/app/friends?uid={}".format(uid)
        response = self._get(url, check_auth=True)
        friends_parser = FriendsParser()
        items = friends_parser.parse(response.text)
        return items

    def friend_add(self, uid):
        url = "/app/friends/add?uid={}".format(uid)
        response = self._get(url)
        if response.status_code == 302:
            raise ApiError("could not add user")
        csrf_token = find_csrf_token(response.text)
        params = {
            'uid': uid,
            'todo': 'submit_request',
            'csrf_token': csrf_token
        }
        self._post("/app/friends/submit", params)

    def friend_remove(self, uid):
        response = self._get("/app/friends", check_auth=True)
        csrf_token = find_csrf_token(response.text)
        params = {
            'target_id': uid,
            'online': '',
            'csrf_token': csrf_token
        }
        self._post("/app/friends/delete", params)

    def albums(self, uid):
        response = self._get("/app/albums", {'uid': uid}, check_auth=True)
        pictures_parser = PicturesParser()
        items = pictures_parser.parse_albums(response.text)
        return items

    def pictures(self, uid, aid):
        response = self._get("/app/album", {'uid': uid, 'aid': aid}, check_auth=True)
        pictures_parser = PicturesParser()
        items = pictures_parser.parse_pictures(response.text)
        return items

    @classmethod
    def _get_full_url(cls, url):
        if not url.startswith("/"):
            url = "/" + url
        return "https://{}{}".format(cls.host, url)

    def _get(self, url, params=None, check_auth=False):
        headers = self._get_headers()
        if params is not None:
            url = url + '?' + urlencode(params, True)
        full_url = self._get_full_url(url)
        response = requests.get(full_url, headers=headers, timeout=self.timeout, allow_redirects=False)
        if check_auth and not self._check_body_for_auth(response.text):
            raise ApiAuthError()
        return response

    def _post(self, url, params, check_auth=False):
        headers = self._get_headers()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        full_url = self._get_full_url(url)
        response = requests.post(full_url, data=params, headers=headers, timeout=self.timeout, allow_redirects=False)
        if check_auth and not self._check_body_for_auth(response.text):
            raise ApiAuthError()
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
            'continents[]': options.get('continents', ['AF', 'AS', 'EU', 'NA', 'OC', 'SA']),
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
