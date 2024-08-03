class DiscordError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.headers = headers

class DiscordUnauthorized(DiscordError):
    def __init__(self, message: str = "Invalid credentials", status_code: int = 401) -> None:
        super().__init__(
            message,
            status_code
        )
