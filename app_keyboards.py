from aiogram.utils.keyboard import InlineKeyboardBuilder

main_kb = InlineKeyboardBuilder()
main_kb.button(text="Каталог",
               callback_data="catalog")
main_kb.button(text="Корзина",
               callback_data="cart")
main_kb.button(text="FAQ",
               callback_data="faq")
main_kb.adjust(2, repeat=True)


categories_kb = InlineKeyboardBuilder()
categories_kb.button(text="Категория1",
                     callback_data="category1")
