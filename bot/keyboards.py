from aiogram import types

def get_main_keyboard():
    """
    Создает и возвращает основную reply-клавиатуру.
    """
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="/categories"),
                types.KeyboardButton(text="/products")
            ],
            [
                types.KeyboardButton(text="/help")
            ]
        ],
        resize_keyboard=True
    )

def get_admin_keyboard():
    """
    Создает и возвращает inline-клавиатуру для администраторов.
    """
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Создать категорию",
                    callback_data="create_category_btn"
                )
            ]
        ]
    )