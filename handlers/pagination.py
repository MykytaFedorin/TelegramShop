from loader import form_router, bot
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery
import app_keyboards as app_kb
from data.config import data_dir_path
from aiogram.fsm.context import FSMContext
import app_keyboards as app_kb
from app_enums import ShiftDirection


@form_router.callback_query(lambda callback: callback.data in ["next_page", "previous_page"])
async def switch_page(callback_query: CallbackQuery):
    await callback_query.answer()
    if callback_query.data == "next_page":
        await app_kb.category_kb.switch_page(ShiftDirection.FORWARD)
    else:
        await app_kb.category_kb.switch_page(ShiftDirection.BACK)
    kb = await app_kb.category_kb.show_page()
    await callback_query.message.edit_text("Page",
                                           reply_markup=kb.as_markup())
