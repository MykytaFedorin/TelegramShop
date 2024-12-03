from loader import form_router, bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus
from app_logger import logger
from data.config import GROUP_ID, CHANEL_ID


async def check_subscription(user_id: int,
                             chat_id: str) -> bool:
    try:
        logger.info(f"Проверяю подписку {user_id} на {chat_id}")
        member_type = await bot.get_chat_member(chat_id=chat_id,
                                                user_id=user_id)
        status = member_type.status in [ChatMemberStatus.CREATOR,
                                 ChatMemberStatus.MEMBER]
        logger.debug(f"Статус юзера в {chat_id}: {member_type.status}")
        return status
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False


@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Проверяет подписан ли юзер на группу и канал
    """
    logger.info(f"Новый пользователь {message.from_user.id} " 
                f"активировал бота")
    group_sub = await check_subscription(message.from_user.id, GROUP_ID)
    chanel_sub = await check_subscription(message.from_user.id, CHANEL_ID)

    if group_sub and chanel_sub:
        await message.answer("Привет, все гуд!")
    else:
        await message.answer(f"Пожалуйста, подпишитесь на "
                             f"{GROUP_ID} и {CHANEL_ID},"
                             f"что бы продолжить общение с ботом.")

    

