from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import app_keyboards as app_kb
from app_enums import ShiftDirection
from app_states import CatalogStates
from loader import form_router
from app_logger import logger
from app_filters import AppCbStateFilter


@form_router.callback_query(AppCbStateFilter(states=[CatalogStates.categories],
                                             cb_values=["next_page",
                                                        "previous_page"]))
async def switch_page_categories(callback_query: CallbackQuery):
    """Обработчик для нажатых кнопок вперед, назад"""
    logger.info(f"Юзер нажал кнопку погинации в категориях")
    kb = await update_keyboard(callback_query, app_kb.category_kb)
    await callback_query.message.edit_text("Категории", reply_markup=kb.as_markup())


async def update_keyboard(callback_query: CallbackQuery,
                          keyboard: app_kb.AppInlineKeyboard) -> InlineKeyboardBuilder:
    """Функция обновления клавиатуры в направлении пагинации"""
    await callback_query.answer()
    if callback_query.data == "next_page":
        await keyboard.switch_page(ShiftDirection.FORWARD)
    else:
        await keyboard.switch_page(ShiftDirection.BACK)
    return await keyboard.show_page()

