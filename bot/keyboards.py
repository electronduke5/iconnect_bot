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
            ],
            [
                types.InlineKeyboardButton(
                    text="Создать продукт",
                    callback_data="create_product_btn"
                )
            ]
        ]
    )

def get_sale_price_keyboard():
    """
    Создает inline-клавиатуру с кнопкой "Пропустить".
    """
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Пропустить",
                    callback_data="skip_sale_price"
                )
            ]
        ]
    )

def get_conditions_keyboard(conditions):
    """
    Создает inline-клавиатуру из списка состояний.
    """
    buttons = [
        types.InlineKeyboardButton(text=cond['name'], callback_data=f"condition_{cond['id']}")
        for cond in conditions
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[buttons])
    return keyboard

def get_categories_keyboard(categories):
    """
    Создает inline-клавиатуру из списка категорий.
    """
    buttons = [
        types.InlineKeyboardButton(text=cat['name'], callback_data=f"category_{cat['id']}")
        for cat in categories
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[buttons])
    return keyboard