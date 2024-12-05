import asyncio

async def main() -> None:
    from handlers import form_router
    from loader import bot, dp
    from data.config import init_categories
    await init_categories()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

