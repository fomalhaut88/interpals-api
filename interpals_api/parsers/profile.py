"""
Parser for general profile data of a user. It includes gender, location,
online, join date, status message, avatar URL, uid number and the description.
"""

import re
import json

from ..errors import ParseError
from ..utils import parse_uid
from ..schemas import Profile, ProfileInfo


class ProfileParser:
    """
    Parser for user profile.
    """

    _regex_page_hdr = re.compile(
        r'<h1 .*?>(.*?)</h1>.*?<span.*?>(.*?)</span>', flags=re.DOTALL
    )
    _regex_main_content = re.compile(
        r'<script type="application/ld\+json">(.*?)</script>'
    )
    _regex_location = re.compile(
        r'<a href="/app/search\?todo=search&city=(\d+)".*?>(.*?)</a>,\s*'
        r'<a href="/country/([A-Z]{2})".*?>(.*?)</a>', flags=re.DOTALL
    )
    _regex_joined_updated = re.compile(
        r'Joined (.*?) ago, profile updated (.*?) ago'
    )
    _regex_status = re.compile(
        r'<i class="fa fa-quote-left text-gray-400 mr-1"></i>(.*?)</div>',
        flags=re.DOTALL
    )
    _regex_avatar = re.compile(
        r'<img [^>]*src="([^"]*?)(\?[^"]*?)?"[^>]*?main profile photo[^>]*?>',
        flags=re.DOTALL
    )
    _regex_info = re.compile(
        r'<h2[^>]*?>\s*<i[^>]*?></i>(.*?)</h2>\s*'
        r'<div[^>]*?>\s*<div[^>]*?>(.*?)</div>', flags=re.DOTALL
    )

    def parse(self, html: str) -> Profile:
        """
        Parse HTML content into a Profile object.
        """
        uid = parse_uid(html)

        if uid is None:
            raise ParseError("uid")

        if match := self._regex_page_hdr.search(html):
            username = match.group(1).strip().split(None, 1)[0]
            name_str, age_str = (
                match.group(2).replace('&nbsp;', ' ').strip().split(',', 1)
            )
            name = name_str.strip()
            age = int(age_str.split(None, 1)[0])
        else:
            raise ParseError("username")

        profile = Profile(uid=uid, username=username, name=name, age=age)

        self._augment_sex(profile, html)
        self._augment_location(profile, html)
        self._augment_online(profile, html)
        self._augment_joined_updated(profile, html)
        self._augment_status(profile, html)
        self._augment_avatar(profile, html)
        self._augment_info(profile, html)

        return profile

    def _augment_sex(self, profile: Profile, html: str):
        # TODO: Some pages lack this JSON, so we need a better way to extract
        # the gender.
        if match := self._regex_main_content.search(html):
            data = json.loads(match.group(1))
            profile.sex = (
                data['mainEntity']['gender'].rsplit('/', 1)[1].lower()
            )

    def _augment_location(self, profile: Profile, html: str):
        if match := self._regex_location.search(html):
            profile.city_code = int(match.group(1))
            profile.city = match.group(2)
            profile.country_code = match.group(3)
            profile.country = match.group(4)

    def _augment_online(self, profile: Profile, html: str):
        html_lower = html.lower()
        if 'online now' in html_lower:
            profile.last_online = 'now'
        else:
            ix = html_lower.find('last online')
            end = html_lower[ix:].find('<')
            profile.last_online = html[ix + 11:ix + end].strip() + ' ago'

    def _augment_joined_updated(self, profile: Profile, html: str):
        if match := self._regex_joined_updated.search(html):
            profile.joined = match.group(1).strip() + ' ago'
            profile.updated = match.group(2).strip() + ' ago'

    def _augment_status(self, profile: Profile, html: str):
        if match := self._regex_status.search(html):
            profile.status = match.group(1).strip()

    def _augment_avatar(self, profile: Profile, html: str):
        if match := self._regex_avatar.search(html):
            profile.avatar = match.group(1)

    def _augment_info(self, profile: Profile, html: str):
        profile.info = []
        for title, text in self._regex_info.findall(html):
            title = title.strip()
            text = re.sub(r'<[^>]*?>', '', text).strip()
            profile.info.append(ProfileInfo(title=title, text=text))
