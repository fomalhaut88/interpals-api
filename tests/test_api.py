import unittest as ut

from interpals_api.session import Session, SessionError
from interpals_api.api import Api


class TestApi(ut.TestCase):
    def setUp(self):
        with open('test-config.txt') as f:
            username, password = f.readlines()
        self.interpals_auth = {
            'username': username,
            'password': password,
        }

    def test_login(self):
        session = Session.login(**self.interpals_auth)
        self.assertTrue(session)

        with self.assertRaises(SessionError) as context:
            Session.login(username='ijvnpe', password='evboqervb')
        self.assertEqual(context.exception.args[0], "Wrong username or password")

    def test_search(self):
        options = {
            'age1': 18,
            'age2': 30,
            'sex': ['male', 'female'],
            'countries': ['US', 'RU'],
            'online': True,
        }

        session = Session.login(**self.interpals_auth)
        api = Api(session)
        users = list(api.search(options, limit=10))

        self.assertEqual(len(users), 10)
