from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.websocket_server.websocket_managers.CentralWebsocketServerInterface import (
    central_ws_interface,
)
import contextlib
from app.dm.endpoints import dm_router
from app.friend_request.endpoints import friend_request_router
from app.friend.endpoints import friend_router
from app.notification.endpoints import notification_router
from app.server.endpoints import server_router
from app.user.endpoints import user_router
from app.websocket_server.endpoints import websocket_router
from exception_handlers import add_exception_handlers


def configure_cors(app: FastAPI):
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@contextlib.asynccontextmanager
async def lifespan():
    await central_ws_interface.initialize_pubsub()
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    configure_cors(app=app)
    add_exception_handlers(app=app)
    app.include_router(dm_router)
    app.include_router(friend_request_router)
    app.include_router(friend_router)
    app.include_router(notification_router)
    app.include_router(server_router)
    app.include_router(websocket_router)
    app.include_router(user_router)

    return app


app = create_app()
