import os
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher
from handlers import register_handlers

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

# Переменная для хранения пула подключений к БД
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


async def main():
    await create_db_pool()

    # Регистрируем все обработчики, передавая db_pool
    register_handlers(dp, ADMIN_IDS, db_pool)

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