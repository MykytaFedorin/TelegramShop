from aiogram.fsm.state import State, StatesGroup


class CatalogStates(StatesGroup):
    categories = State()
    subcategories = State()
    show_products = State()
    adjust_quantity = State()

class CartStates(StatesGroup):
    get_addres = State()

class FaqStates(StatesGroup):
    faq = State()
