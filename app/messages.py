from kafka import KafkaConsumer
import psycopg2
import json
from datetime import datetime
import redis

consumer = KafkaConsumer("messages",bootstrap_servers="localhost:29092")
conn = psycopg2.connect(host="localhost",port="5432",dbname="discord",user="postgres",password="discord")
cursor = conn.cursor()
redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)

while True:
    for message in consumer:
        consumed_message = json.loads(message.value.decode())
        chat = consumed_message.get("chat")
        type = consumed_message["type"]
        username = consumed_message.get("username")
        if chat == "dm":
            dm = consumed_message["id"]
            if type == "text":
                text = consumed_message["text"]
                cursor.execute("INSERT INTO dm_messages (text,username,dm,created_date) VALUES (%s,%s,%s,%s)",(text,username,dm,datetime.now()))
                conn.commit()
            if type == "file":
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                cursor.execute("INSERT INTO dm_messages (file,filetype,username,dm,created_date) VALUES (%s,%s,%s,%s,%s)",(file,file_type,username,dm,datetime.now()))
                conn.commit()
            if type == "textandfile":
                text = consumed_message["text"]
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                cursor.execute("INSERT INTO dm_messages (text,file,filetype,username,dm,created_date) VALUES (%s,%s,%s,%s,%s,%s)", (text,file,file_type,username,dm,datetime.now()))
                conn.commit()
            if type == "link":
                link = consumed_message["link"]
                server_invite_id = consumed_message["serverinviteid"]
                cursor.execute("INSERT INTO dm_messages (link,username,dm,serverinviteid,created_date) VALUES (%s,%s,%s,%s,%s)",(link,username,dm,server_invite_id,datetime.now()))
                conn.commit()
                redis_client.set(link,server_invite_id)
        if chat == "server":
            server = consumed_message["id"]
            if type == "text":
                text = consumed_message["text"]
                cursor.execute("INSERT INTO server_messages (text,username,server,created_date) VALUES (%s,%s,%s,%s)",(text,username,server,datetime.now()))
                conn.commit()
            if type == "file":
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                cursor.execute("INSERT INTO server_messages (file,filetype,username,server,created_date) VALUES (%s,%s,%s,%s,%s)",(file,file_type,username,server,datetime.now()))
                conn.commit()
            if type == "textandfile":
                text = consumed_message["text"]
                file = consumed_message["file"]
                file_type = consumed_message["filetype"]
                cursor.execute("INSERT INTO server_messages (text,file,filetype,username,server,created_date) VALUES (%s,%s,%s,%s,%s,%s)", (text,file,file_type,username,server,datetime.now()))
                conn.commit()
            if type == "announcement":
                username = consumed_message["username"]
                announcement = consumed_message["announcement"]
                cursor.execute("INSERT INTO server_messages (announcement,username,server,created_date) VALUES (%s,%s,%s,%s)",(announcement,username, server, datetime.now()))
                conn.commit()




