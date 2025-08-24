from aiogram import Dispatcher, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import CategoryCreation, ProductCreation, SaleProcess
from keyboards import get_main_keyboard, get_admin_keyboard, get_sale_price_keyboard, get_conditions_keyboard, \
    get_categories_keyboard, get_yes_no_keyboard, get_brands_keyboard, get_models_keyboard, \
    get_colors_keyboard_from_db, get_storage_keyboard, get_markets_keyboard, get_skip_keyboard, get_menu_keyboard, \
    get_item_navigation_keyboard, get_back_to_menu_keyboard, get_success_menu_keyboard, \
    get_products_submenu_keyboard, get_phones_submenu_keyboard
from filters import IsAdminFilter
from functools import partial
import asyncpg
from decimal import Decimal


# --- Функции регистрации обработчиков ---
def register_handlers(dp: Dispatcher, admin_ids: list, db_pool):
    IsAdminFilter.admin_ids = admin_ids

    # Основные обработчики
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_help, Command("help"))
    dp.message.register(handle_menu, Command("menu"))
    dp.message.register(partial(list_categories, db_pool=db_pool), Command("categories"))
    dp.message.register(partial(list_products, db_pool=db_pool), Command("products"))
    
    # Обработчики меню
    dp.callback_query.register(partial(handle_menu_all_products, db_pool=db_pool),
                               lambda c: c.data == "menu_all_products")
    dp.callback_query.register(partial(handle_menu_all_phones, db_pool=db_pool),
                               lambda c: c.data == "menu_all_phones")
    dp.callback_query.register(partial(handle_menu_profit, db_pool=db_pool),
                               lambda c: c.data == "menu_profit")
    dp.callback_query.register(partial(handle_menu_stats, db_pool=db_pool),
                               lambda c: c.data == "menu_stats")
    
    # Обработчики подменю
    dp.callback_query.register(partial(handle_products_submenu, db_pool=db_pool),
                               lambda c: c.data == "products_submenu")
    dp.callback_query.register(partial(handle_phones_submenu, db_pool=db_pool),
                               lambda c: c.data == "phones_submenu")
    dp.callback_query.register(partial(handle_products_available, db_pool=db_pool),
                               lambda c: c.data == "products_available")
    dp.callback_query.register(partial(handle_products_sold, db_pool=db_pool),
                               lambda c: c.data == "products_sold")
    dp.callback_query.register(partial(handle_phones_available, db_pool=db_pool),
                               lambda c: c.data == "phones_available")
    dp.callback_query.register(partial(handle_phones_sold, db_pool=db_pool),
                               lambda c: c.data == "phones_sold")
    
    # Обработчики навигации
    dp.callback_query.register(partial(handle_back_to_menu, db_pool=db_pool),
                               lambda c: c.data == "back_to_menu")
    dp.callback_query.register(partial(handle_nav_products, db_pool=db_pool),
                               lambda c: c.data.startswith("nav_products:"))
    dp.callback_query.register(partial(handle_nav_phones, db_pool=db_pool),
                               lambda c: c.data.startswith("nav_phones:"))
    dp.callback_query.register(partial(handle_edit_item, db_pool=db_pool),
                               lambda c: c.data.startswith("edit_item:"))
    dp.callback_query.register(partial(handle_sell_item, db_pool=db_pool),
                               lambda c: c.data.startswith("sell_item:"))
    
    # Обработчики добавления товаров из меню навигации
    dp.callback_query.register(partial(handle_add_product_from_menu, db_pool=db_pool),
                               lambda c: c.data == "add_product_from_menu", IsAdminFilter())
    dp.callback_query.register(partial(handle_add_phone_from_menu, db_pool=db_pool),
                               lambda c: c.data == "add_phone_from_menu", IsAdminFilter())
    
    # Обработчики "Добавить еще" товары
    dp.callback_query.register(partial(handle_add_another_product, db_pool=db_pool),
                               lambda c: c.data == "add_another_product", IsAdminFilter())
    dp.callback_query.register(partial(handle_add_another_phone, db_pool=db_pool),
                               lambda c: c.data == "add_another_phone", IsAdminFilter())
    
    # Обработчик для процесса продажи
    dp.message.register(partial(handle_sale_price_input, db_pool=db_pool),
                        StateFilter(SaleProcess.waiting_for_sale_price), IsAdminFilter())

    # Обработчики для создания категории
    dp.callback_query.register(partial(handle_create_category_callback, db_pool=db_pool),
                               lambda c: c.data == "create_category_btn", IsAdminFilter())
    dp.message.register(partial(handle_category_name, db_pool=db_pool), StateFilter(CategoryCreation.waiting_for_name),
                        IsAdminFilter())

    # Обработчики для создания продукта
    dp.callback_query.register(partial(handle_create_product_callback, db_pool=db_pool),
                               lambda c: c.data == "create_product_btn", IsAdminFilter())
    dp.message.register(partial(handle_product_name, db_pool=db_pool), StateFilter(ProductCreation.waiting_for_name),
                        IsAdminFilter())
    dp.callback_query.register(partial(handle_product_category, db_pool=db_pool),
                               lambda c: c.data.startswith('category_'),
                               StateFilter(ProductCreation.waiting_for_category), IsAdminFilter())
    dp.message.register(partial(handle_product_purchase_price, db_pool=db_pool),
                        StateFilter(ProductCreation.waiting_for_purchase_price), IsAdminFilter())
    dp.callback_query.register(partial(handle_skip_sale_price, db_pool=db_pool), lambda c: c.data == 'skip_sale_price',
                               StateFilter(ProductCreation.waiting_for_quantity))
    dp.message.register(partial(handle_product_quantity, db_pool=db_pool),
                        StateFilter(ProductCreation.waiting_for_quantity), IsAdminFilter())
    dp.callback_query.register(partial(handle_product_condition, db_pool=db_pool),
                               lambda c: c.data.startswith('condition_'),
                               StateFilter(ProductCreation.waiting_for_condition), IsAdminFilter())
    
    # Специальные обработчики для телефонов (расширенный flow)
    dp.callback_query.register(partial(handle_brand_selection, db_pool=db_pool),
                               lambda c: c.data.startswith('brand_'),
                               StateFilter(ProductCreation.waiting_for_brand), IsAdminFilter())
    dp.callback_query.register(partial(handle_model_selection, db_pool=db_pool),
                               lambda c: c.data.startswith('model_'),
                               StateFilter(ProductCreation.waiting_for_model), IsAdminFilter())
    dp.callback_query.register(partial(handle_storage_selection, db_pool=db_pool),
                               lambda c: c.data.startswith('storage_'),
                               StateFilter(ProductCreation.waiting_for_storage_capacity), IsAdminFilter())
    dp.callback_query.register(partial(handle_market_selection, db_pool=db_pool),
                               lambda c: c.data.startswith('market_'),
                               StateFilter(ProductCreation.waiting_for_market), IsAdminFilter())
    dp.callback_query.register(partial(handle_color_selection, db_pool=db_pool),
                               lambda c: c.data.startswith('color_'),
                               StateFilter(ProductCreation.waiting_for_color), IsAdminFilter())
    dp.message.register(partial(handle_battery_health, db_pool=db_pool),
                        StateFilter(ProductCreation.waiting_for_battery_health), IsAdminFilter())
    dp.callback_query.register(partial(handle_repaired, db_pool=db_pool),
                               lambda c: c.data.startswith('repaired_'),
                               StateFilter(ProductCreation.waiting_for_repaired), IsAdminFilter())
    dp.callback_query.register(partial(handle_full_kit, db_pool=db_pool),
                               lambda c: c.data.startswith('full_kit_'),
                               StateFilter(ProductCreation.waiting_for_full_kit), IsAdminFilter())
    
    # Обработчики для IMEI и серийного номера
    dp.message.register(partial(handle_imei_input, db_pool=db_pool),
                        StateFilter(ProductCreation.waiting_for_imei), IsAdminFilter())
    dp.callback_query.register(partial(handle_imei_skip, db_pool=db_pool),
                               lambda c: c.data == 'skip_imei',
                               StateFilter(ProductCreation.waiting_for_imei), IsAdminFilter())
    dp.message.register(partial(handle_serial_input, db_pool=db_pool),
                        StateFilter(ProductCreation.waiting_for_serial_number), IsAdminFilter())
    dp.callback_query.register(partial(handle_serial_skip, db_pool=db_pool),
                               lambda c: c.data == 'skip_serial',
                               StateFilter(ProductCreation.waiting_for_serial_number), IsAdminFilter())


# --- Основные обработчики ---
async def handle_start(message: types.Message):
    await message.reply("Привет! Я бот для управления складом. Используйте /help для списка команд.",
                        reply_markup=get_main_keyboard())


async def handle_help(message: types.Message):
    help_text = (
        "Список доступных команд:\n\n"
        "*Общие команды:*\n"
        "/start \\- Начать работу с ботом и получить основную клавиатуру\\.\n"
        "/help \\- Показать это сообщение\\.\n"
        "/menu \\- Показать главное меню с быстрым доступом\\.\n"
        "/categories \\- Показать список всех категорий\\.\n"
        "/products \\- Показать список всех товаров\\.\n\n"
        "*Команды для администраторов:*\n"
        "Чтобы добавить категорию или продукт, нажмите соответствующие кнопки в меню\\."
    )

    if message.from_user.id in IsAdminFilter.admin_ids:
        await message.reply(help_text, reply_markup=get_admin_keyboard(), parse_mode='MarkdownV2')
    else:
        help_text = help_text.replace(
            "*Команды для администраторов:*\nЧтобы добавить категорию или продукт, нажмите соответствующие кнопки в меню\\.",
            "")
        await message.reply(help_text, parse_mode='MarkdownV2')

async def handle_menu(message: types.Message):
    await message.reply("🏪 **Главное меню магазина**\n\nВыберите действие:", 
                       reply_markup=get_menu_keyboard(), parse_mode='Markdown')


# --- Обработчики для создания категории ---
async def handle_create_category_callback(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await callback_query.message.reply("Пожалуйста, введите название для новой категории:")
    await state.set_state(CategoryCreation.waiting_for_name)


async def handle_category_name(message: types.Message, state: FSMContext, db_pool):
    category_name = message.text.strip()
    if not category_name:
        await message.reply("Название не может быть пустым. Попробуйте еще раз.")
        return

    async with db_pool.acquire() as connection:
        async with connection.transaction():
            try:
                result = await connection.fetchrow(
                    "INSERT INTO categories (name) VALUES ($1) ON CONFLICT (name) DO NOTHING RETURNING id;",
                    category_name
                )
                if result:
                    await message.reply(f"Категория '{category_name}' (ID: {result['id']}) успешно добавлена.")
                else:
                    await message.reply(f"Категория '{category_name}' уже существует.")
            except Exception as e:
                await message.reply(f"Произошла ошибка при добавлении категории: {e}")
            finally:
                await state.clear()


# --- Обработчики для создания продукта ---
async def handle_create_product_callback(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    async with db_pool.acquire() as connection:
        categories = await connection.fetch("SELECT id, name FROM categories;")

    if not categories:
        await callback_query.message.reply("В базе нет ни одной категории. Добавьте их, прежде чем создавать продукт.")
        await state.clear()
        return

    await callback_query.message.reply("Отлично, давайте добавим новый продукт. Выберите категорию товара:", 
                                       reply_markup=get_categories_keyboard(categories))
    await state.set_state(ProductCreation.waiting_for_category)


async def handle_product_name(message: types.Message, state: FSMContext, db_pool):
    await state.update_data(name=message.text.strip())
    
    # После ввода названия переходим к закупочной цене (категория уже выбрана)
    await message.reply("Введите закупочную цену (например, 150.50):")
    await state.set_state(ProductCreation.waiting_for_purchase_price)


async def handle_product_purchase_price(message: types.Message, state: FSMContext, db_pool):
    try:
        price = float(message.text.replace(',', '.'))
        await state.update_data(purchase_price=price)
        
        user_data = await state.get_data()
        is_phone = user_data.get('is_phone', False)
        
        if is_phone:
            # Для телефонов пропускаем цену продажи и переходим к выбору цвета из БД
            await state.update_data(sale_price=None)
            async with db_pool.acquire() as connection:
                colors = await connection.fetch("SELECT id, name FROM colors ORDER BY name;")

            if not colors:
                await message.reply("В базе нет цветов для выбора.")
                await state.clear()
                return

            await message.reply("Выберите цвет:", reply_markup=get_colors_keyboard_from_db(colors))
            await state.set_state(ProductCreation.waiting_for_color)
        else:
            # Для обычных товаров запрашиваем цену продажи
            await message.reply("Отлично! Теперь введите цену продажи (число) или нажмите 'Пропустить', если её нет:",
                                reply_markup=get_sale_price_keyboard())
            await state.set_state(ProductCreation.waiting_for_quantity)
    except ValueError:
        await message.reply("Неверный формат цены. Пожалуйста, введите число (например, 150.50).")


async def handle_skip_sale_price(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await state.update_data(sale_price=None)
    
    # Используем новую систему сообщений
    message = await send_new_message(
        callback_query.bot, 
        callback_query.from_user.id,
        "Пропускаем цену продажи. Теперь введите количество товара (целое число):"
    )
    await track_message_id(state, message.message_id)
    await state.set_state(ProductCreation.waiting_for_quantity)


async def handle_product_quantity(message: types.Message, state: FSMContext, db_pool):
    user_data = await state.get_data()

    # Если цена продажи ещё не установлена, получаем её из сообщения
    if 'sale_price' not in user_data:
        try:
            sale_price = float(message.text.replace(',', '.'))
            await state.update_data(sale_price=sale_price)
            await message.reply("Теперь введите количество товара (целое число):")
            return
        except ValueError:
            await message.reply("Неверный формат цены продажи. Пожалуйста, введите число или нажмите 'Пропустить'.")
            return

    try:
        quantity = int(message.text)
        await state.update_data(quantity=quantity)
        
        # Проверяем, это телефон или обычный товар
        user_data = await state.get_data()
        is_phone = user_data.get('is_phone', False)
        
        if is_phone:
            # Для телефонов переходим к выбору состояния (у телефонов остались поля color и condition)
            async with db_pool.acquire() as connection:
                conditions = await connection.fetch("SELECT id, name FROM conditions;")

            if not conditions:
                await message.reply("В базе нет ни одного состояния. Добавьте их, прежде чем создавать продукт.")
                await state.clear()
                return

            await message.reply("Выберите состояние товара:", reply_markup=get_conditions_keyboard(conditions))
            await state.set_state(ProductCreation.waiting_for_condition)
        else:
            # Для обычных товаров сразу сохраняем в базу (без цвета и состояния)
            await save_product_to_db(message, state, db_pool)
        
    except ValueError:
        await message.reply("Неверный формат количества. Пожалуйста, введите целое число.")




async def handle_product_condition(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    condition_id = int(callback_query.data.split('_')[1])
    
    # Получаем название состояния
    async with db_pool.acquire() as connection:
        condition_result = await connection.fetchrow("SELECT name FROM conditions WHERE id = $1", condition_id)
    
    if not condition_result:
        await callback_query.message.reply("Ошибка: состояние не найдено.")
        await state.clear()
        return
        
    condition_name = condition_result['name']
    await state.update_data(condition_id=condition_id, condition_name=condition_name)
    
    user_data = await state.get_data()
    is_phone = user_data.get('is_phone', False)
    is_used = condition_name.lower() == "б/у"
    
    # Этот обработчик теперь используется только для телефонов
    if not is_phone:
        await callback_query.message.reply("Ошибка: состояние не должно запрашиваться для обычных товаров.")
        await state.clear()
        return
    
    if is_used:
        # Для телефонов в состоянии Б/У запрашиваем дополнительные поля
        await callback_query.message.reply("Введите здоровье батареи в процентах (например, 85):")
        await state.set_state(ProductCreation.waiting_for_battery_health)
    else:
        # Для телефонов в хорошем состоянии устанавливаем дефолтные значения и завершаем
        await state.update_data(
            battery_health=100,
            repaired=False,
            full_kit=True,
            quantity=1  # У телефонов всегда количество = 1
        )
        await save_phone_to_db(callback_query.message, state, db_pool)


async def handle_product_category(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    category_id = int(callback_query.data.split('_')[1])
    
    # Получаем название категории для определения типа продукта
    async with db_pool.acquire() as connection:
        category_result = await connection.fetchrow("SELECT name FROM categories WHERE id = $1", category_id)
        
    if not category_result:
        error_msg = await send_new_message(callback_query.bot, callback_query.message.chat.id, "Ошибка: категория не найдена.")
        await track_message_id(state, error_msg.message_id)
        await state.clear()
        return
        
    category_name = category_result['name']
    is_phone = (category_name.lower() == "телефоны")
    
    # Сохраняем информацию о категории и типе продукта
    await state.update_data(
        category_id=category_id,
        category_name=category_name,
        is_phone=is_phone
    )
    
    if is_phone:
        # Для телефонов сразу устанавливаем название как "Телефон" и переходим к выбору бренда
        await state.update_data(name="Телефон")
        
        async with db_pool.acquire() as connection:
            brands = await connection.fetch("SELECT id, name FROM brands ORDER BY name;")
            
        if not brands:
            error_msg = await send_new_message(callback_query.bot, callback_query.message.chat.id, "В базе нет брендов. Добавьте их прежде чем создавать телефон.")
            await track_message_id(state, error_msg.message_id)
            await state.clear()
            return
            
        new_msg = await send_new_message(callback_query.bot, callback_query.message.chat.id, "Выберите бренд телефона:", reply_markup=get_brands_keyboard(brands))
        await track_message_id(state, new_msg.message_id)
        await state.set_state(ProductCreation.waiting_for_brand)
    else:
        # Для обычных товаров сначала запрашиваем название
        new_msg = await send_new_message(callback_query.bot, callback_query.message.chat.id, "Введите название товара:")
        await track_message_id(state, new_msg.message_id)
        await state.set_state(ProductCreation.waiting_for_name)


# --- Специальные обработчики для телефонов (новый расширенный flow) ---
async def handle_brand_selection(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    brand_id = int(callback_query.data.split('_')[1])
    
    # Получаем название бренда
    async with db_pool.acquire() as connection:
        brand_result = await connection.fetchrow("SELECT name FROM brands WHERE id = $1", brand_id)
        
    if not brand_result:
        await callback_query.message.reply("Ошибка: бренд не найден.")
        await state.clear()
        return
        
    await state.update_data(brand_id=brand_id, brand_name=brand_result['name'])
    
    # Получаем модели для выбранного бренда
    async with db_pool.acquire() as connection:
        models = await connection.fetch("SELECT id, name FROM models WHERE brand_id = $1 ORDER BY name;", brand_id)
        
    if not models:
        await callback_query.message.reply(f"Для бренда {brand_result['name']} нет моделей в базе данных.")
        await state.clear()
        return
        
    await callback_query.message.reply("Выберите модель:", reply_markup=get_models_keyboard(models))
    await state.set_state(ProductCreation.waiting_for_model)

async def handle_model_selection(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    model_id = int(callback_query.data.split('_')[1])
    
    # Получаем название модели
    async with db_pool.acquire() as connection:
        model_result = await connection.fetchrow("SELECT name FROM models WHERE id = $1", model_id)
        
    if not model_result:
        await callback_query.message.reply("Ошибка: модель не найдена.")
        await state.clear()
        return
        
    await state.update_data(model_id=model_id, model_name=model_result['name'])
    
    # Получаем объемы памяти
    async with db_pool.acquire() as connection:
        storage_capacities = await connection.fetch("SELECT id, capacity_gb FROM storage_capacities ORDER BY capacity_gb;")
        
    if not storage_capacities:
        await callback_query.message.reply("В базе нет объемов памяти.")
        await state.clear()
        return
        
    await callback_query.message.reply("Выберите объем памяти:", reply_markup=get_storage_keyboard(storage_capacities))
    await state.set_state(ProductCreation.waiting_for_storage_capacity)

async def handle_storage_selection(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    storage_id = int(callback_query.data.split('_')[1])
    
    # Получаем объем памяти
    async with db_pool.acquire() as connection:
        storage_result = await connection.fetchrow("SELECT capacity_gb FROM storage_capacities WHERE id = $1", storage_id)
        
    if not storage_result:
        await callback_query.message.reply("Ошибка: объем памяти не найден.")
        await state.clear()
        return
        
    await state.update_data(storage_capacity_id=storage_id, storage_gb=storage_result['capacity_gb'])
    
    # Получаем рынки
    async with db_pool.acquire() as connection:
        markets = await connection.fetch("SELECT id, name FROM markets ORDER BY name;")
        
    if not markets:
        await callback_query.message.reply("В базе нет рынков.")
        await state.clear()
        return
        
    await callback_query.message.reply("Выберите рынок:", reply_markup=get_markets_keyboard(markets))
    await state.set_state(ProductCreation.waiting_for_market)

async def handle_market_selection(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    market_id = int(callback_query.data.split('_')[1])
    
    # Получаем название рынка
    async with db_pool.acquire() as connection:
        market_result = await connection.fetchrow("SELECT name FROM markets WHERE id = $1", market_id)
        
    if not market_result:
        await callback_query.message.reply("Ошибка: рынок не найден.")
        await state.clear()
        return
        
    await state.update_data(market_id=market_id, market_name=market_result['name'])
    await callback_query.message.reply("Введите закупочную цену (например, 150.50):")
    await state.set_state(ProductCreation.waiting_for_purchase_price)

async def handle_color_selection(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    color_id = int(callback_query.data.split('_')[1])
    
    # Получаем название цвета
    async with db_pool.acquire() as connection:
        color_result = await connection.fetchrow("SELECT name FROM colors WHERE id = $1", color_id)
        
    if not color_result:
        await callback_query.message.reply("Ошибка: цвет не найден.")
        await state.clear()
        return
        
    await state.update_data(color_id=color_id, color_name=color_result['name'])
    
    # Получаем состояния
    async with db_pool.acquire() as connection:
        conditions = await connection.fetch("SELECT id, name FROM conditions;")

    if not conditions:
        await callback_query.message.reply("В базе нет ни одного состояния. Добавьте их, прежде чем создавать продукт.")
        await state.clear()
        return

    await callback_query.message.reply("Выберите состояние товара:", reply_markup=get_conditions_keyboard(conditions))
    await state.set_state(ProductCreation.waiting_for_condition)

async def handle_battery_health(message: types.Message, state: FSMContext, db_pool):
    try:
        battery_health = int(message.text)
        if battery_health < 0 or battery_health > 100:
            await message.reply("Здоровье батареи должно быть от 0 до 100%.")
            return
        await state.update_data(battery_health=battery_health)
        await message.reply("Телефон восстанавливался?", reply_markup=get_yes_no_keyboard("repaired"))
        await state.set_state(ProductCreation.waiting_for_repaired)
    except ValueError:
        await message.reply("Неверный формат. Пожалуйста, введите целое число от 0 до 100.")

async def handle_repaired(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    repaired = callback_query.data.split('_')[1] == 'yes'
    await state.update_data(repaired=repaired)
    await callback_query.message.reply("Полная комплектация?", reply_markup=get_yes_no_keyboard("full_kit"))
    await state.set_state(ProductCreation.waiting_for_full_kit)

async def handle_full_kit(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    full_kit = callback_query.data.split('_')[2] == 'yes'  # "full_kit_yes" -> index 2
    await state.update_data(full_kit=full_kit, quantity=1)  # У телефонов всегда количество = 1
    
    # Переходим к опциональному вводу IMEI
    await callback_query.message.reply("Введите IMEI телефона (или нажмите 'Пропустить'):", 
                                      reply_markup=get_skip_keyboard("skip_imei"))
    await state.set_state(ProductCreation.waiting_for_imei)

async def handle_imei_input(message: types.Message, state: FSMContext, db_pool):
    imei = message.text.strip()
    if len(imei) > 17:
        await message.reply("IMEI слишком длинный. Максимум 17 символов.")
        return
        
    await state.update_data(imei=imei)
    await message.reply("Введите серийный номер телефона (или нажмите 'Пропустить'):", 
                       reply_markup=get_skip_keyboard("skip_serial"))
    await state.set_state(ProductCreation.waiting_for_serial_number)

async def handle_imei_skip(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await state.update_data(imei=None)
    await callback_query.message.reply("Введите серийный номер телефона (или нажмите 'Пропустить'):", 
                                      reply_markup=get_skip_keyboard("skip_serial"))
    await state.set_state(ProductCreation.waiting_for_serial_number)

async def handle_serial_input(message: types.Message, state: FSMContext, db_pool):
    serial_number = message.text.strip()
    if len(serial_number) > 50:
        await message.reply("Серийный номер слишком длинный. Максимум 50 символов.")
        return
        
    await state.update_data(serial_number=serial_number)
    await save_phone_to_db(message, state, db_pool)

async def handle_serial_skip(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await state.update_data(serial_number=None)
    await save_phone_to_db(callback_query.message, state, db_pool)

# --- Вспомогательные функции для управления сообщениями ---
async def delete_chat_messages(bot, chat_id: int, message_ids: list):
    """Удаляет сообщения из чата по их ID"""
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            # Игнорируем ошибки - сообщение могло быть уже удалено
            pass

async def send_new_message(bot, chat_id: int, text: str, reply_markup=None, parse_mode=None):
    """Отправляет новое сообщение вместо ответа на предыдущее"""
    return await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode
    )

async def track_message_id(state: FSMContext, message_id: int):
    """Добавляет message_id в историю для последующего удаления"""
    user_data = await state.get_data()
    message_history = user_data.get('message_history', [])
    message_history.append(message_id)
    await state.update_data(message_history=message_history)

async def clear_message_history(bot, chat_id: int, state: FSMContext):
    """Удаляет все сообщения из истории и очищает список"""
    user_data = await state.get_data()
    message_history = user_data.get('message_history', [])
    
    if message_history:
        await delete_chat_messages(bot, chat_id, message_history)
        await state.update_data(message_history=[])

# --- Вспомогательные функции для форматирования ---
def format_product_info(product, current_index, total_count):
    """Форматирует информацию о товаре для отображения"""
    text = f"📦 **Товар {current_index + 1} из {total_count}**\n\n"
    text += f"🆔 **ID**: {product['id']}\n"
    text += f"📝 **Название**: {product['name']}\n"
    text += f"💰 **Закуп**: {product['purchase_price']} руб.\n"
    if product['sale_price']:
        text += f"💵 **Продажа**: {product['sale_price']} руб.\n"
    text += f"📊 **Количество**: {product['quantity']} шт.\n"
    text += f"📂 **Категория**: {product['category_name'] or 'Не указана'}\n"
    return text

def format_phone_info(phone, current_index, total_count):
    """Форматирует информацию о телефоне для отображения"""
    text = f"📱 **Телефон {current_index + 1} из {total_count}**\n\n"
    text += f"🆔 **ID**: {phone['id']}\n"
    text += f"📱 **Модель**: {phone['brand_name']} {phone['model_name']}\n"
    text += f"💾 **Память**: {phone['capacity_gb']} ГБ\n"
    text += f"🎨 **Цвет**: {phone['color_name']}\n"
    text += f"🌍 **Рынок**: {phone['market_name']}\n"
    text += f"💰 **Закуп**: {phone['purchase_price']} руб.\n"
    if phone['sale_price']:
        text += f"💵 **Продажа**: {phone['sale_price']} руб.\n"
    text += f"🔋 **Состояние**: {phone['condition_name']}\n"
    
    if phone['battery_health']:
        text += f"🔋 **Батарея**: {phone['battery_health']}%\n"
    text += f"🔧 **Восстанавливался**: {'Да' if phone['repaired'] else 'Нет'}\n"
    text += f"📦 **Полная комплектация**: {'Да' if phone['full_kit'] else 'Нет'}\n"
    
    if phone['imei']:
        text += f"📟 **IMEI**: {phone['imei']}\n"
    if phone['serial_number']:
        text += f"🔢 **Серийный номер**: {phone['serial_number']}\n"
    
    return text

async def get_products_list(db_pool, sold_status=False):
    """Получает список товаров с фильтрацией по статусу продажи"""
    async with db_pool.acquire() as connection:
        return await connection.fetch("""
            SELECT p.id, p.name, p.purchase_price, p.sale_price, p.quantity,
                   c.name AS category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_sold = $1
            ORDER BY p.id DESC;
        """, sold_status)

async def get_phones_list(db_pool, sold_status=False):
    """Получает список телефонов с фильтрацией по статусу продажи"""
    async with db_pool.acquire() as connection:
        return await connection.fetch("""
            SELECT p.id, p.name, p.purchase_price, p.sale_price, p.battery_health,
                   p.repaired, p.full_kit, p.imei, p.serial_number,
                   b.name AS brand_name, m.name AS model_name, 
                   c.name AS color_name, s.capacity_gb,
                   ma.name AS market_name, cond.name AS condition_name
            FROM phones p
            LEFT JOIN models m ON p.model_id = m.id
            LEFT JOIN brands b ON m.brand_id = b.id
            LEFT JOIN colors c ON p.color_id = c.id
            LEFT JOIN storage_capacities s ON p.storage_capacity_id = s.id
            LEFT JOIN markets ma ON p.market_id = ma.id
            LEFT JOIN conditions cond ON p.condition_id = cond.id
            WHERE p.is_sold = $1
            ORDER BY p.id DESC;
        """, sold_status)

# --- Обработчики меню ---
async def handle_menu_all_products(callback_query: types.CallbackQuery, db_pool):
    """Показать первый товар из списка с навигацией"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    products = await get_products_list(db_pool, sold_status=False)
    
    if not products:
        text = "📦 **Товары не найдены**\n\nВ базе данных пока нет товаров."
        # Показываем кнопку добавления товара для админов даже когда товаров нет
        if is_admin:
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад в меню",
                            callback_data="back_to_menu"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="➕ Добавить товар",
                            callback_data="add_product_from_menu"
                        )
                    ]
                ]
            )
        else:
            keyboard = get_back_to_menu_keyboard()
            
        await callback_query.message.edit_text(
            text, 
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    # Показываем первый товар
    current_index = 0
    product = products[current_index]
    text = format_product_info(product, current_index, len(products))
    
    await callback_query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=get_item_navigation_keyboard('products', current_index, len(products), product['id'], is_admin)
    )

async def handle_menu_all_phones(callback_query: types.CallbackQuery, db_pool):
    """Показать первый телефон из списка с навигацией"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    phones = await get_phones_list(db_pool, sold_status=False)
    
    if not phones:
        text = "📱 **Телефоны не найдены**\n\nВ базе данных пока нет телефонов."
        # Показываем кнопку добавления телефона для админов даже когда телефонов нет
        if is_admin:
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="🔙 Назад в меню",
                            callback_data="back_to_menu"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="➕ Добавить телефон",
                            callback_data="add_phone_from_menu"
                        )
                    ]
                ]
            )
        else:
            keyboard = get_back_to_menu_keyboard()
            
        await callback_query.message.edit_text(
            text, 
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    # Показываем первый телефон
    current_index = 0
    phone = phones[current_index]
    text = format_phone_info(phone, current_index, len(phones))
    
    await callback_query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=get_item_navigation_keyboard('phones', current_index, len(phones), phone['id'], is_admin)
    )

async def handle_menu_profit(callback_query: types.CallbackQuery, db_pool):
    """Рассчитать и показать прибыль"""
    await callback_query.bot.answer_callback_query(callback_query.id)

    async with db_pool.acquire() as connection:
        # Прибыль от проданных товаров
        products_profit = await connection.fetchrow("""
            SELECT 
                COALESCE(SUM((sale_price - purchase_price) * quantity), 0) AS profit,
                COUNT(*) AS count,
                COALESCE(SUM(purchase_price * quantity), 0) AS total_investment,
                COALESCE(SUM(sale_price * quantity), 0) AS total_revenue
            FROM products 
            WHERE is_sold = TRUE AND sale_price IS NOT NULL;
        """)

        # Прибыль от проданных телефонов
        phones_profit = await connection.fetchrow("""
            SELECT 
                COALESCE(SUM(sale_price - purchase_price), 0) AS profit,
                COUNT(*) AS count,
                COALESCE(SUM(purchase_price), 0) AS total_investment,
                COALESCE(SUM(sale_price), 0) AS total_revenue
            FROM phones 
            WHERE is_sold = TRUE AND sale_price IS NOT NULL;
        """)

        # Текущие инвестиции (непроданные товары)
        current_investments = await connection.fetchrow("""
                                                        SELECT COALESCE(SUM(p.purchase_price * p.quantity), 0) +
                                                               COALESCE(
                                                                       (SELECT SUM(purchase_price) FROM phones WHERE is_sold = FALSE),
                                                                       0) AS total_investment
                                                        FROM products AS p
                                                        WHERE p.is_sold = FALSE;
                                                        """)

    total_profit = products_profit['profit'] + phones_profit['profit']
    total_revenue = products_profit['total_revenue'] + phones_profit['total_revenue']
    total_investment = products_profit['total_investment'] + phones_profit['total_investment']
    current_investment = current_investments['total_investment'] if current_investments else 0

    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    text = "💰 **Отчет по прибыли**\n\n"

    text += "📊 **Проданные товары:**\n"
    text += f"   • Товаров: {products_profit['count']} шт.\n"
    text += f"   • Телефонов: {phones_profit['count']} шт.\n"
    text += f"   • Прибыль: {total_profit:.2f} руб.\n\n"

    text += "💵 **Финансовые показатели:**\n"
    text += f"   • Выручка: {total_revenue:.2f} руб.\n"
    text += f"   • Инвестиции: {total_investment:.2f} руб.\n"
    text += f"   • Рентабельность: {profit_margin:.1f}%\n\n"

    text += "📦 **Текущие инвестиции:**\n"
    text += f"   • В наличии на: {current_investment:.2f} руб.\n\n"

    if total_profit > 0:
        text += f"✅ **Общая прибыль: +{total_profit:.2f} руб.**"
    elif total_profit < 0:
        text += f"❌ **Общий убыток: {total_profit:.2f} руб.**"
    else:
        text += "➖ **Прибыль/убыток: 0 руб.**"

    await callback_query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=get_back_to_menu_keyboard()
    )

async def handle_menu_stats(callback_query: types.CallbackQuery, db_pool):
    """Показать общую статистику"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    async with db_pool.acquire() as connection:
        # Статистика товаров
        products_stats = await connection.fetchrow("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN is_sold = TRUE THEN 1 END) as sold,
                COUNT(CASE WHEN is_sold = FALSE THEN 1 END) as available
            FROM products;
        """)
        
        # Статистика телефонов
        phones_stats = await connection.fetchrow("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN is_sold = TRUE THEN 1 END) as sold,
                COUNT(CASE WHEN is_sold = FALSE THEN 1 END) as available
            FROM phones;
        """)
        
        # Популярные бренды
        popular_brands = await connection.fetch("""
            SELECT b.name, COUNT(p.id) as count
            FROM phones p
            JOIN models m ON p.model_id = m.id
            JOIN brands b ON m.brand_id = b.id
            GROUP BY b.name
            ORDER BY count DESC
            LIMIT 5;
        """)
    
    text = "📊 **Статистика магазина**\n\n"
    
    text += "📦 **Обычные товары:**\n"
    text += f"   • Всего: {products_stats['total']}\n"
    text += f"   • В наличии: {products_stats['available']}\n"
    text += f"   • Продано: {products_stats['sold']}\n\n"
    
    text += "📱 **Телефоны:**\n"
    text += f"   • Всего: {phones_stats['total']}\n"
    text += f"   • В наличии: {phones_stats['available']}\n"
    text += f"   • Продано: {phones_stats['sold']}\n\n"
    
    if popular_brands:
        text += "🏆 **Популярные бренды:**\n"
        for brand in popular_brands:
            text += f"   • {brand['name']}: {brand['count']} шт.\n"
    
    total_items = products_stats['total'] + phones_stats['total']
    total_sold = products_stats['sold'] + phones_stats['sold']
    
    text += f"\n🎯 **Общий оборот**: {total_sold}/{total_items} товаров"
    
    await callback_query.message.edit_text(
        text, 
        parse_mode='Markdown',
        reply_markup=get_back_to_menu_keyboard()
    )

# --- Функции сохранения ---
async def save_phone_to_db(message, state: FSMContext, db_pool):
    user_data = await state.get_data()
    bot = message.bot
    chat_id = message.chat.id
    
    async with db_pool.acquire() as connection:
        try:
            # Новый SQL запрос с foreign keys
            query = """
                    INSERT INTO phones (name, purchase_price, sale_price, model_id, color_id, 
                                      storage_capacity_id, market_id, condition_id, battery_health, 
                                      repaired, full_kit, imei, serial_number)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) RETURNING id;
                    """
            result = await connection.fetchrow(
                query,
                user_data['name'],
                user_data['purchase_price'],
                user_data.get('sale_price'),
                user_data['model_id'],
                user_data['color_id'],
                user_data['storage_capacity_id'],
                user_data['market_id'],
                user_data['condition_id'],
                user_data.get('battery_health'),
                user_data.get('repaired', False),
                user_data.get('full_kit', True),
                user_data.get('imei'),
                user_data.get('serial_number')
            )
            phone_id = result['id']
            
            # Удаляем все промежуточные сообщения
            await clear_message_history(bot, chat_id, state)
            
            # Создаем красивое сообщение с деталями телефона
            summary = f"📱 Телефон успешно добавлен!\n\n"
            summary += f"🆔 ID: {phone_id}\n"
            summary += f"📱 Модель: {user_data['brand_name']} {user_data['model_name']}\n"
            summary += f"💾 Память: {user_data['storage_gb']} ГБ\n"
            summary += f"🎨 Цвет: {user_data['color_name']}\n"
            summary += f"🌍 Рынок: {user_data['market_name']}\n"
            summary += f"💰 Закупочная цена: {user_data['purchase_price']} руб.\n"
            summary += f"🔋 Состояние: {user_data['condition_name']}"
            
            if user_data.get('battery_health'):
                summary += f"\n🔋 Батарея: {user_data['battery_health']}%"
            if user_data.get('imei'):
                summary += f"\n📟 IMEI: {user_data['imei']}"
            if user_data.get('serial_number'):
                summary += f"\n🔢 Серийный номер: {user_data['serial_number']}"
                
            # Отправляем новое сообщение с кнопками навигации
            await send_new_message(
                bot, chat_id, summary, 
                reply_markup=get_success_menu_keyboard('phone'),
                parse_mode='Markdown'
            )
        except Exception as e:
            error_msg = f"Произошла ошибка при добавлении телефона: {e}"
            await send_new_message(bot, chat_id, error_msg)
        finally:
            await state.clear()

async def save_product_to_db(message, state: FSMContext, db_pool):
    user_data = await state.get_data()
    bot = message.bot
    chat_id = message.chat.id
    
    async with db_pool.acquire() as connection:
        try:
            query = """
                    INSERT INTO products (name, purchase_price, sale_price, quantity, category_id)
                    VALUES ($1, $2, $3, $4, $5) RETURNING id;
                    """
            result = await connection.fetchrow(
                query,
                user_data['name'],
                user_data['purchase_price'],
                user_data.get('sale_price'),
                user_data['quantity'],
                user_data['category_id']
            )
            product_id = result['id']
            
            # Удаляем все промежуточные сообщения (для товаров удаляем меньше истории)
            await clear_message_history(bot, chat_id, state)
            
            # Создаем подробное сообщение о товаре
            summary = f"📦 **Товар успешно добавлен!**\n\n"
            summary += f"🆔 **ID**: {product_id}\n"
            summary += f"📝 **Название**: {user_data['name']}\n"
            summary += f"💰 **Закупочная цена**: {user_data['purchase_price']} руб.\n"
            if user_data.get('sale_price'):
                summary += f"💵 **Цена продажи**: {user_data['sale_price']} руб.\n"
            summary += f"📊 **Количество**: {user_data['quantity']} шт.\n"
            summary += f"📂 **Категория**: {user_data.get('category_name', 'Не указана')}"
            
            # Отправляем новое сообщение с кнопками навигации
            await send_new_message(
                bot, chat_id, summary, 
                reply_markup=get_success_menu_keyboard('product'),
                parse_mode='Markdown'
            )
        except Exception as e:
            error_msg = f"Произошла ошибка при добавлении продукта: {e}"
            await send_new_message(bot, chat_id, error_msg)
        finally:
            await state.clear()


# --- Остальные обработчики ---
async def list_categories(message: types.Message, db_pool):
    async with db_pool.acquire() as connection:
        categories = await connection.fetch("SELECT id, name FROM categories ORDER BY name;")

    if not categories:
        await message.reply("Список категорий пуст.")
    else:
        categories_text = "Доступные категории:\n\n"
        for category in categories:
            categories_text += f"▪️ {category['name']} (ID: {category['id']})\n"
        await message.reply(categories_text)


async def list_products(message: types.Message, db_pool):
    async with db_pool.acquire() as connection:
        products = await connection.fetch("""
                                          SELECT p.name, p.purchase_price, c.name AS category_name
                                          FROM products p
                                                   JOIN categories c ON p.category_id = c.id
                                          ORDER BY p.name;
                                          """)

    if not products:
        await message.reply("Список товаров пуст.")
    else:
        product_list_text = "Доступные товары:\n\n"
        for product in products:
            product_list_text += f"▪️ **{product['name']}**\n   Цена: ${product['purchase_price']}\n   Категория: {product['category_name']}\n\n"
        await message.reply(product_list_text, parse_mode='Markdown')


# --- Новые обработчики для навигации ---
async def handle_back_to_menu(callback_query: types.CallbackQuery, db_pool):
    """Возврат в главное меню"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    await callback_query.message.edit_text(
        "🏪 **Главное меню магазина**\n\nВыберите действие:", 
        reply_markup=get_menu_keyboard(), 
        parse_mode='Markdown'
    )

async def handle_nav_products(callback_query: types.CallbackQuery, db_pool):
    """Навигация по товарам"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Извлекаем индекс из callback_data: "nav_products:5"
    current_index = int(callback_query.data.split(':')[1])
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    products = await get_products_list(db_pool, sold_status=False)
    
    if not products or current_index >= len(products) or current_index < 0:
        await callback_query.answer("Товар не найден", show_alert=True)
        return
    
    product = products[current_index]
    text = format_product_info(product, current_index, len(products))
    
    await callback_query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=get_item_navigation_keyboard('products', current_index, len(products), product['id'], is_admin)
    )

async def handle_nav_phones(callback_query: types.CallbackQuery, db_pool):
    """Навигация по телефонам"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Извлекаем индекс из callback_data: "nav_phones:5"
    current_index = int(callback_query.data.split(':')[1])
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    phones = await get_phones_list(db_pool, sold_status=False)
    
    if not phones or current_index >= len(phones) or current_index < 0:
        await callback_query.answer("Телефон не найден", show_alert=True)
        return
    
    phone = phones[current_index]
    text = format_phone_info(phone, current_index, len(phones))
    
    await callback_query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=get_item_navigation_keyboard('phones', current_index, len(phones), phone['id'], is_admin)
    )

async def handle_edit_item(callback_query: types.CallbackQuery, db_pool):
    """Обработчик для редактирования товара/телефона"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Разбираем callback_data: "edit_item:products:5" или "edit_item:phones:3"
    parts = callback_query.data.split(':')
    item_type = parts[1]
    item_id = int(parts[2])
    
    # Пока что просто показываем сообщение
    await callback_query.answer(f"Редактирование {item_type} с ID {item_id} будет добавлено в следующей версии", show_alert=True)

async def handle_sell_item(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    """Обработчик для продажи товара/телефона"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Разбираем callback_data: "sell_item:products:5" или "sell_item:phones:3"
    parts = callback_query.data.split(':')
    item_type = parts[1]
    item_id = int(parts[2])
    
    # Проверяем права администратора
    if callback_query.from_user.id not in IsAdminFilter.admin_ids:
        await callback_query.answer("У вас нет прав для выполнения этого действия", show_alert=True)
        return
    
    # Проверяем, что товар/телефон существует и не продан
    async with db_pool.acquire() as connection:
        if item_type == "products":
            item = await connection.fetchrow("""
                SELECT name, is_sold, purchase_price 
                FROM products 
                WHERE id = $1
            """, item_id)
        else:  # phones
            item = await connection.fetchrow("""
                SELECT p.name, p.is_sold, p.purchase_price,
                       b.name AS brand_name, m.name AS model_name
                FROM phones p
                LEFT JOIN models m ON p.model_id = m.id
                LEFT JOIN brands b ON m.brand_id = b.id
                WHERE p.id = $1
            """, item_id)
    
    if not item:
        await callback_query.answer("Товар/телефон не найден", show_alert=True)
        return
    
    if item['is_sold']:
        await callback_query.answer("Этот товар/телефон уже продан", show_alert=True)
        return
    
    # Сохраняем данные о продаже в состояние
    await state.update_data(
        sale_item_type=item_type,
        sale_item_id=item_id
    )
    
    # Формируем название товара
    if item_type == "products":
        item_name = item['name']
    else:
        item_name = f"{item['brand_name']} {item['model_name']}" if item['brand_name'] and item['model_name'] else item['name']
    
    # Запрашиваем цену продажи
    message = await send_new_message(
        callback_query.bot,
        callback_query.from_user.id,
        f"💰 **Продажа товара**\n\n"
        f"📦 **Товар**: {item_name}\n"
        f"💵 **Цена покупки**: {item['purchase_price']:.2f} руб.\n\n"
        f"Введите цену продажи (в рублях):"
    )
    
    await track_message_id(state, message.message_id)
    await state.set_state(SaleProcess.waiting_for_sale_price)

async def handle_add_product_from_menu(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    """Обработчик для добавления товара из меню навигации"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем права администратора
    if callback_query.from_user.id not in IsAdminFilter.admin_ids:
        await callback_query.answer("У вас нет прав для выполнения этого действия", show_alert=True)
        return
    
    # Проверяем наличие категорий
    async with db_pool.acquire() as connection:
        categories = await connection.fetch("SELECT id, name FROM categories;")

    if not categories:
        await callback_query.message.edit_text(
            "В базе нет ни одной категории. Добавьте их, прежде чем создавать продукт.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return

    # Запускаем процесс создания товара
    await callback_query.message.edit_text(
        "Отлично, давайте добавим новый продукт. Выберите категорию товара:", 
        reply_markup=get_categories_keyboard(categories)
    )
    await state.set_state(ProductCreation.waiting_for_category)

async def handle_add_phone_from_menu(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    """Обработчик для добавления телефона из меню навигации"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем права администратора
    if callback_query.from_user.id not in IsAdminFilter.admin_ids:
        await callback_query.answer("У вас нет прав для выполнения этого действия", show_alert=True)
        return
    
    # Проверяем наличие категорий и находим категорию "Телефоны"
    async with db_pool.acquire() as connection:
        phone_category = await connection.fetchrow("SELECT id, name FROM categories WHERE LOWER(name) = 'телефоны';")
        
    if not phone_category:
        await callback_query.message.edit_text(
            "Категория 'Телефоны' не найдена в базе данных. Создайте её сначала.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
        
    # Проверяем наличие брендов
    async with db_pool.acquire() as connection:
        brands = await connection.fetch("SELECT id, name FROM brands ORDER BY name;")
        
    if not brands:
        await callback_query.message.edit_text(
            "В базе нет брендов. Добавьте их прежде чем создавать телефон.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
    
    # Устанавливаем данные для телефона и переходим к выбору бренда
    await state.update_data(
        category_id=phone_category['id'],
        category_name=phone_category['name'],
        is_phone=True,
        name="Телефон"
    )
    
    await callback_query.message.edit_text(
        "Выберите бренд телефона:", 
        reply_markup=get_brands_keyboard(brands)
    )
    await state.set_state(ProductCreation.waiting_for_brand)

async def handle_add_another_product(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    """Обработчик для кнопки 'Добавить еще товар'"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем права администратора
    if callback_query.from_user.id not in IsAdminFilter.admin_ids:
        await callback_query.answer("У вас нет прав для выполнения этого действия", show_alert=True)
        return
    
    # Проверяем наличие категорий
    async with db_pool.acquire() as connection:
        categories = await connection.fetch("SELECT id, name FROM categories;")

    if not categories:
        await callback_query.message.edit_text(
            "В базе нет ни одной категории. Добавьте их, прежде чем создавать продукт.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return

    # Запускаем процесс создания товара
    await callback_query.message.edit_text(
        "Отлично, давайте добавим еще один продукт. Выберите категорию товара:", 
        reply_markup=get_categories_keyboard(categories)
    )
    await state.set_state(ProductCreation.waiting_for_category)

async def handle_add_another_phone(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    """Обработчик для кнопки 'Добавить еще телефон'"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем права администратора
    if callback_query.from_user.id not in IsAdminFilter.admin_ids:
        await callback_query.answer("У вас нет прав для выполнения этого действия", show_alert=True)
        return
    
    # Проверяем наличие категорий и находим категорию "Телефоны"
    async with db_pool.acquire() as connection:
        phone_category = await connection.fetchrow("SELECT id, name FROM categories WHERE LOWER(name) = 'телефоны';")
        
    if not phone_category:
        await callback_query.message.edit_text(
            "Категория 'Телефоны' не найдена в базе данных. Создайте её сначала.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
        
    # Проверяем наличие брендов
    async with db_pool.acquire() as connection:
        brands = await connection.fetch("SELECT id, name FROM brands ORDER BY name;")
        
    if not brands:
        await callback_query.message.edit_text(
            "В базе нет брендов. Добавьте их прежде чем создавать телефон.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
    
    # Устанавливаем данные для телефона и переходим к выбору бренда
    await state.update_data(
        category_id=phone_category['id'],
        category_name=phone_category['name'],
        is_phone=True,
        name="Телефон"
    )
    
    await callback_query.message.edit_text(
        "Выберите бренд телефона:", 
        reply_markup=get_brands_keyboard(brands)
    )
    await state.set_state(ProductCreation.waiting_for_brand)
# --- Обработчики подменю ---

async def handle_products_submenu(callback_query: types.CallbackQuery, db_pool):
    """Обработчик подменю товаров"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    await callback_query.message.edit_text(
        "📦 **Меню товаров**\n\nВыберите действие:",
        reply_markup=get_products_submenu_keyboard(is_admin),
        parse_mode="Markdown"
    )

async def handle_phones_submenu(callback_query: types.CallbackQuery, db_pool):
    """Обработчик подменю телефонов"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    await callback_query.message.edit_text(
        "📱 **Меню телефонов**\n\nВыберите действие:",
        reply_markup=get_phones_submenu_keyboard(is_admin),
        parse_mode="Markdown"
    )

async def handle_products_available(callback_query: types.CallbackQuery, db_pool):
    """Показать товары в наличии"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    products = await get_products_list(db_pool, sold_status=False)
    
    if not products:
        text = "📦 **Товары в наличии**\n\nВ базе данных нет товаров в наличии."
        await callback_query.message.edit_text(
            text, 
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # Показываем первый товар
    current_index = 0
    product = products[current_index]
    text = format_product_info(product, current_index, len(products))
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_item_navigation_keyboard('products', current_index, len(products), product['id'], is_admin)
    )

async def handle_products_sold(callback_query: types.CallbackQuery, db_pool):
    """Показать проданные товары"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    products = await get_products_list(db_pool, sold_status=True)
    
    if not products:
        text = "💰 **Проданные товары**\n\nПока нет проданных товаров."
        await callback_query.message.edit_text(
            text, 
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # Показываем первый товар
    current_index = 0
    product = products[current_index]
    text = format_product_info(product, current_index, len(products))
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_item_navigation_keyboard('products', current_index, len(products), product['id'], is_admin)
    )

async def handle_phones_available(callback_query: types.CallbackQuery, db_pool):
    """Показать телефоны в наличии"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    phones = await get_phones_list(db_pool, sold_status=False)
    
    if not phones:
        text = "📱 **Телефоны в наличии**\n\nВ базе данных нет телефонов в наличии."
        await callback_query.message.edit_text(
            text, 
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # Показываем первый телефон
    current_index = 0
    phone = phones[current_index]
    text = format_phone_info(phone, current_index, len(phones))
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_item_navigation_keyboard('phones', current_index, len(phones), phone['id'], is_admin)
    )

async def handle_phones_sold(callback_query: types.CallbackQuery, db_pool):
    """Показать проданные телефоны"""
    await callback_query.bot.answer_callback_query(callback_query.id)
    
    # Проверяем, является ли пользователь админом
    is_admin = callback_query.from_user.id in IsAdminFilter.admin_ids
    
    phones = await get_phones_list(db_pool, sold_status=True)
    
    if not phones:
        text = "💰 **Проданные телефоны**\n\nПока нет проданных телефонов."
        await callback_query.message.edit_text(
            text, 
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # Показываем первый телефон
    current_index = 0
    phone = phones[current_index]
    text = format_phone_info(phone, current_index, len(phones))
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_item_navigation_keyboard('phones', current_index, len(phones), phone['id'], is_admin)
    )
# Дополнительные обработчики для продажи - временный файл

# --- Обработчики для процесса продажи ---

async def handle_sale_price_input(message: types.Message, state: FSMContext, db_pool):
    """Обработчик для ввода цены продажи"""
    try:
        sale_price = float(message.text.replace(',', '.'))
        
        # Получаем данные о продаваемом товаре/телефоне
        user_data = await state.get_data()
        item_type = user_data.get('sale_item_type')
        item_id = user_data.get('sale_item_id')
        
        if not item_type or not item_id:
            await send_new_message(
                message.bot,
                message.from_user.id,
                "Ошибка: не удалось получить данные о товаре/телефоне для продажи."
            )
            await state.clear()
            return
        
        # Выполняем продажу
        success, profit = await process_sale(db_pool, item_type, item_id, sale_price)
        
        if success:
            profit_text = f"💰 **Прибыль**: {profit:.2f} руб." if profit >= 0 else f"📉 **Убыток**: {abs(profit):.2f} руб."
            
            message_obj = await send_new_message(
                message.bot,
                message.from_user.id,
                f"✅ **Продажа завершена успешно!**\n\n"
                f"💵 **Цена продажи**: {sale_price:.2f} руб.\n"
                f"{profit_text}\n\n"
                f"Транзакция записана в базу данных.",
                reply_markup=get_back_to_menu_keyboard()
            )
            await track_message_id(state, message_obj.message_id)
        else:
            message_obj = await send_new_message(
                message.bot,
                message.from_user.id,
                "❌ **Ошибка при продаже!**\n\nНе удалось завершить операцию.",
                reply_markup=get_back_to_menu_keyboard()
            )
            await track_message_id(state, message_obj.message_id)
        
        await state.clear()
        
    except ValueError:
        await message.reply("❌ Неверный формат цены. Введите числовое значение (например: 15000 или 15000.50).")


async def process_sale(db_pool, item_type, item_id, sale_price):
    """
    Обрабатывает продажу товара/телефона.
    Добавлено подробное логирование для отладки.
    """
    print(f"[LOG] Начало обработки продажи. Тип: '{item_type}', ID: {item_id}, Цена продажи: {sale_price}")

    try:
        async with db_pool.acquire() as connection:
            async with connection.transaction():
                if item_type == "products":
                    print(f"[LOG] Тип товара - 'products'. Получение информации о товаре ID: {item_id}...")

                    # Получаем информацию о товаре
                    product = await connection.fetchrow("""
                                                        SELECT name, purchase_price, is_sold
                                                        FROM products
                                                        WHERE id = $1
                                                        """, item_id)
                    print(f"[LOG] Полученная информация: {product}")

                    if not product or product['is_sold']:
                        print(f"[ERROR] Товар ID: {item_id} не найден или уже продан. Возвращаю False.")
                        return False, 0

                    print(f"[LOG] Товар '{product['name']}' найден и доступен. Обновление статуса...")

                    # Обновляем статус товара
                    await connection.execute("""
                                             UPDATE products
                                             SET is_sold    = TRUE,
                                                 sale_price = $2
                                             WHERE id = $1
                                             """, item_id, sale_price)

                    # Создаем запись в транзакциях
                    # Конвертируем sale_price в Decimal для корректного вычисления прибыли
                    profit = Decimal(str(sale_price)) - product['purchase_price']
                    print(f"[LOG] Создаю запись о транзакции. Прибыль: {profit}")
                    await connection.execute("""
                                             INSERT INTO transactions (product_id, phone_id, type, amount, description)
                                             VALUES ($1, NULL, 'sale', $2, $3)
                                             """, item_id, sale_price, f"Продажа товара: {product['name']}")

                    print(f"[SUCCESS] Продажа товара ID: {item_id} успешно завершена. Прибыль: {profit}")
                    return True, profit

                elif item_type == "phones":
                    print(f"[LOG] Тип товара - 'phones'. Получение информации о телефоне ID: {item_id}...")

                    # Получаем информацию о телефоне
                    phone = await connection.fetchrow("""
                                                      SELECT p.name,
                                                             p.purchase_price,
                                                             p.is_sold,
                                                             b.name AS brand_name,
                                                             m.name AS model_name
                                                      FROM phones p
                                                               LEFT JOIN models m ON p.model_id = m.id
                                                               LEFT JOIN brands b ON m.brand_id = b.id
                                                      WHERE p.id = $1
                                                      """, item_id)
                    print(f"[LOG] Полученная информация: {phone}")

                    if not phone or phone['is_sold']:
                        print(f"[ERROR] Телефон ID: {item_id} не найден или уже продан. Возвращаю False.")
                        return False, 0

                    print(f"[LOG] Телефон найден и доступен. Обновление статуса...")

                    # Обновляем статус телефона
                    await connection.execute("""
                                             UPDATE phones
                                             SET is_sold    = TRUE,
                                                 sale_price = $2
                                             WHERE id = $1
                                             """, item_id, sale_price)

                    # Создаем запись в транзакциях
                    # Конвертируем sale_price в Decimal для корректного вычисления прибыли
                    profit = Decimal(str(sale_price)) - phone['purchase_price']
                    phone_name = f"{phone['brand_name']} {phone['model_name']}" if phone['brand_name'] and phone[
                        'model_name'] else phone['name']
                    print(f"[LOG] Создаю запись о транзакции. Прибыль: {profit}")
                    await connection.execute("""
                                             INSERT INTO transactions (product_id, phone_id, type, amount, description)
                                             VALUES (NULL, $1, 'sale', $2, $3)
                                             """, item_id, sale_price, f"Продажа телефона: {phone_name}")

                    print(f"[SUCCESS] Продажа телефона ID: {item_id} успешно завершена. Прибыль: {profit}")
                    return True, profit

                else:
                    print(f"[ERROR] Неизвестный тип товара: '{item_type}'. Возвращаю False.")
                    return False, 0


    except Exception as e:
        # Выводим подробную ошибку в консоль для отладки
        print(f"[CRITICAL ERROR] Произошла непредвиденная ошибка при продаже: {e}")
        return False, 0
