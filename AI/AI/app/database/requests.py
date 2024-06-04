from app.database.models import async_session
from app.database.models import User, Draft, Task
from sqlalchemy import select, update

# Создание пользователя


async def create_user(tg_id, username, name, surname, birth, city, phone, email):
    async with async_session() as session:
        id = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not id:
            session.add(User(tg_id=tg_id, username=username, name=name,
                        surname=surname, birth=birth, city=city, phone=phone, email=email))
            await session.commit()

# Получение пользователя


async def get_user(tg_id):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.tg_id == tg_id))
        return user.scalars().first()

# Получение имени пользователя


async def get_name(tg_id):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.tg_id == tg_id))
        return user.scalars().first().name

# Получение фамилии пользователя


async def create_draft(tg_id, name, text):
    async with async_session() as session:
        session.add(Draft(tg_id=tg_id, name=name, text=text))
        await session.commit()

# Получение черновика


async def get_drafts(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Draft).where(Draft.tg_id == tg_id))
        return result.scalars().all()

# Получение черновика по имени


async def get_draft_by_name(tg_id, name):
    async with async_session() as session:
        result = await session.execute(select(Draft).where(Draft.tg_id == tg_id, Draft.name == name))
        draft = result.scalars().first()
        return draft

# Удаление черновика


async def delete_draft(tg_id, name):
    async with async_session() as session:
        draft = await session.scalar(select(Draft).where(Draft.tg_id == tg_id, Draft.name == name))
        await session.delete(draft)
        await session.commit()


# Обновление данных пользователя
async def update_user(tg_id, field, value):
    async with async_session() as session:
        async with session.begin():
            stmt = (
                update(User)
                .where(User.tg_id == tg_id)
                .values({field: value})
            )
            await session.execute(stmt)
            await session.commit()


# Создание задачи
async def create_task(tg_id, text):
    async with async_session() as session:
        session.add(Task(tg_id=tg_id, text=text))
        await session.commit()

# Получение задач


async def get_tasks(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.tg_id == tg_id))
        return result.scalars().all()

# Удаление задачи


async def delete_task(tg_id, task_id):
    async with async_session() as session:
        task = await session.scalar(select(Task).where(Task.tg_id == tg_id, Task.id == task_id))
        await session.delete(task)
        await session.commit()

# Обновление задачи


async def update_task(tg_id, task_id, new_text):
    async with async_session() as session:
        async with session.begin():
            stmt = update(Task).where(Task.tg_id == tg_id,
                                      Task.id == task_id).values({Task.text: new_text})
            await session.execute(stmt)
            await session.commit()
