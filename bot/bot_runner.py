import asyncio
import logging
import sys
from os import environ
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.user_handler import UserController
from core.rogue_interface import RogueInterface

load_dotenv()
TOKEN = environ["BOT_TOKEN"]


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="help", description="Помощь")
    ]
    await bot.set_my_commands(commands)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)

    dp = Dispatcher()

    rogue_interface = await RogueInterface.create()
    user_controller = UserController(bot, rogue_interface)

    user_router = user_controller.router
    dp.include_router(user_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
