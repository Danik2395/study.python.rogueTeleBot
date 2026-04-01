import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup

from bot.user_handler import urt
from core.rogue_interface import RogueInterface

load_dotenv()
TOKEN = getenv("BOT_TOKEN") or ""


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_router(urt)

    rogue_interface = await RogueInterface.create()

    # The RogueInterface instance would be available in the rogue_interface kwarg
    await dp.start_polling(bot, rogue_interface=rogue_interface)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
