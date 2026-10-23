from unittest import TestCase

from interpals_api.cookie import Cookie


class TestCookie(TestCase):
    def test_base(self):
        cookie = Cookie()
        self.assertDictEqual(cookie.as_dict(), {})
        self.assertEqual(str(cookie), "")

        cookie["a"] = "25"
        cookie["b"] = "36"
        cookie["c"] = "47"
        self.assertDictEqual(
            cookie.as_dict(), {"a": "25", "b": "36", "c": "47"}
        )
        self.assertEqual(str(cookie), "a=25; b=36; c=47")

        del cookie["b"]
        self.assertDictEqual(cookie.as_dict(), {"a": "25", "c": "47"})

        cookie.update({"a": "14", "d": "58"})
        self.assertDictEqual(
            cookie.as_dict(), {"a": "14", "c": "47", "d": "58"}
        )

        cookie_copy = cookie.copy()

        cookie.clear()
        self.assertDictEqual(cookie.as_dict(), {})

        self.assertDictEqual(
            cookie_copy.as_dict(), {"a": "14", "c": "47", "d": "58"}
        )

    def test_parse_set_cookie(self):
        self.assertEqual(
            Cookie.parse_set_cookie(
                '__ubic1=JqeH5LWVJNV0SGZd; '
                'expires=Thu, 21 Oct 2027 20:56:06 GMT; '
                'Max-Age=31556952; path=/; '
                'domain=interpals.net; HttpOnly'
            ),
            ("__ubic1", "JqeH5LWVJNV0SGZd")
        )

    def test_update_from_headers(self):
        headers = [
            ('access-control-allow-origin', 'https://interpals.net'),
            ('access-control-expose-headers', 'Retry-After'),
            ('alt-svc', 'h3=":443"; ma=86400'),
            ('cache-control', 'no-store, no-cache, must-revalidate'),
            ('cache-control', 'no-cache, private'),
            ('cf-cache-status', 'DYNAMIC'),
            ('cf-ray', 'a4e12b378d95bbdd-FRA'),
            ('content-type', 'text/html; charset=utf-8'),
            ('date', 'Wed, 21 Oct 2026 15:06:54 GMT'),
            ('expires', 'Thu, 19 Nov 1981 08:52:00 GMT'),
            ('location', '/'),
            ('nel', '{"report_to":"cf-nel","success_fraction":0.0,'
                    '"max_age":604800}'),
            ('pragma', 'no-cache'),
            ('priority', 'u=0,i'),
            ('report-to', '{"group":"cf-nel","max_age":604800,'
                          '"endpoints":[{"url":"https://a.nel.cloudflare.com'
                          '/report/v4?s=XsU5YrPtu93QSAagZELwacXi1yPawvk3OtnM'
                          'gU3s9ltUO0wA82bM1cTXb66RfPiv%2FbIRVJy%2B2dlFAgejF'
                          'nUaWcQtL16lmsieOdDQ7iwPZ%2FzmJvi4ZZ4MIt%2B2DyVv8h'
                          'QWugn2E6VliVhA368%3D"}]}'),
            ('server', 'cloudflare'),
            ('server-timing', 'cfExtPri'),
            ('set-cookie', '__ubic1=JqeH5LWVJNV0SGZd; '
                           'expires=Thu, 21 Oct 2027 20:56:06 GMT; '
                           'Max-Age=31556952; path=/; '
                           'domain=interpals.net; HttpOnly'),
            ('set-cookie', 'csrf_cookieV2=tIDlGVPKRrE%3D; '
                           'expires=Tue, 19 Jan 2027 15:06:54 GMT; '
                           'Max-Age=7776000; path=/; secure; HttpOnly; '
                           'SameSite=Lax'),
            ('set-cookie', 'interpals_sessid=deleted; '
                           'expires=Thu, 01 Jan 1970 00:00:01 GMT; '
                           'Max-Age=0; path=/; domain=interpals.net'),
            ('set-cookie', 'interpals_sessid=deleted; '
                           'expires=Thu, 01 Jan 1970 00:00:01 GMT; '
                           'Max-Age=0; path=/'),
            ('set-cookie', 'oauth_signin_nonce=deleted; '
                           'expires=Thu, 01 Jan 1970 00:00:01 GMT; '
                           'Max-Age=0; path=/; domain=interpals.net'),
            ('set-cookie', 'oauth_signin_nonce=deleted; '
                           'expires=Thu, 01 Jan 1970 00:00:01 GMT; '
                           'Max-Age=0; path=/'),
            ('set-cookie', 'lt=deleted; '
                           'expires=Thu, 01 Jan 1970 00:00:01 GMT; '
                           'Max-Age=0; path=/; domain=interpals.net'),
            ('set-cookie', 'lt=deleted; '
                           'expires=Thu, 01 Jan 1970 00:00:01 GMT; '
                           'Max-Age=0; path=/'),
            ('set-cookie', 'fbnl=1; '
                           'expires=Thu, 22 Oct 2026 15:06:54 GMT; '
                           'Max-Age=86400; path=/; domain=interpals.net'),
            ('strict-transport-security', 'max-age=604800'),
            ('vary', 'Origin'),
            ('via', '1.1 google'),
        ]
        cookie = Cookie()
        cookie.update_from_headers(headers)
        self.assertDictEqual(
            cookie.as_dict(),
            {
                '__ubic1': 'JqeH5LWVJNV0SGZd',
                'csrf_cookieV2': 'tIDlGVPKRrE%3D',
                'interpals_sessid': 'deleted',
                'oauth_signin_nonce': 'deleted',
                'lt': 'deleted',
                'fbnl': '1',
            }
        )
        self.assertEqual(
            str(cookie),
            "__ubic1=JqeH5LWVJNV0SGZd; "
            "csrf_cookieV2=tIDlGVPKRrE%3D; "
            "interpals_sessid=deleted; "
            "oauth_signin_nonce=deleted; "
            "lt=deleted; "
            "fbnl=1",
        )
