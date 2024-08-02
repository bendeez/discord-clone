from fastapi import FastAPI
from app.exceptions import DiscordError


class DiscordUnauthorized(DiscordError):
    def __init__(
        self, message: str = "Could not validate credentials", status_code: int = 401
    ) -> None:
        super().__init__(message, status_code)
