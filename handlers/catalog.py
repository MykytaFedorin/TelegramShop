from loader import form_router, bot
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery
import app_keyboards as app_kb
from data.config import data_dir_path
from aiogram.fsm.context import FSMContext
from app_states import CatalogStates
from app_logger import logger
from typing import Dict, List


@form_router.callback_query(lambda cb: cb.data == "catalog")
async def show_categories(callback_query: CallbackQuery, 
                          state: FSMContext):
    from data.config import root_categories
    logger.info(f"Юзер нажал каталог")
    logger.debug(f"root_cat: {root_categories}")
    await callback_query.answer()
    await state.set_state(CatalogStates.categories)
    keyboard = app_kb.AppCategoryKeyboard(root_categories)
    kb_page = await keyboard.show_page()
    await callback_query.message.edit_text(f"Выберите категорию товара: 1",
                                           reply_markup=kb_page.as_markup())

async def choose_subcategory(parent_id: int) -> List[Dict]:
    chosen_categories = []
    for cat in root_categories:
        if cat["parent_id"] is parent_id:
            chosen_categories.append(cat)
    return chosen_categories


@form_router.callback_query(lambda cb: cb.data in root_cat_titles)
async def show_subcategories(callback_query: CallbackQuery,
                             state: FSMContext):
    logger.info(f"Юзер выбрал категорию {callback_query.data}")
    await callback_query.answer()
    await state.set_state(CatalogStates.subcategories)
    subcategories = choose_subcategory(int(str(callback_query.data)))
    keyboard = app_kb.AppCategoryKeyboard(subcategories)
    kb = await keyboard.show_page()
    await callback_query.message.edit_text(text="subcategories",
                                           reply_markup=kb.as_markup())

async def show_product(callback_query: CallbackQuery):
    image_path = f"{data_dir_path}/avatar.jpg"
    image_file = FSInputFile(image_path) 
    await callback_query.answer()
    await bot.send_photo(
        chat_id=callback_query.from_user.id,
        photo=image_file,
        caption="Вот ваше изображение!"
    )
