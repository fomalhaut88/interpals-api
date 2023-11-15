class Cookie(dict):
    """
    A class that manages HTTP cookies.
    """

    def as_string(self):
        """
        Represents saves cookie values as a string for HTTP header.
        """
        return "; ".join(
            "{}={}".format(key, value) for key, value in self.items()
        )

    def __repr__(self):
        return self.as_string()

    @classmethod
    def parse_set_cookie(cls, set_cookie):
        """
        Extracts key and value of a cookie from Set-Cookie header of an HTTP response.
        """
        key, value = set_cookie[:set_cookie.find(';')].split('=')
        key = key.strip()
        value = value.strip()
        return key, value

    @classmethod
    def from_response_headers(cls, headers):
        """
        Creates cookie instance from HTTP response headers.
        """
        obj = cls()
        for key, value in headers.items():
            if key.lower() == "set-cookie":
                for val in value.split("HttpOnly,"):
                    cookie_key, cookie_value = cls.parse_set_cookie(val)
                    obj[cookie_key] = cookie_value
        return obj
