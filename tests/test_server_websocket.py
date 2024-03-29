import websockets
import pytest
from test_authentication import get_authorization_header
import json
import requests
from datetime import datetime
import asyncio

SERVER = "/api"



def get_user_information(username:str,password:str) -> dict:
    headers = get_authorization_header(username, password)
    response = requests.get(f"{SERVER}/usercredentials",headers=headers)
    assert response.status_code == 200
    user_information = response.json()
    token = headers["Authorization"].split(" ")[-1]
    username = user_information["username"]
    profile = user_information["profile"]
    return {"username":username,"profile":profile,"token":token}


async def connect_first_user(blaziken_data:dict):
    token = blaziken_data["token"]
    username = blaziken_data["username"]
    profile = blaziken_data["profile"]
    await asyncio.sleep(.5)
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/server/{token}") as ws:
        await ws.send(json.dumps({"chat":"dm","dm":1,"type":"text","text":"hi","username":username,"otheruser":"nolife","profile":profile,"date":datetime.now().isoformat()}))
async def connect_second_user(nolife_data:dict):
    token = nolife_data["token"]
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/server/{token}") as ws:
        dm_message = json.loads(await asyncio.wait_for(ws.recv(),5))
        print(dm_message)
        assert dm_message["chat"] == "dm"
        notification = json.loads(await asyncio.wait_for(ws.recv(), 5))
        print(notification)
        assert notification["chat"] == "notification"
@pytest.mark.asyncio
async def test_websocket_messages():
    blaziken_data = get_user_information("Blaziken","1234")
    nolife_data = get_user_information("nolife","1234")
    tasks = []
    tasks.append(asyncio.create_task(connect_first_user(blaziken_data)))
    tasks.append(asyncio.create_task(connect_second_user(nolife_data)))
    await asyncio.gather(*tasks)






