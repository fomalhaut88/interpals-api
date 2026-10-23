import os
from unittest import IsolatedAsyncioTestCase

from interpals_api.api import ApiAsync
from interpals_api.schemas import SearchOptions

from .common import ensure_session_sync


TEST_INTERPALS_UID = int(os.getenv('TEST_INTERPALS_UID', '0'))
TEST_INTERPALS_USERNAME = os.getenv('TEST_INTERPALS_USERNAME')


class TestAsync(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = ensure_session_sync()
        cls.api = ApiAsync(cls.session)

    async def test_check_auth(self):
        self.assertTrue(await self.api.check_auth())

    async def test_get_uid(self):
        self.assertTrue(await self.api.get_uid())
        self.assertTrue(await self.api.get_uid(TEST_INTERPALS_USERNAME))

    async def test_profile(self):
        profile = await self.api.profile(TEST_INTERPALS_USERNAME)
        self.assertEqual(profile.username, TEST_INTERPALS_USERNAME)
        self.assertEqual(profile.uid, TEST_INTERPALS_UID)

    async def test_visitors(self):
        self.assertTrue(await self.api.visitors())

    async def test_pictures(self):
        albums = await self.api.albums(TEST_INTERPALS_UID)
        self.assertTrue(albums)

        aid = albums[0].aid

        pictures = await self.api.pictures(TEST_INTERPALS_UID, aid)
        self.assertTrue(pictures)

        self.assertEqual(albums[0].pics_num, len(pictures))

    async def test_get_citycode(self):
        self.assertEqual(await self.api.get_citycode("Moscow"), 524901)
        self.assertEqual(await self.api.get_citycode("Fethiye"), 314967)

    async def test_search(self):
        options = SearchOptions()
        users = []
        async for user in self.api.search(options, limit=5):
            users.append(user)
        self.assertTrue(users)
