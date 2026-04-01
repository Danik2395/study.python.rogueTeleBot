import asyncio
from pprint import pprint
import random
random.seed(42)

from aiogram import Bot, Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, message, pre_checkout_query
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Filter, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from data.presets import FTEXT, Contract, Button
from core.rogue_interface import RogueInterface, process_action

urt = Router(name="User_Router")


def get_keyboard(buttons: list[Button]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in buttons:
        builder.button(
            text=btn.label,
            callback_data=btn.action
        )

    builder.adjust(1)

    return builder.as_markup()


# === Commands ===

@urt.message(Command("start"), F.from_user)
async def cmd_start(message: types.Message, rogue_interface: RogueInterface) -> None:
    if message.from_user is None: return
    user_id = message.from_user.id

    contract = await rogue_interface.cmd_start(user_id)

    keyboard = get_keyboard(contract.buttons)

    cmd_start_text = FTEXT["cmd_start"]
    await message.answer(cmd_start_text, reply_markup=keyboard)

# Need to be highier then ignore command
@urt.message(Command("help"), F.from_user)
async def cmd_help(message: types.Message) -> None:
    await message.answer(FTEXT["help_message"])

@urt.message(~Command("start"), F.from_user)
async def ignore_text(message: types.Message) -> None:
    await message.answer(FTEXT["ignore_message"])

# === Callback Processing ===

@urt.callback_query(F.from_user)
async def callback_handler(callback: types.CallbackQuery, rogue_interface: RogueInterface) -> None:
    user_id = callback.from_user.id
    action = callback.data

    contract = await process_action(user_id, action, rogue_interface)

    keyboard = get_keyboard(contract.buttons)

    pprint(contract)
    await callback.message.answer(contract.text, reply_markup=keyboard) #type: ignore
    await callback.answer()

