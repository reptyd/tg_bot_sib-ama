
import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import user, operator
from aiogram.client.bot import DefaultBotProperties
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

async def main():
    dp.include_router(user.router)
    dp.include_router(operator.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
