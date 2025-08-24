from aiogram import Dispatcher, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from states import CategoryCreation
from keyboards import get_main_keyboard, get_admin_keyboard
from filters import IsAdminFilter
from functools import partial


def register_handlers(dp: Dispatcher, admin_ids: list, db_pool):
    """
    Регистрирует все обработчики в диспетчере.
    """
    # Регистрируем фильтр администратора
    IsAdminFilter.admin_ids = admin_ids

    # Регистрируем обработчики с передачей db_pool
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_help, Command("help"))
    dp.message.register(partial(list_categories, db_pool=db_pool), Command("categories"))
    dp.message.register(partial(list_products, db_pool=db_pool), Command("products"))
    dp.callback_query.register(partial(handle_create_category_callback, db_pool=db_pool),
                               lambda c: c.data == "create_category_btn", IsAdminFilter())
    dp.message.register(partial(handle_category_name, db_pool=db_pool), StateFilter(CategoryCreation.waiting_for_name),
                        IsAdminFilter())


# --- Все ваши обработчики теперь находятся здесь ---

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
        "Чтобы добавить категорию, нажмите 'Создать категорию' в меню\\."
    )

    # Кнопки для админов
    if message.from_user.id in IsAdminFilter.admin_ids:
        await message.reply(help_text, reply_markup=get_admin_keyboard(), parse_mode='MarkdownV2')
    else:
        # Убираем часть для администраторов
        help_text = help_text.replace(
            "*Команды для администраторов:*\nЧтобы добавить категорию, нажмите 'Создать категорию' в меню\\.", "")
        await message.reply(help_text, parse_mode='MarkdownV2')


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