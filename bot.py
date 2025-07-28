import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import user, operator
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

async def set_bot_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать обращение"),
        BotCommand(command="help", description="Как пользоваться ботом")
    ])

async def main():
    await set_bot_commands()
    dp.include_router(user.router)
    dp.include_router(operator.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
