import os
from unittest import TestCase, IsolatedAsyncioTestCase

from interpals_api.session import login_sync, login_async
from interpals_api.errors import WrongUsernameOrPasswordError


TEST_SESSION_PATH = "./test.session"

INTERPALS_USERNAME = os.getenv('INTERPALS_USERNAME')
INTERPALS_PASSWORD = os.getenv('INTERPALS_PASSWORD')


class TestSessionSync(TestCase):
    def test_success(self):
        session = login_sync(INTERPALS_USERNAME, INTERPALS_PASSWORD)
        self.assertEqual(session.username, INTERPALS_USERNAME)
        self.assertTrue(session.interpals_sessid)
        self.assertTrue(session.csrf_cookieV2)

    def test_unsuccess(self):
        with self.assertRaises(WrongUsernameOrPasswordError):
            login_sync(INTERPALS_USERNAME, "qweRTY123")


class TestSessionAsync(IsolatedAsyncioTestCase):
    async def test_success(self):
        session = await login_async(INTERPALS_USERNAME, INTERPALS_PASSWORD)
        self.assertEqual(session.username, INTERPALS_USERNAME)
        self.assertTrue(session.interpals_sessid)
        self.assertTrue(session.csrf_cookieV2)

    async def test_unsuccess(self):
        with self.assertRaises(WrongUsernameOrPasswordError):
            await login_async(INTERPALS_USERNAME, "qweRTY123")
