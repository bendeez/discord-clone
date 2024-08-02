from pydantic import Field, TypeAdapter
from typing import Union, Annotated
from app.websocket_server.schemas.dm_message import DmWebsocketMessage
from app.websocket_server.schemas.server_message import ServerWebsocketMessage
from app.websocket_server.schemas.notification_message import Notification
from app.websocket_server.schemas.notificationall_message import NotificationAll


WebsocketData = Annotated[
    Union[DmWebsocketMessage, ServerWebsocketMessage, Notification, NotificationAll],
    Field(..., discriminator="chat"),
]
websocket_data_adaptor = TypeAdapter(WebsocketData)
