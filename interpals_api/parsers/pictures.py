"""
Parser for user pictures. It supports the album structure.
"""

from ..errors import ParseError
from ..schemas import Album, Picture
from ..utils import find_react_data


class AlbumsParser:
    """
    Parser for user album.
    """

    def parse(self, html: str) -> list[Album]:
        """
        Parse HTML content into an Album object.
        """
        data = find_react_data(html)
        if data is None:
            raise ParseError("data-react-data")
        return [
            Album(
                aid=int(row['id']),
                name=row['title'],
                pics_num=int(row['photoCountText'].split()[0]),
            )
            for row in data['cards']
        ]


class PicturesParser:
    """
    Parser for user pictures.
    """

    def parse(self, html: str) -> list[Picture]:
        """
        Parse HTML content into a list of Picture objects.
        """
        data = find_react_data(html)
        if data is None:
            raise ParseError("data-react-data")
        return [
            Picture(
                small=row['thumbUrl'],
                large=self._large_photo(row['thumbUrl']),
            )
            for row in data['tiles']
        ]

    @classmethod
    def _large_photo(cls, small: str) -> str:
        url = small.replace('/thumbs/300x300/', '/photos/')
        if '?' in url:
            url = url[:url.find('?')]
        return url
