from aiogram.utils.keyboard import InlineKeyboardBuilder
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app_enums import ShiftDirection
from app_logger import logger
import database.db_connection as db
from data.config import root_categories

main_kb = InlineKeyboardBuilder()
main_kb.button(text="Каталог",
               callback_data="catalog")
main_kb.button(text="Корзина",
               callback_data="cart")
main_kb.button(text="FAQ",
               callback_data="faq")
main_kb.adjust(2, repeat=True)



class AppInlineKeyboard(ABC):
    page = 1
    size = 40
    page_size = 9
    row_size = 3
    keyboard: List[Dict[str, Any]]


    async def show_page(self) -> InlineKeyboardBuilder:
        kb = InlineKeyboardBuilder()
        start_index = (self.page-1) * self.page_size
        end_index = (self.page-1) * self.page_size + self.page_size
        if end_index > len(self.keyboard):
            end_index = len(self.keyboard)
        try:
            for i in range(start_index, end_index):
                for text, callback_data in self.keyboard[i].items():
                    kb.button(text=text,
                              callback_data=callback_data)
        except IndexError as ex:
            logger.error(f"Ошибка создания клвавиатуры: {ex}") 
        await self.add_ctrl_kb(kb)
        return kb


    async def add_ctrl_kb(self, kb: InlineKeyboardBuilder) -> None:
        if self.page == 1:
            kb.button(text="Вперед",
                      callback_data="next_page")
        elif self.page == self.size / self.page_size:
            kb.button(text="Назад",
                      callback_data="previous_page")
        else: 
            kb.button(text="Назад",
                      callback_data="previous_page")
            kb.button(text="Вперед",
                      callback_data="next_page")
        kb.adjust(self.row_size,
                  repeat=True)


    async def switch_page(self, direction: ShiftDirection) -> None:
        if direction is ShiftDirection.BACK:
            self.page = self.page - 1
        elif direction is ShiftDirection.FORWARD:
            self.page = self.page + 1


class AppCategoryKeyboard(AppInlineKeyboard):


    def __init__(self, categories):
        self.keyboard = []
        for category in categories:
            name = category['category_name']
            self.keyboard.append({f"{name}":
                                  f"{name}"})


category_kb = AppCategoryKeyboard(root_categories)
