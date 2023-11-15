import requests
import aiohttp


def request(url,
            method="GET",
            data=None,
            headers={},
            timeout=None,
            allow_redirects=True,
            use_async=False):
    if use_async:
        return _request_async(url,
                              method=method,
                              data=data,
                              headers=headers,
                              timeout=timeout,
                              allow_redirects=allow_redirects)
    else:
        return _request_sync(url,
                             method=method,
                             data=data,
                             headers=headers,
                             timeout=timeout,
                             allow_redirects=allow_redirects)


def _request_sync(url,
                  method="GET",
                  data=None,
                  headers={},
                  timeout=None,
                  allow_redirects=True):
    return


async def _request_async(url,
                         method="GET",
                         data=None,
                         headers={},
                         timeout=None,
                         allow_redirects=True):
    return
