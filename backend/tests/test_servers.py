import asyncio
from app.models.user import Users
from app.models.servers import Server, Server_User, Server_Messages
from utils import RequestMethod
import base64

async def test_create_server(http_request,websocket_connection,tokens,get_user_by_username_index,clean_up_data):

    async def create_server():
        current_user = await get_user_by_username_index(0)
        await websocket_connection(path=f"/ws/server/{tokens[current_user.username]}")
        with open("./tests/programming.jfif","rb") as f:
            encoded_image = base64.b64encode(f.read()).decode()
        json = {"name":f"{current_user.username} server","profile":encoded_image}
        response = await http_request("/server", method=RequestMethod.POST,
                                      json=json, token=tokens[current_user.username])
        data = await response.json()
        assert response.status == 201
        assert {"id":data["id"],"name":data["name"]} == {"id": data["id"], "name":json["name"]}
        assert data["profile"].startswith("https://firebasestorage.googleapis.com")
        await check_for_create_server_message(current_user,data,json)

    async def check_for_create_server_message(current_user,data,json):
        """
            check for create server message
        """
        server_id = data["id"]
        response = await http_request(f"/servermessages/{server_id}", method=RequestMethod.GET,
                                      json=json, token=tokens[current_user.username])
        data = await response.json()
        server_messages = [{key:value for key,value in message.items() if value is not None} for message in data] # filter out none values
        assert response.status == 200
        assert server_messages == [{"server":server_id,"announcement":f"{current_user.username} has created the server",
                                  "username":current_user.username,"profile":current_user.profile,"date":server_messages[0]["date"]}]
        await clean_up_data(Server,id=server_id)

    await create_server()


async def test_get_servers(http_request,get_user_by_username_index,tokens):
    """
        user with username of usernames[0] is a part
        of one server that it owns
    """
    current_user = await get_user_by_username_index(0,load_attributes=[(Users.owned_servers,)])
    server = current_user.owned_servers[0]
    response = await http_request(f"/servers", method=RequestMethod.GET, token=tokens[current_user.username])
    data = await response.json()
    assert response.status == 200
    assert data == [{"id":server.id,"profile":server.profile,"owner":server.owner,"name":f"{server.owner} server"}]

async def test_get_server_information(http_request,get_user_by_username_index,tokens):
    """
            user with username of usernames[0] is a part
            of one server that it owns
    """
    current_user = await get_user_by_username_index(0, load_attributes=[(Users.owned_servers,)])
    server = current_user.owned_servers[0]
    response = await http_request(f"/server/{server.id}", method=RequestMethod.GET, token=tokens[current_user.username])
    data = await response.json()
    assert response.status == 200
    assert data == {"id": server.id, "profile": server.profile, "owner": server.owner,"name": f"{server.owner} server"}

async def test_get_server_users(http_request,get_user_by_username_index,tokens):
    """
        returns users with usernames of usernames[0] and usernames[2]
        who are a part of the server that usernames[0] owns
    """
    current_user = await get_user_by_username_index(0, load_attributes=[(Users.owned_servers,)])
    remote_user = await get_user_by_username_index(2)
    server = current_user.owned_servers[0]
    response = await http_request(f"/server/users/{server.id}", method=RequestMethod.GET, token=tokens[current_user.username])
    data = await response.json()
    assert response.status == 200
    assert data == [{"username":remote_user.username,"profile":remote_user.profile,"status":remote_user.status},
                    {"username":current_user.username,"profile":current_user.profile,"status":current_user.status}
                    ]

async def test_join_server(http_request,websocket_connection,tokens,get_user_by_username_index,clean_up_data):

    async def send_link(current_user,current_user_ws,remote_user: Users):
        """
            user with username of usernames[0] (current_user) sends an invite link
            to username with usernames[1]
            user with usernames[0] is the dm sender of the dm with usernames[1]
        """
        dm = current_user.sent_dms[0]
        server = current_user.owned_servers[0]
        await current_user_ws.send_json({"chat":"dm","type":"link","serverinviteid":server.id,"dm":dm.id,"otheruser":remote_user.username})

        async def wait_for_remote_user_to_join():
            while True:
                data = await current_user_ws.receive_json()
                join_message = {"chat": "server","type":"announcement","server":server.id,
                                "announcement": f"{remote_user.username} has joined the server",
                                "username": remote_user.username, "profile": remote_user.profile,
                                "date": data.get("date")}
                if data == join_message:
                    return data

        await asyncio.wait_for(wait_for_remote_user_to_join(),2)
        await clean_up_data(Server_User, username=remote_user.username)

    async def wait_for_link_and_join_server(remote_user,remote_user_ws):
        """
            user with usernames[1] (remote_user) waits for invite link
            then joins the server
        """
        async def wait_for_link():
            while True:
                data = await remote_user_ws.receive_json()
                if "link" in data:
                    return data
        message_data = await asyncio.wait_for(wait_for_link(),2)
        json = {"link":message_data["link"]}
        response = await http_request("/server/user", method=RequestMethod.POST,
                                      json=json, token=tokens[remote_user.username])
        data = await response.json()
        assert response.status == 201
        assert data == {"id":data["id"],"username":remote_user.username,"server_id":message_data["serverinviteid"]}

    current_user = await get_user_by_username_index(0,load_attributes=[(Users.owned_servers,),(Users.sent_dms,)])
    current_user_ws = await websocket_connection(path=f"/ws/server/{tokens[current_user.username]}")

    remote_user = await get_user_by_username_index(1)
    remote_user_ws = await websocket_connection(path=f"/ws/server/{tokens[remote_user.username]}")

    tasks = []
    tasks.append(asyncio.create_task(send_link(current_user,current_user_ws,remote_user)))
    tasks.append(asyncio.create_task(wait_for_link_and_join_server(remote_user,remote_user_ws)))
    await asyncio.gather(*tasks)

async def test_invalid_link(http_request,usernames,tokens):
    json = {"link": "invalidlink"}
    response = await http_request("/server/user", method=RequestMethod.POST,
                                  json=json, token=tokens[usernames[0]])
    assert response.status == 403

async def test_get_server_messages(http_request,get_user_by_username_index,usernames,tokens,clean_up_data):
    """
        there's only one message in the server
        except for a message from a previous test that will be deleted
        sent by the current user (usernames[0])
        Server_Messages(text="hi",user=user_models[0],date=datetime.now())
    """
    await clean_up_data(Server_Messages,announcement=f"{usernames[1]} has joined the server")
    current_user = await get_user_by_username_index(0,load_attributes=[(Users.owned_servers,Server.server_messages)])
    server = current_user.owned_servers[0]
    response = await http_request(f"/servermessages/{server.id}", method=RequestMethod.GET, token=tokens[current_user.username])
    data = await response.json()
    server_messages = [{key: value for key, value in message.items() if value is not None}
                   for message in data]  # filter out None values
    assert server_messages == [{"server":server.id,"text":"hi","username":current_user.username,
                    "profile":current_user.profile,"date":server_messages[0]["date"]}]
    assert response.status == 200




