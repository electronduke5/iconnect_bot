import os
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.filters import BaseFilter, CommandStart, Command, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Получаем данные для подключения из переменных окружения
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Получаем строку с ID администраторов и преобразуем её в список целых чисел
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS")
ADMIN_IDS = [int(x) for x in ADMIN_IDS_STR.split(',')]

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- FSM STATES ---
class CategoryCreation(StatesGroup):
    """
    Состояния для создания категории
    """
    waiting_for_name = State()


# --- CUSTOM FILTERS ---
class IsAdminFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in ADMIN_IDS


# --- DATABASE CONNECTION ---
db_pool = None


async def create_db_pool():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            host=DB_HOST,
            min_size=1,
            max_size=10
        )
        print("Пул подключений к базе данных успешно создан.")
    except Exception as e:
        print(f"Ошибка при создании пула подключений: {e}")
        exit(1)


# --- HANDLERS ---
@dp.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Обработчик команды /start. Отправляет главное меню с кнопками.
    """
    # Создаем inline-клавиатуру
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Создать категорию",
                    callback_data="create_category_btn"
                )
            ]
        ]
    )
    await message.reply("Привет! Я бот для управления складом. Выберите действие:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "create_category_btn", IsAdminFilter())
async def handle_create_category_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Создать категорию".
    Переводит бота в состояние ожидания имени категории.
    """
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.reply("Пожалуйста, введите название для новой категории:")
    await state.set_state(CategoryCreation.waiting_for_name)


@dp.message(StateFilter(CategoryCreation.waiting_for_name), IsAdminFilter())
async def handle_category_name(message: types.Message, state: FSMContext):
    """
    Обработчик, который срабатывает в состоянии ожидания имени категории.
    Добавляет категорию в БД и сбрасывает состояние.
    """
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
                    category_id = result['id']
                    await message.reply(f"Категория '{category_name}' (ID: {category_id}) успешно добавлена.")
                else:
                    await message.reply(f"Категория '{category_name}' уже существует.")
            except Exception as e:
                await message.reply(f"Произошла ошибка при добавлении категории: {e}")
            finally:
                # Сбрасываем состояние
                await state.clear()


@dp.message(Command("categories"))
async def list_categories(message: types.Message):
    async with db_pool.acquire() as connection:
        categories = await connection.fetch("SELECT id, name FROM categories ORDER BY name;")

    if not categories:
        await message.reply("Список категорий пуст.")
    else:
        categories_text = "Доступные категории:\n\n"
        for category in categories:
            categories_text += f"▪️ {category['name']} (ID: {category['id']})\n"
        await message.reply(categories_text)


@dp.message(Command("products"))
async def list_products(message: types.Message):
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


# Запуск бота
async def main():
    await create_db_pool()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
    finally:
        if db_pool:
            db_pool.terminate()
            print("Пул подключений к БД закрыт.")
