import os
from unittest import TestCase

from interpals_api.parsers.profile import ProfileParser
from interpals_api.parsers.userdata import UserDataParser
from interpals_api.parsers.pictures import AlbumsParser, PicturesParser

from .common import ensure_session_sync, ensure_html_sync


TEST_INTERPALS_UID = int(os.getenv('TEST_INTERPALS_UID', '0'))
TEST_INTERPALS_USERNAME = os.getenv('TEST_INTERPALS_USERNAME')


class TestParsers(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = ensure_session_sync()
        cls.profile_html = ensure_html_sync(
            TEST_INTERPALS_USERNAME, cls.session
        )
        cls.visitors_html = ensure_html_sync("/app/views", cls.session)
        cls.albums_html = ensure_html_sync(
            f"/app/albums?uid={TEST_INTERPALS_UID}", cls.session
        )

    def test_profile(self):
        profile = ProfileParser().parse(self.profile_html)
        self.assertEqual(profile.username, TEST_INTERPALS_USERNAME)
        self.assertEqual(profile.uid, TEST_INTERPALS_UID)

    def test_visitors(self):
        users = UserDataParser().parse(self.visitors_html)
        self.assertTrue(users)

    def test_pictures(self):
        albums = AlbumsParser().parse(self.albums_html)
        self.assertTrue(albums)

        aid = albums[0].aid
        pictures_html = ensure_html_sync(
            f"/app/album?aid={aid}&uid={TEST_INTERPALS_UID}", self.session
        )

        pictures = PicturesParser().parse(pictures_html)
        self.assertTrue(pictures)

        self.assertEqual(albums[0].pics_num, len(pictures))
