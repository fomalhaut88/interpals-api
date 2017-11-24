from bs4 import BeautifulSoup


class FriendsParser:
    def parse(self, content):
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
