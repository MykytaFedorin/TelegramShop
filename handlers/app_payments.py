from aiogram import Bot, Dispatcher, types, F
from database.db_connection import App_DB_Connection
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from loader import form_router, bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yookassa import Configuration, Payment
from data.config import SHOP_ID, SHOP_SECRET_KEY
from app_logger import logger
from aiogram.types import PreCheckoutQuery
from app_states import CartStates

Configuration.account_id = SHOP_ID
Configuration.secret_key = SHOP_SECRET_KEY


@form_router.pre_checkout_query(CartStates.payment)
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    logger.debug("pre_checkout")
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@form_router.message(lambda message: not (message.successful_payment is None))
async def process_successful_payment(message: types.Message,
                                     state: FSMContext):
    logger.debug("HERE")
    try:
        data = await state.get_data()
        logger.debug(data)
        address = data["address"]
        cart_id = data["cart_id"]
        db = App_DB_Connection()
        await db.connect()
        query = """UPDATE cart SET delivery_info = $1, status = 'payed' WHERE id = $2;"""
        await db.connection.execute(query, address, cart_id)
        logger.debug("Платёж прошёл успешно!")
        await message.reply("Спасибо за оплату!")
    except Exception as ex:
        logger.debug(ex)
        await message.answer("Ошибка")
