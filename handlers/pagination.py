from aiogram.filters import Filter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import app_keyboards as app_kb
from app_enums import ShiftDirection
from app_states import CatalogStates
from loader import form_router
from app_logger import logger


# Кастомный фильтр для объединения условий
class PageSwitchFilter(Filter):
    def __init__(self, states: list):
        self.states = states

    async def __call__(self, callback: CallbackQuery, state: FSMContext) -> bool:
        current_state = await state.get_state()
        logger.debug(f"current_state {current_state}")
        logger.debug(f"data {callback.data}")
        return callback.data in ["next_page", "previous_page"] and current_state in self.states


# Регистрация обработчиков
@form_router.callback_query(PageSwitchFilter([CatalogStates.categories]))
async def switch_page_categories(callback_query: CallbackQuery, state: FSMContext):

    logger.info(f"Юзер нажал кнопку погинации в категориях")
    kb = await update_keyboard(callback_query, app_kb.category_kb)
    await callback_query.message.edit_text("Категории", reply_markup=kb.as_markup())


@form_router.callback_query(PageSwitchFilter([CatalogStates.subcategories]))
async def switch_page_subcategories(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"Юзер нажал кнопку погинации в подкатегориях")
    kb = await update_keyboard(callback_query, app_kb.subcategory_kb)
    await callback_query.message.edit_text("Подкатегории", reply_markup=kb.as_markup())


# Вспомогательная функция для обновления клавиатуры
async def update_keyboard(callback_query: CallbackQuery,
                          keyboard: app_kb.AppInlineKeyboard) -> InlineKeyboardBuilder:
    await callback_query.answer()
    if callback_query.data == "next_page":
        await keyboard.switch_page(ShiftDirection.FORWARD)
    else:
        await keyboard.switch_page(ShiftDirection.BACK)
    return await keyboard.show_page()

