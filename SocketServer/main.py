import socket
import asyncio
from anyio import create_task_group
import json
from schemas import ConnectionConfig, Message

class SocketServer:

    def __init__(self):
        self.active_connections: list[ConnectionConfig] = []
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    async def recv_data(self, client: socket.socket):
        data = await self.loop.sock_recv(client, 2048)
        data = json.loads(data.decode())
        data["client"] = client
        connection = ConnectionConfig(**data)
        self.active_connections.append(connection)
        while True:
            data = await self.loop.sock_recv(client, 2048)
            data = json.loads(data.decode())
            Message.model_validate_json(data) # check if channel config is in message
            await self.broadcast(data=data)

    async def broadcast(self, data: dict):
        async with create_task_group() as task:
            for channel_type, channels in data.items():
                for channel in channels:
                    for connection in self.active_connections:
                        if channel in connection.channels[channel_type]:
                            task.start_soon(self.loop.sock_sendall, connection.client, json.dumps(data).encode())


    async def check_for_connections(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 8001))
        s.listen()
        while True:
            client, _ = await self.loop.sock_accept(s)
            asyncio.create_task(self.recv_data(client))


async def main():
    socket_server = SocketServer()
    await socket_server.check_for_connections()

asyncio.run(main())