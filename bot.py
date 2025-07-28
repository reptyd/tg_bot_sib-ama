
import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import user, operator
from config import BOT_TOKEN
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

async def main():
    dp.include_router(user.router)
    dp.include_router(operator.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
