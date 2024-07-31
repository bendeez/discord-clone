from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

class Database:

    def __init__(self, url):
        self.url = url
        self.engine = create_async_engine(url)
        self._session: Optional[AsyncSession] = None

    async def init(self):
        if self._session is not None:
            await self._session.close() # close the previous session
        self._session =

    async def get_session(self):
        if self.engine is None:
            raise RuntimeError("Engine has not been initialized")

        session_factory = async_sessionmaker(
                            autocommit=False, autoflush=False, expire_on_commit=False, bind=self.engine
                            )

        return session_factory()

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Database session has not been initialized.")
        return self._session


db: Database = Database(SQLALCHEMY_DATABASE_URL)
