"""
# interpals-api

This Python library provides a simple HTTP API for working with the website
https://interpals.net/. It includes:

* retrieving data by user identifier
* listing visitors
* searching for users by criteria
* viewing users
* listing albums and pictures

## Installation

```
pip install interpals-api
```

## Basic example

```python
from interpals_api import login_sync, ApiSync

session = login_sync('yourusername', 'yourpassword')
api = ApiSync(session)

profile = api.profile('someuser')
print(profile)
```

Since version `2.1` it supports asynchronous calls for each api method. Below
there is a brief asynchronous example:

```python
from interpals_api import login_async, ApiAsync

session = await login_async('yourusername', 'yourpassword')
api = ApiAsync(session)

profile = await api.profile('someuser')
print(profile)
```

## Other examples

Basic example to retrieve user info:

```python
from interpals_api import login_sync, ApiSync

session = login_sync('yourusername', 'yourpassword')
api = ApiSync(session)

# This gives info of the user with the link: https://www.interpals.net/someuser
profile = api.profile('someuser')
```

Dump and load session object:

```python
from interpals_api import login_sync, ApiSync

session = login_sync('yourusername', 'yourpassword')

# Save session into a file
with open('session.txt', 'w') as f:
    f.write(session.dumps())

# Load session from the saved file
with open('session.txt') as f:
    session = Session.loads(f.read())
```

Viewing and searching for users:

```python
from interpals_api import login_sync, ApiSync
from interpals_api.schemas import SearchOptions

session = login_sync('yourusername', 'yourpassword')
api = ApiSync(session)

# Viewing a certain user
api.view('someuser')

# Showing the visitors of your profile
users = api.visitors()
print(users)

# Searching for users
options = SearchOptions(
    age1=20,
    age2=40,
    sex=['male', 'female'],
    continents=['AF', 'AS', 'EU', 'NA', 'OC', 'SA'],
    countries=['US', 'CA', 'UK', 'RU'],
    keywords='travelling',
    online=True,
    city_name='London'  # Or you can use 'city_code' with its direct code on
                        # the website (it's faster)
)
for user in api.search(options, limit=100, timeout=1.0):
    print(user)
```

To work with pictures, it is necessary to use `uid` in methods:

```python
from interpals_api import login_sync, ApiSync

session = login_sync('yourusername', 'yourpassword')
api = ApiSync(session)

uid = api.get_uid('someuser')

albums = api.albums(uid)
for album in albums:
    pictures = api.pictures(uid, album.aid)
    for picture in pictures:
        print(picture.large)
```
"""

from .session import Session, login_sync, login_async  # noqa: F401
from .api import ApiSync, ApiAsync  # noqa: F401
