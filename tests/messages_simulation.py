import websockets
import asyncio
import json
from test_authentication import get_authorization_header
from datetime import datetime
import requests


SERVER = "http://app:8000"

def get_user_information(username:str,password:str) -> dict:
    headers = get_authorization_header(username, password)
    response = requests.get(f"{SERVER}/usercredentials",headers=headers)
    user_information = response.json()
    token = headers["Authorization"].split(" ")[-1]
    username = user_information["username"]
    profile = user_information["profile"]
    return {"username":username,"profile":profile,"token":token}


async def connect_first_user(blaziken_data:dict):
    token = blaziken_data["token"]
    username = blaziken_data["username"]
    profile = blaziken_data["profile"]
    count = 0
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/server/{token}") as ws:
        while True:
            await ws.send(json.dumps({"chat":"dm","dm":18,"type":"text","text":count,"username":username,"otheruser":"bot","profile":profile,"date":datetime.now().isoformat()}))
            count += 2
            await asyncio.sleep(.5)
async def connect_second_user(nolife_data):
    await asyncio.sleep(.1)
    token = nolife_data["token"]
    username = nolife_data["username"]
    profile = nolife_data["profile"]
    count = 1
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/server/{token}") as ws:
        while True:
            await ws.send(json.dumps({"chat":"dm","dm":18,"type":"text","text":count,"username":username,"otheruser":"Donyone","profile":profile,"date":datetime.now().isoformat()}))
            count += 2
            await asyncio.sleep(.5)
async def main():
    blaziken_data = get_user_information("Donyone","1234")
    nolife_data = get_user_information("bot","1234")
    tasks = []
    tasks.append(asyncio.create_task(connect_first_user(blaziken_data)))
    tasks.append(asyncio.create_task(connect_second_user(nolife_data)))
    await asyncio.gather(*tasks)





asyncio.run(main())