from loader import form_router, bot, dp
from aiogram.types.inline_query import InlineQuery
from aiogram.types import CallbackQuery
from aiogram import types
from app_logger import logger
from app_states import FaqStates
from aiogram.fsm.context import FSMContext
from database.db_connection import App_DB_Connection


@form_router.callback_query(lambda cb: cb.data == "faq")
async def send_faq_intro(callback_query: CallbackQuery,
                         state: FSMContext):
    await callback_query.answer()
    await state.set_state(FaqStates.faq)
    await bot.send_message(chat_id = callback_query.from_user.id,
                           text="Введите вопрос") 


@form_router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    logger.debug("here")

    results = []
    db = App_DB_Connection()
    await db.connect()
    query = """SELECT * FROM question"""
    questions = await db.connection.fetch(query)
    if inline_query.query:
        for question in questions:
            if inline_query.query in question["text"] :
                results.append(
                    types.InlineQueryResultArticle(
                        id=str(question['id']),
                        title=str(question["text"]),
                        input_message_content=types.InputTextMessageContent(message_text=question["answer"]),
                    )
                )

    await inline_query.answer(results, is_personal=True)

