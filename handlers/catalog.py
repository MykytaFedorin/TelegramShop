from loader import form_router, bot
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery
import app_keyboards as app_kb
from data.config import data_dir_path
from aiogram.fsm.context import FSMContext


@form_router.callback_query(lambda cb: cb.data == "catalog")
async def show_categories(callback_query: CallbackQuery):
    kb = await app_kb.category_kb.show_page()
    await callback_query.message.edit_text(f"Выберите категорию товара: 1",
                                           reply_markup=kb.as_markup())


@form_router.callback_query(lambda cb: cb.data in ["category1"])
async def show_subcategories(callback_query: CallbackQuery):
    image_path = f"{data_dir_path}/avatar.jpg"
    image_file = FSInputFile(image_path) 
    await callback_query.answer()
    await bot.send_photo(
        chat_id=callback_query.from_user.id,
        photo=image_file,
        caption="Вот ваше изображение!"
    )

