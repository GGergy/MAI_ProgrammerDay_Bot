import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, enums
# from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from utils.config import settings
from routers import auth, shared


# storage=RedisStorage.from_url(settings.redis_url)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
# Роутер shared включается последним!!!
dp.include_routers(auth.router, shared.router)

bot = Bot(token=settings.tg_bot_token, default=DefaultBotProperties(parse_mode=enums.ParseMode.HTML))


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO, filename=settings.log_file, filemode="w", encoding="utf-8", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(main())
