from loader import form_router, bot
from asyncpg.exceptions import UniqueViolationError
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
from handlers.cart import show_cart
import app_queries

logger.debug(f"init catalog.py {root_categories}")

@form_router.callback_query(lambda cb: cb.data == "catalog")
async def show_categories(callback_query: CallbackQuery, 
                          state: FSMContext):
    """Обработчик для нажатия кнопки Каталог в главном меню"""
    logger.info(f"Юзер нажал каталог")
    await callback_query.answer()
    await state.set_state(CatalogStates.categories)
    cats = await choose_root(root_categories) 
    keyboard = app_kb.AppCategoryKeyboard(cats)
    kb_page = await keyboard.show_page()
    await callback_query.message.edit_text(f"Выберите категорию товара: 1",
                                           reply_markup=kb_page.as_markup())


async def choose_root(categories):
    """Функция для выбора только
    корневых категорий в каталоге"""

    res = []
    for cat in categories:
        if cat["parent_id"] is None:
            res.append(cat)
    logger.debug(categories)
    return res 


async def choose_subcategory(parent_category: str) -> List[Dict]:
    """Выбирает все подкатегории из данной категории"""
    chosen_categories = []
    parent_id = None
    for cat in root_categories:
        if cat["category_name"] == parent_category:
            parent_id = cat["id"]
            break
    for cat in root_categories:
        if cat["parent_id"] is parent_id:
            chosen_categories.append(cat)
    return chosen_categories


@form_router.callback_query(AppCbStateFilter(states=[CatalogStates.categories],
                                             cb_values=root_cat_titles))
async def handle_category_choosing(callback_query: CallbackQuery):
    """Обработчик для показа всех подкатегорий
    выбранной пользователем категории или продуктов, если подкатегорий нет"""
    logger.info(f"Юзер выбрал категорию {callback_query.data}")
    chosen_category = str(callback_query.data)
    await callback_query.answer()
    subcategories = await choose_subcategory(str(chosen_category))
    if not subcategories:
        await send_products(callback_query,
                            chosen_category)
    logger.debug(subcategories)
    keyboard = app_kb.AppCategoryKeyboard(subcategories)
    kb = await keyboard.show_page()
    await callback_query.message.edit_text(text="subcategories",
                                           reply_markup=kb.as_markup())

async def get_category_id(category_name: str) -> Optional[int]:
    """Находит id категории по ее имени"""
    db = App_DB_Connection()
    await db.connect()
    try:
        get_id_query = "SELECT id FROM category WHERE category_name = $1;"
        category_id = await db.connection.fetchval(get_id_query, category_name)
        return category_id
    except Exception as ex:
        logger.error(f"Error fetching category id for '{category_name}': {ex}")
        return None
    finally:
        await db.close()


async def send_products(callback_query: CallbackQuery, category: str) -> None:
    logger.debug("send_products")
    category_id = await get_category_id(category)
    logger.debug(f"category_id: {category_id}")
    
    async with App_DB_Connection() as db:
        get_product = "SELECT id, photo_path, description FROM product WHERE category_id = $1;"
        products = await db.connection.fetch(get_product, category_id)
        logger.debug(products) 
        for product in products:
            logger.debug(f"product: {product['photo_path']}")
            await show_product(callback_query,
                               product["id"],
                               product["photo_path"],
                               product["description"])

import os
import asyncio
from aiogram.types.input_file import FSInputFile
from aiogram.exceptions import TelegramNetworkError

async def show_product(callback_query: CallbackQuery,
                       product_id: int,
                       image_path: str,
                       caption: str) -> None:
    kb = InlineKeyboardBuilder()
    kb.button(text="Купить",
              callback_data=f"buy_{product_id}")
    try:
        if not os.path.exists(image_path):
            logger.error(f"Файл {image_path} не найден.")
            await callback_query.answer("Изображение не найдено.", show_alert=True)
            return

        if os.path.getsize(image_path) > 20 * 1024 * 1024:
            logger.error(f"Файл {image_path} превышает допустимый размер.")
            await callback_query.answer("Файл слишком большой для отправки.", show_alert=True)
            return

        if not os.access(image_path, os.R_OK):
            logger.error(f"Нет прав на чтение файла {image_path}.")
            await callback_query.answer("Ошибка доступа к изображению.", show_alert=True)
            return

        if not caption:
            caption = "Описание отсутствует."

        if len(caption) > 1024:
            caption = caption[:1021] + "..."

        image_file = FSInputFile(image_path)
        
        for attempt in range(3):
            try:
                await bot.send_photo(
                    chat_id=callback_query.from_user.id,
                    photo=image_file,
                    caption=caption,
                    reply_markup=kb.as_markup()
                )
                break
            except TelegramNetworkError as e:
                logger.warning(f"Попытка отправки: {attempt + 1}, Ошибка: {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2)

        await callback_query.answer()

    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await callback_query.answer("Ошибка при отправке изображения.", show_alert=True)


async def create_cart(customer_id: int):
    db = App_DB_Connection()
    await db.connect()
    query = """WITH cart_exist AS (
    SELECT id 
    FROM cart 
    WHERE customer_id = $1 AND status = 'pending'
), 
inserted_cart AS (
    INSERT INTO cart (price, status, customer_id)
    SELECT 0.00, 'pending', $1
    WHERE NOT EXISTS (SELECT 1 FROM cart_exist)
    RETURNING id
)
SELECT id 
FROM cart_exist
UNION ALL
SELECT id 
FROM inserted_cart;
;
"""
    return await db.connection.fetchval(query, customer_id)



@form_router.callback_query(lambda cb: "buy" in cb.data)
async def handle_buying(callback_query: CallbackQuery,
                        state: FSMContext):
    product_id = int(str(callback_query.data).split("_")[1])
    cart_id = await create_cart(callback_query.from_user.id)
    logger.debug(f"cart_id: {cart_id}")
    await state.update_data(cart_id=cart_id)
    await state.update_data(quantity=1)
    await state.update_data(product_id=product_id)
    await callback_query.answer()
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="Выберите кол-во: 1",
                           reply_markup=app_kb.quantity_kb.as_markup())


@form_router.callback_query(lambda cb: cb.data in ["plus", "minus"])
async def handle_quantity_changing(callback_query: CallbackQuery,
                                   state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    quantity = int(data["quantity"])
    if callback_query.data == "plus":
        quantity += 1
        await state.update_data(quantity=quantity)
    else:
        quantity -= 1
        await state.update_data(quantity=quantity)
    await callback_query.message.edit_text(f"Выберите кол-во: {quantity}",
                                           reply_markup=app_kb.quantity_kb.as_markup())

async def add_product_to_cart(product_id: int, 
                              cart_id: int,
                              quantity: int):
    db = App_DB_Connection()
    await db.connect()
    query = """INSERT INTO product_in_cart (product_id, cart_id, quantity) VALUES ($1, $2, $3);"""
    try:
        await db.connection.execute(query, product_id, cart_id, quantity)
    except UniqueViolationError as ex:
        query = """UPDATE product_in_cart SET quantity = quantity + $1 
        WHERE cart_id = $2 AND product_id = $3;"""
        await db.connection.execute(query, quantity, cart_id, product_id)
    query = """WITH prices AS (
            SELECT price 
            FROM product 
            WHERE id = $1
            )
            UPDATE cart
            SET price = price + (SELECT price * $2 FROM prices)
            WHERE id = $3;
            """
    await db.connection.execute(query, product_id, quantity, cart_id)


@form_router.callback_query(lambda cb: cb.data == "continue")
async def continue_to_purchase(callback_query: CallbackQuery,
                               state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    product_id = data["product_id"]
    quantity = data["quantity"]
    await add_product_to_cart(product_id,
                              data["cart_id"],
                              quantity)
    await show_cart(callback_query, state)
