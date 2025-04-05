import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import bot, router


async def main():
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())