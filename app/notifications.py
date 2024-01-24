from aiokafka import AIOKafkaConsumer
import psycopg2
import json
import websockets
import asyncio
import redis
from datetime import datetime

conn = psycopg2.connect(host="localhost",port="5432",dbname="discord",user="postgres",password="discord")
cursor = conn.cursor()
redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
server_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

async def notifications():
    consumer = AIOKafkaConsumer("notifications", bootstrap_servers="localhost:29092")
    await consumer.start()
    try:
        async with websockets.connect(f"ws://127.0.0.1:8000/ws/server/{server_token}") as ws:
            async for message in consumer:
                consumed_message = json.loads(message.value.decode())
                chat = consumed_message.get("chat")
                type = consumed_message["type"]
                if chat == "dm":
                    if type == "text" or type == "file" or type == "textandfile" or type == "link":
                        dm = consumed_message["id"]
                        username = consumed_message["username"]
                        other_user = consumed_message["otheruser"]
                        profile = consumed_message["profile"]
                        message_json = {"chat":"notification","type":"message","dm":dm,"sender":username,"receiver":other_user,"profile":profile}
                        await ws.send(json.dumps(message_json))
                        cursor.execute("SELECT * from notifications WHERE dm = %s",(dm,))
                        notification = cursor.fetchone()
                        if notification:
                            count = notification[4] + 1
                            cursor.execute("UPDATE notifications SET count = %s WHERE dm = %s",(count,dm))
                            conn.commit()
                        else:
                            count = 1
                            cursor.execute("INSERT INTO notifications (sender,receiver,dm,count) VALUES (%s,%s,%s,%s)", (username,other_user,dm,count))
                            conn.commit()
                if type == "status":
                    status = consumed_message["status"]
                    username = consumed_message["username"]
                    message_json = {"chat":"notificationall","type": "status", "status": status, "username":username}
                    await ws.send(json.dumps(message_json))
                    redis_client.set(f"{username}-status", status)
                if type == "newdm":
                    other_user = consumed_message["otheruser"]
                    username = consumed_message["username"]
                    message_json = {"chat":"notification","type":"newdm","sender":username,"receiver":other_user}
                    await ws.send(json.dumps(message_json))
                if type == "announcement":
                    server_id = consumed_message["serverid"]
                    username = consumed_message["username"]
                    message_json = {"chat":"server","id":server_id,"type":"announcement","announcement":f"{username} has joined the server","username":username,"date":datetime.now().isoformat()}
                    await ws.send(json.dumps(message_json))
    finally:
        await consumer.stop()

asyncio.run(notifications())







