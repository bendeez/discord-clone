import socket
import asyncio
import json



class SocketClient:

    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sent_config = False
        self.message_queue = asyncio.Queue()

    async def connect(self):
        await self.loop.sock_connect(self.socket,('127.0.0.1', 8001))

    async def wait_for_message(self):
        msg = await self.loop.sock_recv(self.socket,2048)
        msg = json.loads(msg.decode())
        await self.message_queue.put(msg)

    async def send_config(self, message: dict):
        await self.loop.sock_sendall(self.socket, json.dumps(message).encode("utf-8"))
        self.sent_config = True

    async def send_message(self, message: dict):
        if self.sent_config:
            await self.loop.sock_sendall(self.socket, json.dumps(message).encode("utf-8"))
        else:
            raise Exception("Config not sent")

    def disconnect(self):
        self.socket.close()