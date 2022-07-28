from urllib.parse import urlparse

from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from bot.models import Base
from bot.models.users import User


class Database(object):

    def __init__(self, db: int = 0, **kwargs):
        ret = urlparse(kwargs.get("config")["db"]["host"])
        print(ret)
        self._engine = create_async_engine("sqlite+aiosqlite:///database.db",
                                           future=True,
                                           echo=True)
        self.async_session = sessionmaker(self._engine,
                                          expire_on_commit=False,
                                          class_=AsyncSession)

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def add_user(self, id: int, force=False):
        async with self.async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.id == id)
                result = await session.execute(stmt)
            if result.first() is None or force:
                print(f"creating users {id}")
                u = User(id=id, data="meow")
                session.add(u)
                try:
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
            else:
                print("user already exists")
        #    data = {
        #        "server-uri": "",
        #        "username": "",
        #        "password": "",
        #        "split-size": 100,
        #        "upload-path": "/",
        #        "upload-parallel": "false",
        #        "streaming": "false",
        #        "use-libcurl": "false",
        #        "use-compression": "false",
        #        "file-password": "",
        #        "checksum": "true",
        #    }

        #            self.set_data(id, **data)
        #            return True

        return False

    def get_data(self, id: int):
        return {
            k.decode("utf-8"): v.decode("utf-8")
            for k, v in self._redis.hgetall(f"user:{id}").items()
        }

    def set_data(self, id: int, **kwargs):
        # print(kwargs)
        for k, v in kwargs.items():
            self._redis.hset(f"user:{id}", key=k, value=v)

    async def contains_user(self, id: int):
        async with self.async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.id == id)
                result = await session.execute(stmt)
            if result.first() is None:
                return False
            else:
                return True
