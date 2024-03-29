
from aiogram import Bot, executor

from dotenv import load_dotenv

import os

from src.utils.connect_db import con
from src.utils.db_functions import create_table_products, create_table_bank_card, create_table_carts, create_table_orders, create_table_categories
from src.loader import dp


load_dotenv()
bot = Bot(os.getenv('TOKEN'))


async def on_startup(dispatcher):
    await create_table_products()
    await create_table_bank_card()
    await create_table_carts()
    await create_table_orders()
    await create_table_categories()


async def on_shutdown(dispatcher):
    con.close()

if __name__ == '__main__':
    from src.handlers.admins import admin_panel
    from src.handlers.users import user_panel
    print("Bot started successfully")
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
    print("Bot stopped")
