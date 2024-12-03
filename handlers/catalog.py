from loader import form_router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext


@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Send hello message and continue to introduce rules and policy
    """
    await message.answer("Привет")

