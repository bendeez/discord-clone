from pydantic import Field,TypeAdapter
from typing import Union,Annotated
from app.schemas.websocket_data.dm_message import DmWebsocketMessage
from app.schemas.websocket_data.server_message import ServerWebsocketMessage
from app.schemas.websocket_data.notification_message import Notification
from app.schemas.websocket_data.notificationall_message import NotificationAll



WebsocketData = Annotated[Union[DmWebsocketMessage,ServerWebsocketMessage,Notification,NotificationAll],Field(...,discriminator='chat')]
websocket_data_adaptor = TypeAdapter(WebsocketData)

