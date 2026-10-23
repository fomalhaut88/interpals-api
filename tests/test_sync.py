import os
from unittest import TestCase

from interpals_api.api import ApiSync
from interpals_api.schemas import SearchOptions

from .common import ensure_session_sync


TEST_INTERPALS_UID = int(os.getenv('TEST_INTERPALS_UID', '0'))
TEST_INTERPALS_USERNAME = os.getenv('TEST_INTERPALS_USERNAME')


class TestSync(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = ensure_session_sync()
        cls.api = ApiSync(cls.session)

    def test_check_auth(self):
        self.assertTrue(self.api.check_auth())

    def test_get_uid(self):
        self.assertTrue(self.api.get_uid())
        self.assertTrue(self.api.get_uid(TEST_INTERPALS_USERNAME))

    def test_profile(self):
        profile = self.api.profile(TEST_INTERPALS_USERNAME)
        self.assertEqual(profile.username, TEST_INTERPALS_USERNAME)
        self.assertEqual(profile.uid, TEST_INTERPALS_UID)

    def test_visitors(self):
        self.assertTrue(self.api.visitors())

    def test_pictures(self):
        albums = self.api.albums(TEST_INTERPALS_UID)
        self.assertTrue(albums)

        aid = albums[0].aid

        pictures = self.api.pictures(TEST_INTERPALS_UID, aid)
        self.assertTrue(pictures)

        self.assertEqual(albums[0].pics_num, len(pictures))

    def test_get_citycode(self):
        self.assertEqual(self.api.get_citycode("Moscow"), 524901)
        self.assertEqual(self.api.get_citycode("Fethiye"), 314967)

    def test_search(self):
        options = SearchOptions()
        users = list(self.api.search(options, limit=5))
        self.assertTrue(users)
