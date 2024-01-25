from aiokafka import AIOKafkaConsumer
import asyncpg
import json
import websockets
import asyncio
import redis
from datetime import datetime

redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
server_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

async def update_notification_count(pool:asyncpg.Pool,count,dm):
    async with pool.acquire() as connection:
        return await connection.execute("UPDATE notifications SET count = $1 WHERE dm = $2",count,int(dm))
async def insert_notification(pool:asyncpg.Pool,username,other_user,dm,count):
    async with pool.acquire() as connection:
        return await connection.execute("INSERT INTO notifications (sender,receiver,dm,count) VALUES ($1,$2,$3,$4)", username,other_user,int(dm),count)
async def send_message(ws,message_json:dict):
    await ws.send(json.dumps(message_json))

async def create_dm_notification(pool:asyncpg.Pool,ws,consumed_message:dict):
    dm = consumed_message["id"]
    username = consumed_message["username"]
    other_user = consumed_message["otheruser"]
    profile = consumed_message["profile"]
    message_json = {"chat": "notification", "type": "message", "dm": dm, "sender": username, "receiver": other_user,
                    "profile": profile}
    asyncio.create_task(send_message(ws, message_json))
    async with pool.acquire() as connection:
        notification = await connection.fetchrow("SELECT * from notifications WHERE dm = $1", int(dm))
    if notification:
        count = notification["count"] + 1
        asyncio.create_task(update_notification_count(pool, count, dm))
    else:
        count = 1
        asyncio.create_task(insert_notification(pool, username, other_user, dm, count))
async def notifications():
    consumer = AIOKafkaConsumer("notifications", bootstrap_servers="localhost:29092")
    await consumer.start()
    try:
        async with asyncpg.create_pool(host="127.0.0.1",port=5432,user="postgres",database="discord",password="discord",min_size=6,max_size=6) as pool:
            async with websockets.connect(f"ws://127.0.0.1:8000/ws/server/{server_token}") as ws:
                async for message in consumer:
                    consumed_message = json.loads(message.value.decode())
                    chat = consumed_message.get("chat")
                    type = consumed_message["type"]
                    if chat == "dm":
                        if type == "text" or type == "file" or type == "textandfile" or type == "link":
                            asyncio.create_task(create_dm_notification(pool,ws,consumed_message))
                    if type == "status":
                        status = consumed_message["status"]
                        username = consumed_message["username"]
                        message_json = {"chat":"notificationall","type": "status", "status": status, "username":username}
                        asyncio.create_task(send_message(ws,message_json))
                        redis_client.set(f"{username}-status", status)
                    if type == "newdm":
                        other_user = consumed_message["otheruser"]
                        username = consumed_message["username"]
                        message_json = {"chat":"notification","type":"newdm","sender":username,"receiver":other_user}
                        asyncio.create_task(send_message(ws,message_json))
                    if type == "announcement":
                        server_id = consumed_message["serverid"]
                        username = consumed_message["username"]
                        message_json = {"chat":"server","id":server_id,"type":"announcement","announcement":f"{username} has joined the server","username":username,"date":datetime.now().isoformat()}
                        asyncio.create_task(send_message(ws,message_json))
    finally:
        await consumer.stop()
        await ws.close()

asyncio.run(notifications())







