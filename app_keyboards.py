from aiogram.utils.keyboard import InlineKeyboardBuilder
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Tuple
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

quantity_kb = InlineKeyboardBuilder()
quantity_kb.button(text="+", callback_data="plus")
quantity_kb.button(text="-", callback_data="minus")

class AppInlineButton(NamedTuple):
    name: str
    callback_data: str


class AppInlineKeyboard(ABC):
    page = 1 # сначала видна 1 страница кнопок
    page_size = 9 # размер страницы
    row_size = 3 # ширина строки
    keyboard: List[AppInlineButton]


    async def show_page(self) -> InlineKeyboardBuilder:
        """Возвращает часть всей клавиатуры,
           которая соответствует актуальной странице"""
        logger.debug("show_page func")
        kb = InlineKeyboardBuilder()
        start_index, end_index = await self.get_btn_range()
        try:
            chosen_btns = self.keyboard[start_index:end_index]
            await self.create_page(kb=kb,
                             btns=chosen_btns)
            return kb
        except IndexError as ex:
            logger.error(f"Ошибка создания клвавиатуры: {ex}") 
        finally:
            await self.add_ctrl_kb(kb)
            return kb
    

    async def get_btn_range(self) -> Tuple:
        """Возвращает нужный диапазон индексов кнопок
           исходя из актуальных настроек клавиатуры"""
        logger.debug("get_btn_range_func")
        start_index = (self.page-1) * self.page_size
        end_index = (self.page-1) * self.page_size + self.page_size
        if end_index > len(self.keyboard):
            end_index = len(self.keyboard)
        return start_index, end_index


    async def create_page(self,
                          kb: InlineKeyboardBuilder, 
                          btns: List[AppInlineButton]) -> None: 
        """Создает InlineKeyboardBuilder из списка кнопок"""
        logger.debug("create_page func")
        for btn in btns:
            kb.button(text=btn.name,
                      callback_data=btn.callback_data)


    async def add_ctrl_kb(self, kb: InlineKeyboardBuilder) -> None:
        """Добавляет в клавиатуру кнопки управления"""
        logger.debug("add_ctrl_kb func")
        if (self.page == 1 and
            self.page_size < len(self.keyboard)):
            kb.button(text="Вперед",
                      callback_data="next_page")

        elif self.page == len(self.keyboard) / self.page_size:
            kb.button(text="Назад",
                      callback_data="previous_page")

        elif len(self.keyboard) < self.page_size: 
            pass
        else:
            kb.button(text="Назад",
                      callback_data="previous_page")
            kb.button(text="Вперед",
                      callback_data="next_page")
        kb.adjust(self.row_size,
                  repeat=True)


    async def switch_page(self, direction: ShiftDirection) -> None:
        """Меняет актуальную страницу в настройках клавиатуры"""
        logger.debug("switch_page func")
        if direction is ShiftDirection.BACK:
            self.page = self.page - 1
        elif direction is ShiftDirection.FORWARD:
            self.page = self.page + 1


class AppCategoryKeyboard(AppInlineKeyboard):


    def __init__(self, categories):
        logger.debug("AppInlineBtn init")
        self.keyboard = []
        for category in categories:
            name = category["category_name"]
            btn = AppInlineButton(name=name,
                                  callback_data=name)
            self.keyboard.append(btn)




category_kb = AppCategoryKeyboard(root_categories)
