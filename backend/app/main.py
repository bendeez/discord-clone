from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import dms, friend_requests, friends, notifications, servers, user, server_websocket

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dms.router)
app.include_router(friend_requests.router)
app.include_router(friends.router)
app.include_router(notifications.router)
app.include_router(servers.router)
app.include_router(server_websocket.router)
app.include_router(user.router)
