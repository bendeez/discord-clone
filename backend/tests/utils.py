from aiohttp import ClientSession
from enum import Enum

http_server = "http://127.0.0.1:8000"

class RequestMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


async def http_request(session: ClientSession,
                       path,method=RequestMethod.GET,
                       json=None,files=None,token=None):
    url = f"{http_server}{path}"
    headers = {"Authorization": f"bearer {token}"}
    if method == RequestMethod.POST:
        response = await session.post(url, json=json, data=files, headers=headers)
    elif method == RequestMethod.PUT:
        response = await session.put(url, json=json, data=files, headers=headers)
    elif method == RequestMethod.GET:
        response = await session.get(url, headers=headers)
    elif method == RequestMethod.DELETE:
        response = await session.delete(url, json=json, headers=headers)
    else:
        raise ValueError("Invalid method")
    return response








