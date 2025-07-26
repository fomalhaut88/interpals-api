"""
This Python library provides a simple HTTP API for working with the website https://interpals.net/. It includes:

* retrieving data by user identifier
* listing visitors
* searching for users by criterions
* viewing and sending messages, deleting chats
* listing, adding and removing friends
* listing albums and pictures

## Installation

```
pip install interpals-api
```

## Basic example

```python
from interpals_api import Session, Api

session = Session.login('yourusername', 'yourpassword')
api = Api(session)

user_info = api.profile('someuser')
print(user_info)
```

Since version `2.1` it supports asynchronous calls for each api method. Below there is a brief asynchonous example:

```python
from interpals_api import SessionAsync, ApiAsync

session = await SessionAsync.login('yourusername', 'yourpassword')
api = ApiAsync(session)

user_info = await api.profile('someuser')
print(user_info)
```

## Other examples

Basic example to retrieve user info:

```python
from interpals_api import Session, Api

session = Session.login('yourusername', 'yourpassword')
api = Api(session)

# This gives info of the user with the link: https://www.interpals.net/someuser
user_info = api.profile('someuser')
```

Dump and load session object:

```python
from interpals_api import Session, Api

session = Session.login('yourusername', 'yourpassword')

# Save session into a file
with open('session.json', 'w') as f:
    session.dump(f)

# Load session from the saved file
with open('session.json') as f:
    session = Session.load(f)
```

Viewing and searching for users:

```python
from interpals_api import Session, Api

session = Session.login('yourusername', 'yourpassword')
api = Api(session)

# Viewing a certain user
api.view('someuser')

# Showing the visitors of your profile
users = api.visitors()
print(users)

# Searching for users
options = {
    'age1': '20',
    'age2': '40',
    'sex': ['male', 'female'],
    'continents': ['AF', 'AS', 'EU', 'NA', 'OC', 'SA'],
    'countries': ['US', 'CA', 'UK', 'RU'],
    'keywords': 'travelling',
    'online': True,
    'cityName': 'London'  # Or you can use 'city' with its direct code on the website (it's faster)
}
for user in api.search(options, limit=100, timeout=1.0):
    print(user)
```

To work with friends and pictures, it is necessary to use `uid` in methods:

```python
from interpals_api import Session, Api

session = Session.login('yourusername', 'yourpassword')
api = Api(session)

uid = api.get_uid('someuser')

# Listing friends of the user 'someuser'
friends = api.friends(uid)
print(friends)

# Adding 'someuser' to friends
api.friend_add(uid)

# Removing 'someuser' from friends
api.friend_remove(uid)

# Listing pictures
albums = api.albums(uid)
for album in albums:
    aid = album['aid']
    pictures = api.pictures(uid, aid)
    for picture in pictures:
        print(picture['src'])
```

Working with the chat is done through `thread_id`:

```python
from interpals_api import Session, Api

session = Session.login('yourusername', 'yourpassword')
api = Api(session)

uid = api.get_uid('someuser')

# Listing your chats
result = api.chat(count=9, offset=0)
print(result['chats'])

# Staring new chat (getting thread_id)
thread_id = api.get_thread_id(uid)

# Show chat messages
messages = api.chat_messages(thread_id)
print(messages)

# Send new message to the thread
api.chat_send(thread_id, "Hey! How are you?")

# Removing chat
api.chat_delete(thread_id)
```

"""

from .session import Session, SessionAsync
from .api import Api, ApiAsync
