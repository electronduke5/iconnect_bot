from aiogram import Dispatcher, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import CategoryCreation, ProductCreation
from keyboards import get_main_keyboard, get_admin_keyboard, get_sale_price_keyboard, get_conditions_keyboard, \
    get_categories_keyboard
from filters import IsAdminFilter
from functools import partial


# --- Функции регистрации обработчиков ---
def register_handlers(dp: Dispatcher, admin_ids: list, db_pool):
    IsAdminFilter.admin_ids = admin_ids

    # Основные обработчики
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_help, Command("help"))
    dp.message.register(partial(list_categories, db_pool=db_pool), Command("categories"))
    dp.message.register(partial(list_products, db_pool=db_pool), Command("products"))

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
    dp.message.register(partial(handle_product_purchase_price, db_pool=db_pool),
                        StateFilter(ProductCreation.waiting_for_purchase_price), IsAdminFilter())
    dp.callback_query.register(partial(handle_skip_sale_price, db_pool=db_pool), lambda c: c.data == 'skip_sale_price',
                               StateFilter(ProductCreation.waiting_for_purchase_price))
    dp.message.register(partial(handle_product_quantity, db_pool=db_pool),
                        StateFilter(ProductCreation.waiting_for_quantity), IsAdminFilter())
    dp.message.register(partial(handle_product_color, db_pool=db_pool), StateFilter(ProductCreation.waiting_for_color),
                        IsAdminFilter())
    dp.callback_query.register(partial(handle_product_condition, db_pool=db_pool),
                               lambda c: c.data.startswith('condition_'),
                               StateFilter(ProductCreation.waiting_for_condition), IsAdminFilter())
    dp.callback_query.register(partial(handle_product_category, db_pool=db_pool),
                               lambda c: c.data.startswith('category_'),
                               StateFilter(ProductCreation.waiting_for_category), IsAdminFilter())


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
    await callback_query.message.reply("Отлично, давайте добавим новый продукт. Введите его название:")
    await state.set_state(ProductCreation.waiting_for_name)


async def handle_product_name(message: types.Message, state: FSMContext, db_pool):
    await state.update_data(name=message.text.strip())
    await message.reply("Введите закупочную цену (например, 150.50):")
    await state.set_state(ProductCreation.waiting_for_purchase_price)


async def handle_product_purchase_price(message: types.Message, state: FSMContext, db_pool):
    try:
        price = float(message.text.replace(',', '.'))
        await state.update_data(purchase_price=price)
        await message.reply("Отлично! Теперь введите цену продажи (число) или нажмите 'Пропустить', если её нет:",
                            reply_markup=get_sale_price_keyboard())
        await state.set_state(ProductCreation.waiting_for_quantity)
    except ValueError:
        await message.reply("Неверный формат цены. Пожалуйста, введите число (например, 150.50).")


async def handle_skip_sale_price(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await state.update_data(sale_price=None)
    await callback_query.message.reply("Пропускаем цену продажи. Теперь введите количество товара (целое число):")
    await state.set_state(ProductCreation.waiting_for_quantity)


async def handle_product_quantity(message: types.Message, state: FSMContext, db_pool):
    user_data = await state.get_data()

    # Если цена продажи ещё не установлена, получаем её из сообщения
    if 'sale_price' not in user_data:
        try:
            sale_price = float(message.text.replace(',', '.'))
            await state.update_data(sale_price=sale_price)
        except ValueError:
            await message.reply("Неверный формат цены продажи. Пожалуйста, введите число или нажмите 'Пропустить'.")
            return

    try:
        quantity = int(message.text)
        await state.update_data(quantity=quantity)
        await message.reply("Введите цвет товара (например, 'черный', 'серый'):")
        await state.set_state(ProductCreation.waiting_for_color)
    except ValueError:
        await message.reply("Неверный формат количества. Пожалуйста, введите целое число.")


async def handle_product_color(message: types.Message, state: FSMContext, db_pool):
    await state.update_data(color=message.text.strip())

    async with db_pool.acquire() as connection:
        conditions = await connection.fetch("SELECT id, name FROM conditions;")

    if not conditions:
        await message.reply("В базе нет ни одного состояния. Добавьте их, прежде чем создавать продукт.")
        await state.clear()
        return

    await message.reply("Выберите состояние товара:", reply_markup=get_conditions_keyboard(conditions))
    await state.set_state(ProductCreation.waiting_for_condition)


async def handle_product_condition(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    condition_id = int(callback_query.data.split('_')[1])
    await state.update_data(condition_id=condition_id)

    async with db_pool.acquire() as connection:
        categories = await connection.fetch("SELECT id, name FROM categories;")

    if not categories:
        await callback_query.message.reply("В базе нет ни одной категории. Добавьте их, прежде чем создавать продукт.")
        await state.clear()
        return

    await callback_query.message.reply("Выберите категорию товара:", reply_markup=get_categories_keyboard(categories))
    await state.set_state(ProductCreation.waiting_for_category)


async def handle_product_category(callback_query: types.CallbackQuery, state: FSMContext, db_pool):
    await callback_query.bot.answer_callback_query(callback_query.id)
    category_id = int(callback_query.data.split('_')[1])

    user_data = await state.get_data()
    user_data['category_id'] = category_id

    async with db_pool.acquire() as connection:
        try:
            query = """
                    INSERT INTO products (name, purchase_price, sale_price, quantity, color, condition_id, category_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id; \
                    """
            result = await connection.fetchrow(
                query,
                user_data['name'],
                user_data['purchase_price'],
                user_data['sale_price'],
                user_data['quantity'],
                user_data['color'],
                user_data['condition_id'],
                user_data['category_id']
            )

            product_id = result['id']
            await callback_query.message.reply(f"Продукт '{user_data['name']}' (ID: {product_id}) успешно добавлен.")

        except Exception as e:
            await callback_query.message.reply(f"Произошла ошибка при добавлении продукта: {e}")
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