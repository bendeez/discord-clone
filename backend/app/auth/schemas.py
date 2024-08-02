from pydantic import BaseModel


class TokenCreate(BaseModel):
    access_token: str
