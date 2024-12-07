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
    cart_id = db.connection.fetchval(query, customer_id)
    return cart_id
        


@form_router.callback_query(lambda cb: cb.data == "cart")
async def show_cart(callback_query: CallbackQuery):
    user_cart_id = await get_customer_cart(callback_query.from_user.id)
    db = App_DB_Connection()
    await db.connect()
    query = """WITH products AS (
    SELECT product_id 
    FROM product_in_cart 
    WHERE cart_id = $1
)
SELECT * 
FROM product 
WHERE product_id IN (SELECT product_id FROM products);

            """
    products_in_cart = db.connection.fetch(user_cart_id)
    logger.debug(products_in_cart)
