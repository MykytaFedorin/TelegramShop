from aiogram.filters import Filter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app_logger import logger
from typing import List, Any
from aiogram.fsm.state import State, StatesGroup


class AppCbStateFilter(Filter):
    def __init__(self, states: List[State],
                 cb_values: List[Any]):
        self.states = states
        self.cb_values = cb_values

    async def __call__(self,
                       callback: CallbackQuery,
                       state: FSMContext) -> bool:
        current_state = await state.get_state()
        logger.debug(f"current_state {current_state}")
        logger.debug(f"data {callback.data}")
        return (callback.data in self.cb_values
                and current_state in self.states)


