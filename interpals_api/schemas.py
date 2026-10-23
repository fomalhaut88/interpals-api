"""
Schemas used in the library.
"""

from typing import Literal
from dataclasses import dataclass, field


@dataclass
class ProfileInfo:
    """
    Information line in the profile.
    """

    title: str
    text: str


@dataclass
class Profile:
    """
    User profile structure.
    """

    uid: int
    username: str

    name: str | None = None
    age: int | None = None
    sex: Literal['male', 'female'] | None = None

    country: str | None = None
    country_code: str | None = None
    city: str | None = None
    city_code: int | None = None

    last_online: str | None = None
    joined: str | None = None
    updated: str | None = None

    status: str | None = None
    avatar: str | None = None

    info: list[ProfileInfo] | None = None


@dataclass
class Album:
    """
    Album structure.
    """

    aid: int
    name: str
    pics_num: int


@dataclass
class Picture:
    """
    Picture structure.
    """

    small: str
    large: str


@dataclass
class SearchOptions:
    """
    Search options.
    """

    age1: int = 16
    age2: int = 110
    sex: list[Literal['male', 'female']] = field(
        default_factory=lambda: ['male', 'female']
    )
    continents: list[Literal['AF', 'AS', 'EU', 'NA', 'OC', 'SA']] = field(
        default_factory=lambda: ['AF', 'AS', 'EU', 'NA', 'OC', 'SA']
    )
    countries: list[str] = field(default_factory=lambda: ['---'])
    keywords: str = ''
    online: bool = False
    city_code: int | None = None
    city_name: str | None = None
