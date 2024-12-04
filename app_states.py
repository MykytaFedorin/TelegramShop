from aiogram.fsm.state import State, StatesGroup


class CatalogStates(StatesGroup):
    categories = State()
    subcategories = State()
    show_products = State()
    adjust_quantity = State()
