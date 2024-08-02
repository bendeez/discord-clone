import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, WebSocket, WebSocketException
from exceptions import DiscordUnauthorized
from app.base_service import BaseService
from app.db.database import get_db
from app.config import settings
from app.user.service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from app.websocket_server.schemas.websocket_connection import WebsocketConnection
from app.auth.schemas import TokenCreate
from passlib.context import CryptContext

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class HashService:
    def __init__(self, schemes: list = ["bcrypt"], deprecated: str = "auto"):
        self.pwd_context = CryptContext(schemes=schemes, deprecated=deprecated)

    def verify(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash(self, password):
        return self.pwd_context.hash(password)


class AuthService(BaseService):
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return TokenCreate(access_token=encoded_jwt)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise DiscordUnauthorized()
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("username")
        if username is None:
            raise DiscordUnauthorized()
        user = await UserService().get_user_by_username(
            remote_user_username=username
        )  # doesnt have session
        if user is None:
            raise DiscordUnauthorized()
        return user
    except jwt.PyJWTError:
        raise DiscordUnauthorized()


async def get_websocket_user(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    websocket_params = websocket.path_params
    token = websocket_params.get("token")
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("username")
        if username is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        user = await UserService.get_user_data(db=db, username=username)
        if user is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        user_data_json = WebsocketConnection(
            **{
                "websocket": websocket,
                "username": user.username,
                "profile": user.profile,
                "server_ids": [server.server_id for server in user.server_associations],
                "dm_ids": [dm.id for dm in user.sent_dms + user.received_dms],
                "user_model": user,
            }
        )
        return user_data_json
    except jwt.PyJWTError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
