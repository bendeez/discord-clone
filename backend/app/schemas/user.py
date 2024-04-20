from app.schemas.base import UserBase




class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    profile: str

class UserCreate(UserIn):
    email: str

