from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_to_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_start")]
    ])

def back_to_help_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_help")]
    ])
