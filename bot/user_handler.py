import asyncio
from pprint import pprint
import random

from aiogram import Router, types, Bot, exceptions
from aiogram.filters import Command

from data.presets import FTEXT
from core.rogue_interface import RogueInterface, process_action, NoAction
from bot.keyboards import get_keyboard



class UserController:
    def __init__(self, bot: Bot, interface: RogueInterface) -> None:
        self.bot = bot
        self.interface = interface
        self.router = Router(name="User_Router")

        self._register_handlers()

        self.lock_users: set[int] = set()
        self.lock_messages: set[int] = set()

    def _register_handlers(self) -> None:
        """
        Method replaces decorators
        """

        # Need to be highier then ignore command
        self.router.message(Command("start"))(self.cmd_start)
        self.router.message(Command("expanse"))(self.cmd_expanse)
        # self.router.message(Command("help"))(self.cmd_help)
        self.router.message(~Command("start"))(self.cmd_ignore)
        self.router.callback_query()(self.callback_handler)


    async def _update_bot_message(self, user_id: int, text: str,
                                  keyboard: types.InlineKeyboardMarkup,
                                  map_photo: bytes | None = None) -> None:
        try:
            ui_message = await self.interface.get_ui_message_id(user_id)
        except ValueError:
            ui_message = 0

        if ui_message:
            try:
                if map_photo is not None:
                    await self.bot.edit_message_media(
                        chat_id=user_id,
                        message_id=ui_message,
                        media=types.InputMediaPhoto(
                            media=types.BufferedInputFile(map_photo, filename="map.png"),
                            caption=text
                        ),
                        reply_markup=keyboard
                    )
                else:
                    await self.bot.edit_message_text(
                        chat_id=user_id,
                        message_id=ui_message,
                        text=text,
                        reply_markup=keyboard
                    )
                return
            except (exceptions.TelegramBadRequest, exceptions.TelegramForbiddenError) as e:
            # except Exception as e:
                asyncio.create_task(self._delete_bot_message(message_id=ui_message, chat_id=user_id, delay=2))

        if map_photo is not None:
            new_ui_message = await self.bot.send_photo(
                chat_id=user_id,
                photo=types.BufferedInputFile(map_photo, filename="map.png"),
                caption=text,
                reply_markup=keyboard
            )
        else:
            new_ui_message = await self.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=keyboard
            )
        await self.interface.save_ui_message_id(user_id, new_ui_message.message_id)

    async def _delete_object_message(self, *, message: types.Message, delay: int = 0, warning_message: types.Message | None = None) -> None:
        self.lock_messages.add(message.message_id)
        await asyncio.sleep(delay)
        try:
            await message.delete()
            if warning_message is not None:
                await warning_message.delete()
        except:
            pass
        finally:
            msg_id = message.message_id
            self.lock_messages.discard(msg_id)

    async def _delete_bot_message(self, *, message_id: int, delay: int = 0, chat_id: int) -> None:
        self.lock_messages.add(message_id)
        await asyncio.sleep(delay)
        try:
            await self.bot.delete_message(message_id=message_id, chat_id=chat_id)
        except:
            pass
        finally:
            self.lock_messages.discard(message_id)

    # === Commands ===

    async def cmd_start(self, message: types.Message) -> None: # TODO: нужно переделать, чтобы оно сразу показывало стартовое сообщение, а через пару секунд только кнопки
        if message.from_user is None: return
        user_id = message.from_user.id

        if user_id in self.lock_users:
            await self._delete_object_message(message=message)
            return
        self.lock_users.add(user_id)
        try: # To exactly unlock the user
            contract = await self.interface.cmd_start(user_id)

            keyboard = get_keyboard(contract.buttons)
            cmd_start_text = random.choice(FTEXT["cmd_start"])

            asyncio.create_task(self._delete_object_message(message=message, delay=3))
            try:
                ui_message = await self.interface.get_ui_message_id(user_id)
                await self._delete_bot_message(message_id=ui_message, chat_id=user_id)

            except ValueError:
                pass

            ui_message = await self.bot.send_message(
                chat_id=user_id,
                text=cmd_start_text,
                # reply_markup=keyboard
            )
            await asyncio.sleep(2)

            await self.bot.edit_message_text(
                        chat_id=user_id,
                        message_id=ui_message.message_id,
                        text=cmd_start_text,
                        reply_markup=keyboard
                    )

            await self.interface.save_ui_message_id(user_id, ui_message.message_id)
        finally:
            self.lock_users.discard(user_id)
            self.lock_messages.discard(message.message_id)

    async def cmd_expanse(self, message: types.Message) -> None:
        if message.from_user is None: return
        user_id = message.from_user.id

        if user_id in self.lock_users:
            await self._delete_object_message(message=message)
            return
        self.lock_users.add(user_id)

        try: # To exactly unlock the user
            contract = await self.interface.goto_menu_expanse(user_id)

            keyboard = get_keyboard(contract.buttons)
            menu_text = contract.text

            await self._delete_object_message(message=message)
            await self._update_bot_message(user_id, menu_text, keyboard, contract.map_photo)
        finally:
            self.lock_users.discard(user_id)
            self.lock_messages.discard(message.message_id)

    # async def cmd_help(self, message: types.Message) -> None:
    #
    #     if message.from_user is None: return
    #     user_id = message.from_user.id
    #     contract = await self.interface.goto_menu_help(user_id)
    #
    #     keyboard = get_keyboard(contract.buttons)
    #     help_text = contract.text
    #
    #     await self._delete_object_message(message=message)
    #     await self._update_bot_message(user_id, help_text, keyboard, contract.map_photo)

    async def cmd_ignore(self, message: types.Message) -> None:
        ignore_message = random.choice(FTEXT["ignore_message"])
        warning_message = await message.answer(ignore_message)
        await self._delete_object_message(message=message, delay=2, warning_message=warning_message)


    # === Callback Processing ===

    async def callback_handler(self, callback: types.CallbackQuery) -> None:
        user_id = callback.from_user.id
        message_id = callback.message.message_id # type: ignore
        if user_id in self.lock_users or message_id in self.lock_messages:
            await callback.answer()
            return
        self.lock_users.add(user_id)

        try:
            action = callback.data

            contract = await process_action(user_id, action, self.interface)

            keyboard = get_keyboard(contract.buttons)

            pprint(contract)
            await self._update_bot_message(user_id, contract.text, keyboard, contract.map_photo)

        except NoAction:
            pass

        finally:
            await callback.answer()
            self.lock_users.discard(user_id)
