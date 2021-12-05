from aiogram import executor

from .bot import create_bot

if __name__ == "__main__":
    dp = create_bot()
    executor.start_polling(dp)
