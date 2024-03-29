import asyncio

import aiohttp
import time
import requests
from test_authentication import get_authorization_header
import uuid
import pytest

SERVER = "/api"

# def sync_requests(blaziken_headers):
#     for i in range(100):
#         start = time.time()
#         random_username = str(uuid.uuid4())
#         payload = {"username":random_username,"password":"1234","email":"f"}
#         create_random_user_response = requests.post(f"{SERVER}/user",json=payload)
#         assert create_random_user_response.status_code == 200
#         random_user_headers = get_authorization_header(random_username,"1234")
#         payload = {"username":"ben"}
#         post_friend_request_response = requests.post(f"{SERVER}/friendrequest", json=payload, headers=random_user_headers)
#         assert post_friend_request_response.status_code == 200
#         payload = {"username":random_username}
#         post_friend_response = requests.post(f"{SERVER}/friend", json=payload, headers=blaziken_headers)
#         assert post_friend_response.status_code == 200
#         end = time.time()
#         print(end - start)
#
# async def send_async_request(session,sem,blaziken_headers):
#     async with sem:
#         start = time.time()
#         random_username = str(uuid.uuid4())
#         payload = {"username": random_username, "password": "1234", "email": "f"}
#         async with session.post(f"{SERVER}/user", json=payload) as create_random_user_response:
#             assert create_random_user_response.status == 200
#         random_user_headers = get_authorization_header(random_username, "1234")
#         payload = {"username": "ben"}
#         async with session.post(f"{SERVER}/friendrequest", json=payload,
#                                 headers=random_user_headers) as post_friend_request_response:
#             assert post_friend_request_response.status == 200
#         payload = {"username": random_username}
#         async with session.post(f"{SERVER}/friend", json=payload, headers=blaziken_headers) as post_friend_response:
#             assert post_friend_response.status == 200
#         end = time.time()
#         print(end-start)
# async def async_requests(blaziken_headers):
#     async with aiohttp.ClientSession() as session:
#         sem = asyncio.Semaphore(10)
#         tasks = []
#         for i in range(100):
#             tasks.append(asyncio.create_task(send_async_request(session,sem,blaziken_headers)))
#         await asyncio.gather(*tasks)
# @pytest.mark.asyncio
# async def test_friend_requests():
#     blaziken_headers = get_authorization_header("ben", "1234")
#     start = time.time()
#     sync_requests(blaziken_headers)
#     end = time.time()
#     sync_requests_time = end - start
#     print(sync_requests_time)
#     start = time.time()
#     await async_requests(blaziken_headers)
#     end = time.time()
#     async_requests_time = end - start
#     print(async_requests_time)


def test_get_friend_requests():
    headers = get_authorization_header("ben", "1234")
    response = requests.get(f"{SERVER}/friendrequests",headers=headers)
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert isinstance(data,list)

def test_get_friends():
    headers = get_authorization_header("ben", "1234")
    response = requests.get(f"{SERVER}/friends", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert isinstance(data, list)