from loader import form_router, bot
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery
import app_keyboards as app_kb
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.config import data_dir_path
from aiogram.fsm.context import FSMContext
from app_states import CatalogStates
from app_logger import logger
from typing import Dict, List, Optional
from data.config import root_categories, root_cat_titles
from app_filters import AppCbStateFilter
from database.db_connection import App_DB_Connection

async def get_customer_cart(customer_id: int):
    db = App_DB_Connection()
    await db.connect()
    query = "SELECT id FROM cart WHERE customer_id = $1;"
    cart_id = await db.connection.fetchval(query, customer_id)
    return cart_id
        


@form_router.callback_query(lambda cb: cb.data == "cart")
async def show_cart(callback_query: CallbackQuery):
    await callback_query.answer()
    user_cart_id = await get_customer_cart(callback_query.from_user.id)
    db = App_DB_Connection()
    await db.connect()
    query = """WITH products AS (
    SELECT product_id, quantity
    FROM product_in_cart 
    WHERE cart_id = $1
)
SELECT 
    p.id,
    p.title, 
    p.price, 
    pr.quantity
FROM product p
JOIN products pr ON p.id = pr.product_id;
"""

    products_in_cart = await db.connection.fetch(query, user_cart_id)
    message = "Заказ:\n\n"
    if not products_in_cart:
        message = "Заказ пуст"
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=message)

    for product in products_in_cart:
        message += f"{product['title']}\n {product['price']} {product['quantity']}"
        kb = InlineKeyboardBuilder()
        kb.button(text="Удалить из корзины",
                  callback_data=f"delete_{product['id']}")
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=message,
                               reply_markup=kb.as_markup())

@form_router.callback_query(lambda cb: "delete" in cb.data)
async def delete_from_cart(callback_query: CallbackQuery):
    product_id = int(str(callback_query.data).split("_")[1])
    query = """DELETE FROM product_in_cart WHERE product_id = $1;"""
    db = App_DB_Connection()
    await db.connect()
    await db.connection.execute(query, product_id)
    await callback_query.answer("Продукт удален")
