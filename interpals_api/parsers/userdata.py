"""
Parser for short user data that is usually stored in `data-react-data` JSON.
"""

from ..errors import ParseError
from ..schemas import Profile
from ..utils import find_react_data


class UserDataParser:
    """
    Parser for user profiles.
    """

    def parse(self, html: str) -> list[Profile]:
        """
        Parse HTML content into a list of Profile objects.
        """
        data = find_react_data(html)
        if data is None:
            raise ParseError("data-react-data")
        return [
            Profile(
                uid=int(row['id']),
                username=row['username'],
                sex=row['sex'],
                age=int(row['age']),
                name=row['displayName'],
                avatar=row['avatarUrl'],
            )
            for row in data['rows']
        ]
