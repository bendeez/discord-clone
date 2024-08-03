import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, WebSocket, WebSocketException
from app.exceptions import DiscordUnauthorized
from app.config import settings
from app.user.service import UserService
from app.websocket_server.schemas.websocket_connection import WebsocketConnection
from app.auth.schemas import TokenCreate
from app.user.schemas import UserIn
from passlib.context import CryptContext
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class HashService:

    def __init__(self, schemes: list = ["bcrypt"], deprecated: str = "auto"):
        self.pwd_context = CryptContext(schemes=schemes, deprecated=deprecated)

    def verify(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash(self, password):
        return self.pwd_context.hash(password)


class AuthService(UserService):

    def __init__(self, hash_service: Optional[HashService] = Depends(HashService)):
        super().__init__()
        self.hash_service = hash_service
        self.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
        self.JWT_ALGORITHM = settings.JWT_ALGORITHM

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return TokenCreate(access_token=encoded_jwt)

    async def verify_user(self, user: UserIn):
        existing_user = await self.get_user_by_id(user_id=user.id)
        if existing_user is None:
            raise DiscordUnauthorized()
        verify_password = self.hash_service.verify(user.password, existing_user.password)
        if not verify_password:
            raise DiscordUnauthorized()

    def decode_user_id(self, token: str):
        try:
            if not token:
                raise DiscordUnauthorized()
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            user_id = payload.get("user_id")
            if user_id is None:
                raise DiscordUnauthorized()
            return user_id
        except jwt.PyJWTError:
            raise DiscordUnauthorized()

    async def get_current_user(self, token: str):
        user_id = self.decode_user_id(token=token)
        current_user = await self.get_user_by_id(
            user_id=user_id
        )
        if current_user is None:
            raise DiscordUnauthorized()
        return current_user

    async def get_websocket_user(self, websocket: WebSocket):
        token = websocket.path_params.get("token")
        user_id = self.decode_user_id(token=token)
        ws_user = await self.get_ws_user_entities(user_id=user_id)
        if ws_user is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        user_data_json = WebsocketConnection(
            **{
                "websocket": websocket,
                "username": ws_user.username,
                "profile": ws_user.profile,
                "server_ids": [server.server_id for server in ws_user.server_associations],
                "dm_ids": [dm.id for dm in ws_user.sent_dms + ws_user.received_dms],
                "user_model": ws_user,
            }
        )
        return user_data_json

async def get_current_user(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(AuthService)):
    current_user = await auth_service.get_current_user(token=token)
    return current_user

async def get_websocket_user(websocket: WebSocket, auth_service: AuthService = Depends(AuthService)):
    ws_user = await auth_service.get_websocket_user(websocket=websocket)
    return ws_user






