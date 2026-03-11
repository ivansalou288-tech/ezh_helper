import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main.secret import admin_token as token
from aiogram import Router, Bot, Dispatcher, types, F
from path import Path
import datetime
import aiogram
from aiogram.filters import Command
import password_generator
import main.secret

TOKEN = token
bot = Bot(token=TOKEN)
router = Router(name=__name__)
import asyncio
import json

MINIAPP_LINKS_URL = "https://ezh-dev.ru/ezh_helper/admin/client/index.html"
#? EN: Handles /start command and shows admin bot main menu with available actions.
#* RU: Обрабатывает команду /start и показывает главное меню админ-бота с доступными действиями.
@router.message(Command(commands="start"))
async def start(message: types.Message):
    print(message.from_user.id)
    buttons = [

        types.InlineKeyboardButton(
            text="MiniApp",
            web_app=types.WebAppInfo(url=MINIAPP_LINKS_URL),
        ),
        
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])

    await message.answer("Приветствуем в админ боте\n\nЧто хочешь сделать?", reply_markup=keyboard)




async def main() -> None:
    try:
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
    
        dp.include_router(router)
    
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(e)
        await main()
if __name__ == "__main__":

    asyncio.run(main())