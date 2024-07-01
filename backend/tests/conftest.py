import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from aiohttp import ClientSession
from utils import http_request,RequestMethod
from app.db.database import SessionLocal, engine
from app.db.base import BaseMixin
from app.core.oauth import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Users
from app.models.dms import Dms, Dm_Messages
from app.models.servers import Server, Server_User, Server_Messages
from app.models.friends import Friends
from app.models.friend_requests import FriendRequests
from app.models.notifications import Notifications
from app.core.utils import hash
from datetime import datetime
from functools import reduce

"""
    Note: Implement a way to test
    locally so I can have direct
    access to the domain logic
    such as websocket connection manager
"""

@pytest.fixture(name="db",scope="session",autouse=True)
async def create_db_session():
    async with SessionLocal() as db:
        yield db

@pytest.fixture(scope="session")
def usernames():
    """
        usernames[0] aka current_user
        is the user from first person
        perspective

        password is automatically 1234
    """
    return ["current_user","test_user1","test_user2","test_user3"]

@pytest.fixture(scope="session",autouse=True)
async def populate_db(db):
    async with engine.begin() as conn:
        await conn.run_sync(BaseMixin.metadata.drop_all)
        await conn.run_sync(BaseMixin.metadata.create_all)

@pytest.fixture(scope="session",autouse=True)
async def insert_data(populate_db, usernames: list[str], db: AsyncSession):
    """
    third user has no entities
    @param populate_db:
    @param usernames:
    @param db:
    @return: None
    """
    user_models = [Users(username=username,email=f"{username}@gmail.com",password=hash("1234"))
                   for username in usernames]
    dm = Dms(sender_user=user_models[0],receiver_user=user_models[1],
             dm_messages=[
                 Dm_Messages(text="hi", user=user_models[0], date=datetime.now())
             ])
    user_entities = [Server(name=f"{usernames[0]} server",owner_user=user_models[0],
                            server_users=[
                                Server_User(user=user_models[0]),
                                Server_User(user=user_models[2])
                            ],
                            server_messages=[
                                Server_Messages(text="hi",user=user_models[0],date=datetime.now())
                            ]),
                     Friends(sender_user=user_models[0],receiver_user=user_models[1],
                             dm=dm),
                     FriendRequests(sender_user=user_models[0],receiver_user=user_models[3]),
                     Notifications(sender_user=user_models[0],receiver_user=user_models[1],
                                   parent_dm=dm
                                   )
                     ]
    db.add_all(user_models + user_entities)
    await db.commit()

@pytest.fixture()
async def clean_up_data(db):
    async def _clean_up_data(model,**kwargs):
        delete_model = await db.execute(select(model).where(*[getattr(model,key) == value
                                                             for key, value in kwargs.items()]))
        delete_model = delete_model.scalars().first()
        if delete_model:
            await db.delete(delete_model)
            await db.commit()
    return _clean_up_data

@pytest.fixture()
async def undelete_data(db):
    async def _undelete_data(model,**kwargs):
        db.add(model(**kwargs))
        await db.commit()
    return _undelete_data

@pytest.fixture(autouse=True)
async def get_user_by_username_index(insert_data,usernames,db: AsyncSession):
    async def _get_user_by_username_index(index,load_attributes: list[tuple] = []):
        """
            loads a chain (tuple) of relationships
        """
        user = await db.execute(select(Users).where(Users.username == usernames[index]).execution_options(populate_existing=True)
                                .options(*[reduce(lambda a,b: a.selectinload(b),chain[1:],selectinload(chain[0])) for chain in load_attributes]))
        user = user.scalars().first()
        return user

    return _get_user_by_username_index

@pytest.fixture(scope="session")
def tokens(usernames):
    return {username:create_access_token(data={"username":username}) for username in usernames}

@pytest.fixture(scope="session",name="session",autouse=True)
async def create_web_session():
    async with ClientSession() as session:
        yield session

@pytest.fixture(name="http_request")
async def make_http_request(session):
    async def _make_http_request(path,session=session,method=RequestMethod.GET,
                                 json=None,files=None,token=None):
        data = await http_request(session=session,path=path,method=method,
                                  json=json,files=files,token=token)
        return data
    return _make_http_request

@pytest.fixture(name="websocket_connection")
async def create_websocket_connection(session):
    websocket_server = "ws://127.0.0.1:8000"
    connections = []

    async def _create_websocket_connection(path):
        ws = await session.ws_connect(f"{websocket_server}{path}")
        connections.append(ws)
        return ws
    yield _create_websocket_connection

    for ws in connections:
        await ws.close()

@pytest.fixture(scope="session",autouse=True)
def anyio_backend():
    return "asyncio"









