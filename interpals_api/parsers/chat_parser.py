from bs4 import BeautifulSoup


class ChatParser:
    def parse_maxmsgid(self, body):
        soup = BeautifulSoup(body, "lxml")
        maxmsgid = soup.find('div', id='threads_left')['data-max-msg-id']
        return maxmsgid

    def parse_unread(self, body):
        soup = BeautifulSoup(body, "lxml")
        unread = soup.find('span', id='pmNewCnt').text.strip()
        return int(unread[2:-1]) if unread else 0

    def parse_chat(self, body):
        soup = BeautifulSoup(body, "lxml")

        chats = []
        elements = soup.find_all('div', class_='pm_thread')
        for element in elements:
            chat = {}
            chat.update(self._parse_thread_info(element))
            chat.update(self._parse_user_info(element))
            chat.update(self._parse_message_info(element))
            chats.append(chat)

        return chats

    def parse_messages(self, body):
        soup = BeautifulSoup(body, "lxml")

        messages = []

        elements = soup.find_all('div', class_=['pm_date', 'pm_msg'])
        user = None
        date = None
        for element in elements:
            if 'pm_date' in element['class']:
                date = element.text

            else:
                msg_user_thumb = element.find('div', class_='msg_user_thumb')
                if msg_user_thumb:
                    user = msg_user_thumb.a['href']

                message = {}
                message.update(self._parse_message(element))
                message['date'] = date
                message['user'] = user
                messages.append(message)

        return messages

    def _parse_thread_info(self, element):
        data = {}
        data['new'] = 'new' in element['class']
        data['thread_id'] = element['id'][7:]
        return data

    def _parse_user_info(self, element):
        data = {}

        tui_el = element.find_all('div', class_='tui_el')
        user_age = tui_el[0].text.strip().split(', ')
        if len(user_age) == 2:
            data['user'], data['age'] = user_age
        else:
            data['user'], data['age'] = user_age[0], None
        data['city'] = tui_el[1].text
        data['sex'] = tui_el[0]['class'][1]

        data['avatar'] = 'https:' + element.find(class_='thumb')['src']

        data['flag'] = None
        flag_img = element.find('div', class_='tui_flag').img
        if flag_img:
            data['flag'] = 'https:' + flag_img['src']

        data['online'] = bool(element.find(class_='online-now'))

        return data

    def _parse_message_info(self, element):
        data = {}
        data['message'] = element.find(class_='th_snippet').text.strip()
        data['i_sent'] = bool(element.find(class_='snippet_thumb'))
        data['unread'] = 'pm_new' in element.find(class_='th_snippet')['class']
        return data

    def _parse_message(self, element):
        data = {}
        data['time'] = element.find('div', class_='pm_time').text
        data['text'] = element.find('div', class_='msg_body').text.strip()
        data['msg_id'] = element['id'][4:]
        data['unread'] = 'pm_unread' in element['class']
        return data
