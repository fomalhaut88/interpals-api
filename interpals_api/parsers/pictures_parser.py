from bs4 import BeautifulSoup


class PicturesParser:
    def parse_albums(self, content):
        soup = BeautifulSoup(content, "lxml")

        elements = soup.find_all('div', class_='editAlbumBox')
        albums = []
        for element in elements:
            album = {}
            album.update(self._parse_aid(element))
            album.update(self._parse_info(element))
            album.update(self._parse_album_pictures(element))
            albums.append(album)

        return albums

    def parse_pictures(self, content):
        soup = BeautifulSoup(content, "lxml")

        elements = soup.find_all('div', class_='albThumb')
        pictures = []
        for element in elements:
            picture = {}
            picture['src180x180'] = element.find('img')['src']
            picture['src'] = "https://ipstatic.net/photos/" + picture['src180x180'].split('/180x180/')[1]
            # picture['src'] = self._patch_src(picture['src'])
            pictures.append(picture)

        return pictures

    def _parse_aid(self, element):
        href = element.find('a', class_='albEditThumb')['href']
        aid = href.split('&')[0].split('=')[-1]
        return {'aid': aid}

    def _parse_info(self, element):
        name = element.find('h3').text
        stat = element.find('div', class_='albumStats').text.split('|')
        pics_number = int(stat[0].strip().split()[0])
        created = stat[1].strip().split(None, 1)[1]
        updated = stat[2].strip().split(None, 1)[1]
        return {
            'name': name,
            'pics_number': pics_number,
            'created': created,
            'updated': updated
        }

    def _parse_album_pictures(self, element):
        links = element.find_all('a', class_='thumb')
        pics = [
            link.find('img')['src']
            for link in links
        ]
        return {'pictures': pics}

    # def _patch_src(self, src):
    #     if src[-6] == '_':
    #         src = src[:-6] + src[-4:]
    #     return src
