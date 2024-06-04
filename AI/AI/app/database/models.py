from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import relationship

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)

# Создание таблиц


class Base(AsyncAttrs, DeclarativeBase):
    pass

# Таблица пользователей


class User(Base):
    __tablename__ = 'users'
    tg_id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, unique=True)
    name = Column(String)
    surname = Column(String)
    birth = Column(String)
    city = Column(String)
    phone = Column(String)
    email = Column(String)
    drafts = relationship("Draft", back_populates="user")

# Таблица черновиков


class Draft(Base):
    __tablename__ = 'drafts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, ForeignKey('users.tg_id'))
    name = Column(String)
    text = Column(String)
    user = relationship("User", back_populates="drafts")

# Таблица задач


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, index=True)
    text = Column(String, nullable=False)


# Создание таблиц


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
