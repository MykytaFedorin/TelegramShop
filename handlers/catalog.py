from loader import form_router, bot
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery, Message
from app_keyboards import categories_kb 
from data.config import data_dir_path



@form_router.callback_query(lambda cb: cb.data == "catalog")
async def show_categories(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Выберите категорию товара:",
                                           reply_markup=categories_kb.as_markup())


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

