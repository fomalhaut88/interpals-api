"""
A simple class for Cookie support. It keeps cookie data as a dictionary and has
special functions to convert from and into strings and to parse 'Set-Cookie'
header.
"""

from typing import Self


class Cookie:
    """
    A simple class that manages HTTP cookies. It keeps the data in an inner
    dictionary, so most typical dictionary operations are supported.
    Use `str()` to convert cookie object into a string that can be used in
    HTTP request header `Cookie`.
    """

    def __init__(self, dct: dict[str, str] = {}):
        self._data = dct.copy()

    def __repr__(self) -> str:
        return "; ".join(
            f"{key}={value}" for key, value in self._data.items()
        )

    def __getitem__(self, key: str) -> str:
        return self._data[key]

    def __setitem__(self, key: str, value: str):
        self._data[key] = value

    def __delitem__(self, key: str):
        del self._data[key]

    def as_dict(self) -> dict[str, str]:
        """
        Represent cookie as a dictionary.
        """
        return self._data

    def clear(self):
        """
        Clear all data.
        """
        self._data.clear()

    def update(self, dct: dict[str, str]):
        """
        Update cookie with the dictionary.
        """
        self._data.update(dct)

    def update_from_headers(self, headers: list[tuple[str, str]]):
        """
        Update cookie from the HTTP response headers.
        """
        for hdr_key, hdr_value in headers:
            if hdr_key.lower().strip() == 'set-cookie':
                key, value = self.parse_set_cookie(hdr_value)
                self._data[key] = value

    def copy(self) -> Self:
        """
        Copy cookie object.
        """
        return self.__class__(self._data)

    @classmethod
    def parse_set_cookie(cls, set_cookie: str) -> tuple[str, str]:
        """
        Extract key and value of a cookie from Set-Cookie header of an HTTP
        response.
        """
        end = set_cookie.find(';')
        key, value = set_cookie[:end].split('=', 1)
        return key.strip(), value.strip()
