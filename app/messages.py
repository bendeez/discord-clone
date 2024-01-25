from aiokafka import AIOKafkaConsumer
import asyncpg
import json
from datetime import datetime
import redis
import asyncio


redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)

async def insert_message(pool:asyncpg.Pool,chat,type,username,consumed_message):
    async with pool.acquire() as connection:
        if chat == "dm":
            dm = consumed_message["id"]
            if type == "text":
                text = consumed_message["text"]
                await connection.execute("INSERT INTO dm_messages (text,username,dm,created_date) VALUES ($1,$2,$3,$4)",text,username,int(dm),datetime.now())
            if type == "file":
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                await connection.execute("INSERT INTO dm_messages (file,filetype,username,dm,created_date) VALUES ($1,$2,$3,$4,$5)",file, file_type, username, int(dm), datetime.now())
            if type == "textandfile":
                text = consumed_message["text"]
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                await connection.execute("INSERT INTO dm_messages (text,file,filetype,username,dm,created_date) VALUES ($1,$2,$3,$4,$5,$6)",text, file, file_type, username, int(dm), datetime.now())
            if type == "link":
                link = consumed_message["link"]
                server_invite_id = consumed_message["serverinviteid"]
                await connection.execute("INSERT INTO dm_messages (link,username,dm,serverinviteid,created_date) VALUES ($1,$2,$3,$4,$5)",link, username, int(dm), int(server_invite_id), datetime.now())
                redis_client.set(link, server_invite_id)
        if chat == "server":
            server = consumed_message["id"]
            if type == "text":
                text = consumed_message["text"]
                await connection.execute("INSERT INTO server_messages (text,username,server,created_date) VALUES ($1,$2,$3,$4)",text, username, int(server), datetime.now())
            if type == "file":
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                await connection.execute("INSERT INTO server_messages (file,filetype,username,server,created_date) VALUES ($1,$2,$3,$4,$5)",file, file_type, username, int(server), datetime.now())
            if type == "textandfile":
                text = consumed_message["text"]
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                await connection.execute("INSERT INTO server_messages (text,file,filetype,username,server,created_date) VALUES ($1,$2,$3,$4,$5,$6)",text, file, file_type, username, int(server), datetime.now())
            if type == "announcement":
                username = consumed_message["username"]
                announcement = consumed_message["announcement"]
                await connection.execute("INSERT INTO server_messages (announcement,username,server,created_date) VALUES ($1,$2,$3,$4)",announcement, username, int(server), datetime.now())
async def save_messages():
    consumer = AIOKafkaConsumer("notifications", bootstrap_servers="localhost:29092")
    await consumer.start()
    try:
        async with asyncpg.create_pool(host="127.0.0.1", port=5432, user="postgres", database="discord",password="discord", min_size=6, max_size=6) as pool:
            async for message in consumer:
                consumed_message = json.loads(message.value.decode())
                chat = consumed_message.get("chat")
                type = consumed_message["type"]
                username = consumed_message.get("username")
                asyncio.create_task(insert_message(pool,chat,type,username,consumed_message))
    finally:
        await consumer.stop()

asyncio.run(save_messages())


