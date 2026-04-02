import asyncio
from pprint import pprint
import random
random.seed(42)

from aiogram import Router, F, types, Bot, exceptions
from aiogram.enums import ParseMode
from aiogram.types import Message, message, pre_checkout_query, user
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Filter, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

from data.presets import FTEXT
from core.rogue_interface import RogueInterface, process_action, NoAction
from bot.keyboards import get_keyboard



class UserController:
    def __init__(self, bot: Bot, interface: RogueInterface) -> None:
        self.bot = bot
        self.interface = interface
        self.router = Router(name="User_Router")

        self._register_handlers()

    def _register_handlers(self) -> None:
        """
        Method replaces decorators
        """

        # Need to be highier then ignore command
        self.router.message(Command("start"))(self.cmd_start)
        self.router.message(Command("help"))(self.cmd_help)
        self.router.message(~Command("start"))(self.cmd_ignore)
        self.router.callback_query()(self.callback_handler)


    async def _update_bot_message(self, user_id: int, text: str, keyboard: types.InlineKeyboardMarkup) -> None:
        ui_message: int = 0
        try:
            ui_message = await self.interface.get_ui_message_id(user_id)

            await self.bot.edit_message_text(
                chat_id=user_id,
                message_id=ui_message,
                text=text,
                reply_markup=keyboard
            )
            return

        except (ValueError, exceptions.TelegramBadRequest, exceptions.TelegramForbiddenError):
            await self._delete_bot_message(message_id=ui_message, chat_id=user_id)
            pass

        new_ui_message = await self.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=keyboard
                )

        await self.interface.save_ui_message_id(user_id, new_ui_message.message_id)

    async def _delete_object_message(self, *, message: types.Message, delay: int = 0, warning_message: types.Message | None = None) -> None:
        await asyncio.sleep(delay)
        try:
            await message.delete()
            if warning_message is not None:
                await warning_message.delete()
        except:
            pass

    async def _delete_bot_message(self, *, message_id: int, delay: int = 0, chat_id: int) -> None:
        await asyncio.sleep(delay)
        try:
            await self.bot.delete_message(message_id=message_id, chat_id=chat_id)
        except:
            pass

    # === Commands ===

    async def cmd_start(self, message: types.Message) -> None:
        if message.from_user is None: return
        user_id = message.from_user.id

        contract = await self.interface.cmd_start(user_id)

        keyboard = get_keyboard(contract.buttons)
        cmd_start_text = FTEXT["cmd_start"]

        # await message.answer(cmd_start_text, reply_markup=keyboard)
        await self._delete_object_message(message=message,)
        await self._update_bot_message(user_id, cmd_start_text, keyboard)

    async def cmd_help(self, message: types.Message) -> None:
        # await message.answer(FTEXT["help_message"])

        if message.from_user is None: return
        user_id = message.from_user.id
        contract = await self.interface.goto_menu_help(user_id)

        keyboard = get_keyboard(contract.buttons)
        help_text = FTEXT["help_message"]

        await self._delete_object_message(message=message)
        await self._update_bot_message(user_id, help_text, keyboard)

    async def cmd_ignore(self, message: types.Message) -> None:
        warning_message = await message.answer(FTEXT["ignore_message"])
        await self._delete_object_message(message=message, delay=2, warning_message=warning_message)


    # === Callback Processing ===

    async def callback_handler(self, callback: types.CallbackQuery) -> None:
        try:
            user_id = callback.from_user.id
            action = callback.data

            contract = await process_action(user_id, action, self.interface)

            keyboard = get_keyboard(contract.buttons)

            pprint(contract)
            # await callback.message.answer(contract.text, reply_markup=keyboard) #type: ignore
            await self._update_bot_message(user_id, contract.text, keyboard)
        except NoAction:
            pass

        await callback.answer()
