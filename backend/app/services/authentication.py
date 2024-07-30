import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from app.db.database import get_db
from app.config import settings
from app.services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from base import BaseService
from app.schemas.websocket_data.websocket_connection import WebsocketConnection

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class AuthService(BaseService):

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        try:
            payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
            username = payload.get("username")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            user = await UserService.get_user(db=db, remote_user_username=username)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            return user
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_websocket_user(
        self, websocket: WebSocket, db: AsyncSession = Depends(get_db)
    ):
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
                    "server_ids": [
                        server.server_id for server in user.server_associations
                    ],
                    "dm_ids": [dm.id for dm in user.sent_dms + user.received_dms],
                    "user_model": user,
                }
            )
            return user_data_json
        except jwt.PyJWTError:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
