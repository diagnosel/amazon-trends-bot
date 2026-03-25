from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/daily")],
            [KeyboardButton(text="/keyword portable blender")],
        ],
        resize_keyboard=True,
    )

