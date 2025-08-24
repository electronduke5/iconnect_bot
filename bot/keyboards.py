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

def get_yes_no_keyboard(callback_prefix):
    """
    Создает inline-клавиатуру с кнопками "Да" и "Нет".
    """
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Да",
                    callback_data=f"{callback_prefix}_yes"
                ),
                types.InlineKeyboardButton(
                    text="Нет",
                    callback_data=f"{callback_prefix}_no"
                )
            ]
        ]
    )

def get_brands_keyboard(brands):
    """
    Создает inline-клавиатуру из списка брендов.
    """
    buttons = [
        types.InlineKeyboardButton(text=brand['name'], callback_data=f"brand_{brand['id']}")
        for brand in brands
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
    return keyboard

def get_models_keyboard(models):
    """
    Создает inline-клавиатуру из списка моделей для выбранного бренда.
    """
    buttons = [
        types.InlineKeyboardButton(text=model['name'], callback_data=f"model_{model['id']}")
        for model in models
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[[button] for button in buttons])
    return keyboard

def get_colors_keyboard_from_db(colors):
    """
    Создает inline-клавиатуру из списка цветов из базы данных.
    """
    buttons = [
        types.InlineKeyboardButton(text=color['name'], callback_data=f"color_{color['id']}")
        for color in colors
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3, inline_keyboard=[buttons[i:i+3] for i in range(0, len(buttons), 3)])
    return keyboard

def get_storage_keyboard(storage_capacities):
    """
    Создает inline-клавиатуру из списка объемов памяти.
    """
    buttons = [
        types.InlineKeyboardButton(text=f"{storage['capacity_gb']} ГБ", callback_data=f"storage_{storage['id']}")
        for storage in storage_capacities
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3, inline_keyboard=[buttons[i:i+3] for i in range(0, len(buttons), 3)])
    return keyboard

def get_markets_keyboard(markets):
    """
    Создает inline-клавиатуру из списка рынков.
    """
    buttons = [
        types.InlineKeyboardButton(text=market['name'], callback_data=f"market_{market['id']}")
        for market in markets
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
    return keyboard

def get_skip_keyboard(callback_data):
    """
    Создает inline-клавиатуру с кнопкой "Пропустить".
    """
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Пропустить",
                    callback_data=callback_data
                )
            ]
        ]
    )

def get_menu_keyboard():
    """
    Создает главную inline-клавиатуру меню.
    """
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📦 Товары",
                    callback_data="products_submenu"
                ),
                types.InlineKeyboardButton(
                    text="📱 Телефоны",
                    callback_data="phones_submenu"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="💰 Прибыль",
                    callback_data="menu_profit"
                ),
                types.InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="menu_stats"
                )
            ]
        ]
    )

def get_item_navigation_keyboard(item_type, current_index, total_count, item_id=None, is_admin=False):
    """
    Создает клавиатуру для навигации по товарам/телефонам.
    item_type: 'products' или 'phones'
    current_index: текущий индекс товара (0-based)
    total_count: общее количество товаров
    item_id: ID товара для действий (опционально)
    is_admin: True если пользователь администратор
    """
    keyboard = []
    
    # Первая строка: Назад в меню
    keyboard.append([
        types.InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="back_to_menu"
        )
    ])
    
    # Вторая строка: Добавить товар/телефон (только для админов)
    if is_admin:
        add_text = "➕ Добавить телефон" if item_type == "phones" else "➕ Добавить товар"
        add_callback = "add_phone_from_menu" if item_type == "phones" else "add_product_from_menu"
        keyboard.append([
            types.InlineKeyboardButton(
                text=add_text,
                callback_data=add_callback
            )
        ])
    
    # Третья строка: Действия с товаром (если есть item_id и пользователь админ)
    if item_id and is_admin:
        keyboard.append([
            types.InlineKeyboardButton(
                text="✏️ Изменить товар",
                callback_data=f"edit_item:{item_type}:{item_id}"
            ),
            types.InlineKeyboardButton(
                text="💰 Продать товар",
                callback_data=f"sell_item:{item_type}:{item_id}"
            )
        ])
    
    # Четвертая строка: Навигация влево/вправо (если больше одного товара)
    if total_count > 1:
        nav_buttons = []
        
        # Кнопка "предыдущий" (показываем только если не первый)
        if current_index > 0:
            nav_buttons.append(
                types.InlineKeyboardButton(
                    text="◀️ Предыдущий",
                    callback_data=f"nav_{item_type}:{current_index - 1}"
                )
            )
        
        # Кнопка "следующий" (показываем только если не последний)
        if current_index < total_count - 1:
            nav_buttons.append(
                types.InlineKeyboardButton(
                    text="Следующий ▶️",
                    callback_data=f"nav_{item_type}:{current_index + 1}"
                )
            )
        
        if nav_buttons:
            keyboard.append(nav_buttons)
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_to_menu_keyboard():
    """
    Создает простую клавиатуру с кнопкой возврата в меню.
    """
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад в меню",
                    callback_data="back_to_menu"
                )
            ]
        ]
    )

def get_success_menu_keyboard(item_type):
    """
    Создает клавиатуру после успешного создания товара/телефона.
    item_type: 'product' или 'phone'
    """
    add_text = "➕ Добавить еще телефон" if item_type == "phone" else "➕ Добавить еще товар"
    add_callback = "add_another_phone" if item_type == "phone" else "add_another_product"
    
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🏪 Меню",
                    callback_data="back_to_menu"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=add_text,
                    callback_data=add_callback
                )
            ]
        ]
    )

def get_products_submenu_keyboard(is_admin=False):
    """
    Создает подменю для товаров.
    """
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="📦 Товары в наличии",
                callback_data="products_available"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="💰 Проданные товары",
                callback_data="products_sold"
            )
        ]
    ]
    
    # Добавляем кнопку для админов
    if is_admin:
        keyboard.append([
            types.InlineKeyboardButton(
                text="➕ Добавить товар",
                callback_data="add_product_from_menu"
            )
        ])
    
    # Кнопка назад
    keyboard.append([
        types.InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="back_to_menu"
        )
    ])
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_phones_submenu_keyboard(is_admin=False):
    """
    Создает подменю для телефонов.
    """
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="📱 Телефоны в наличии",
                callback_data="phones_available"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="💰 Проданные телефоны",
                callback_data="phones_sold"
            )
        ]
    ]
    
    # Добавляем кнопку для админов
    if is_admin:
        keyboard.append([
            types.InlineKeyboardButton(
                text="➕ Добавить телефон",
                callback_data="add_phone_from_menu"
            )
        ])
    
    # Кнопка назад
    keyboard.append([
        types.InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="back_to_menu"
        )
    ])
    
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)