from aiogram import Dispatcher
import logging
import asyncio

from bot import bot
from app.handlers import router
from app.database.models import async_main

dp = Dispatcher()

# Запуск бота


async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
