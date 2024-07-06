from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    
class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    profile: str


class UserCreate(UserIn):
    email: str

class UserCreated(UserBase):
    email: str

class UserTokenOut(BaseModel):
    access_token: str

class UserUpdateProfile(BaseModel):
    profile: str
