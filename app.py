import asyncio

async def main() -> None:
    from data.config import init_categories, init_titles
    await init_categories()
    await init_titles()
    from app_logger import logger
    logger.debug(f"init app.py")
    from handlers import form_router
    from loader import bot, dp
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

