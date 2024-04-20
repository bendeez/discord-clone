from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status,WebSocket,WebSocketException
from app.db.database import get_db
from app.core.config import settings
from app.models.user import Users
from app.models.dms import Dms
from app.models.servers import Server_User
from sqlalchemy import or_,select
from sqlalchemy.ext.asyncio import AsyncSession

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(data:dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token:str = Depends(oauth2_scheme),db:AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
        username = payload.get("username")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
        user = await db.execute(select(Users).filter(Users.username == username))
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
async def get_websocket_user(websocket:WebSocket,db:AsyncSession = Depends(get_db)):
    websocket_params = websocket.path_params
    token = websocket_params.get("token")
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("username")
        if username is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        user_data = await db.execute(select(Users.username, Dms.id.label("dm_id"),
                                            Server_User.server_id.label("server_id")).select_from(Users).outerjoin(
            Dms, or_(Dms.sender == username, Dms.receiver == username)) \
                                     .outerjoin(Server_User, Server_User.username == username).filter(
            Users.username == username))
        user_data = user_data.all()
        if not user_data:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        user_data_json = {"websocket":websocket,"username": user_data[0].username, "server_ids": list(set(user.server_id for user in user_data)),"dm_ids": list(set(user.dm_id for user in user_data))}
        return user_data_json
    except JWTError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

