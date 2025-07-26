"""
Parser for general profile data of a user. It includes gender, location,
online, join date, status message, avatar URL, uid number and the description.
"""

from typing import Dict, Any

from bs4 import BeautifulSoup


class ProfileParser:
    """
    Parser class.

    ```python
    parser = ProfileParser()
    data = parser.parse(html)
    ```
    """

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse HTML content and return the data as a dictionary.
        """
        soup = BeautifulSoup(content, "lxml")

        data = {}

        data.update(self._extract_name_age_sex(soup))
        data.update(self._extract_location(soup))
        data.update(self._extract_online(soup))
        data.update(self._extract_joined_updated(soup))
        data.update(self._extract_status(soup))
        data.update(self._extract_avatar(soup))
        data.update(self._extract_uid(soup))
        data.update(self._extract_info(soup))

        return data

    def _extract_name_age_sex(self, soup):
        profile_box = soup.find(class_='profileBox')

        sex = profile_box.find('img')['src'].split('/')[-1][:-7]

        pieces = profile_box.text.split('\n')
        pieces = list(map(str.strip, pieces))
        pieces = list(filter(lambda s: s, pieces))
        piece = pieces[1]
        piece = piece.replace('y.o.', '')
        na = piece.split(', ')
        if len(na) == 2:
            name, age = na
        else:
            if na.isdigit():
                name, age = None, na
            else:
                name, age = na, None
        age = int(age)

        return {'name': name, 'age': age, 'sex': sex}

    def _extract_location(self, soup):
        links = soup.find(class_='profLocation').find_all('a')
        city = links[1].text
        city_code = links[1]['href'].split('=')[-1]
        country = links[2].text
        country_code = links[2]['href'][-2:]
        return {
            'city': city,
            'city_code': city_code,
            'country': country,
            'country_code': country_code
        }

    def _extract_online(self, soup):
        text = soup.find(class_='profOnlineStatus').text.strip()
        if text.lower() == "online now":
            online = True
            last = None
        else:
            online = False
            last = ' '.join(text.split()[1:])
        return {'online': online, 'last': last}

    def _extract_joined_updated(self, soup):
        text = soup.find(class_='profileBox').find_all('p')[0].text.strip()
        joined, updated = text.split('\n')[1::2]
        joined = joined[:-1]
        updated = updated[:-1]
        return {'joined': joined, 'updated': updated}

    def _extract_status(self, soup):
        element = soup.find('span', id='prStatMsgTxt')
        status = element.text if element else ''
        return {'status': status}

    def _extract_avatar(self, soup):
        avatar_link = soup.find('a', class_='mainPhoto')
        if not avatar_link:
            avatar_link = soup.find('a', class_='mpImgLink')
        avatar = 'https:' + avatar_link.find('img')['src']
        return {'avatar': avatar}

    def _extract_uid(self, soup):
        report_link = soup.find('a', class_='profReportLink')
        if report_link:
            uid = report_link['user-id']
        else:
            uid = soup.find('div', class_='hidden-uid').text
        return {'uid': uid}

    def _extract_info(self, soup):
        box = soup.find(class_='profDataBox')
        titles = box.find_all('h2')
        texts = box.find_all('div', class_='profDataBoxText')
        info = []
        for title, text in zip(titles, texts):
            title = title.text.strip()
            text = text.text.strip()
            info.append({
                'title': title,
                'text': text
            })
        return {'info': info}
