from loader import form_router, bot
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery
import app_keyboards as app_kb
from data.config import data_dir_path
from aiogram.fsm.context import FSMContext
from app_states import CatalogStates
from app_logger import logger
from typing import Dict, List, Optional
from data.config import root_categories, root_cat_titles
from app_filters import AppCbStateFilter
from database.db_connection import App_DB_Connection
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
        get_product = "SELECT photo_path, description FROM product WHERE category = $1;"
        products = await db.connection.fetch(get_product, category_id)
        logger.debug(products) 
        for product in products:
            logger.debug(f"product: {product['photo_path']}")
            await show_product(callback_query,
                               product["photo_path"],
                               product["description"])

import os
import asyncio
from aiogram.types.input_file import FSInputFile
from aiogram.exceptions import TelegramNetworkError

async def show_product(callback_query: CallbackQuery,
                       image_path: str,
                       caption: str) -> None:
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

        for attempt in range(3):  # Повторная попытка
            try:
                await bot.send_photo(
                    chat_id=callback_query.from_user.id,
                    photo=image_file,
                    caption=caption
                )
                break
            except TelegramNetworkError as e:
                logger.warning(f"Попытка отправки: {attempt + 1}, Ошибка: {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2)

        await callback_query.answer()  # Ответ клиенту о выполнении

    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await callback_query.answer("Ошибка при отправке изображения.", show_alert=True)

