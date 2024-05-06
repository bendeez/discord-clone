from pydantic import BaseModel, Field
from typing import Union
from app.schemas.websocket_data.dm_message import DmWebsocketMessage
from app.schemas.websocket_data.server_message import ServerWebsocketMessage
from app.schemas.websocket_data.notification_message import Notification
from app.schemas.websocket_data.notificationall_message import NotificationAll



class WebsocketData(BaseModel):
    data: Union[DmWebsocketMessage,ServerWebsocketMessage,Notification,NotificationAll] = Field(...,discriminator='chat')

