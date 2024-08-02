from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from exceptions import DiscordError


async def discord_exception_handler(
    request: Request, exc: DiscordError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": type(exc).__name__, "detail": exc.message},
        headers=exc.headers,
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DiscordError, discord_exception_handler)
