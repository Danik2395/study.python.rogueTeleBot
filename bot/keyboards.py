from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.presets import Button

def get_keyboard(buttons: list[Button]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in buttons:
        builder.button(
            text=btn.label,
            callback_data=btn.action
        )

    builder.adjust(1)

    return builder.as_markup()
