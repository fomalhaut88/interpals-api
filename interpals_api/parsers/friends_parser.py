"""
Parser for user friends.
"""

from typing import List, Dict, Any

from bs4 import BeautifulSoup


class FriendsParser:
    """
    Friends parser:

    ```python
    parser = FriendsParser()
    data = parser.parse(html)
    ```
    """

    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse HTML content and return list of friends as dictionaries having
        username, age, city, online status and avatar URL.
        """
        soup = BeautifulSoup(content, "lxml")

        boxes = soup.find_all('div', class_='friendBox')
        friends = []
        for box in boxes:
            friend = {}
            friend.update(self._parse_user_info(box))
            friend.update(self._parse_avatar(box))
            friend.update(self._parse_online(box))
            friends.append(friend)

        return friends

    def _parse_avatar(self, box):
        avatar = 'https:' + box.img['src']
        return {'avatar': avatar}

    def _parse_user_info(self, box):
        src = box.find('img', class_='status')['src']
        online = 'online' in src
        return {'online': online}

    def _parse_online(self, box):
        username, age, city, *extra = box.text.strip().split()
        return {
            'user': username,
            'age': age,
            'city': city
        }
