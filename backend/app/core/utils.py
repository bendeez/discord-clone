from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash(password):
    return pwd_context.hash(password)