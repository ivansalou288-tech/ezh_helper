from aiogram import types, F, Router, Dispatcher, Bot
from aiogram.filters import Command
from aiogram.enums import ParseMode
import asyncio
import random
import string
import html
from datetime import datetime


from aiogram.utils.markdown import hlink
import sys
import os
TOKEN = '8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q'
router = Router(name=__name__)
  
@router.message(F.text.lower().startswith(('ник')))
async def show_nik(message, bot: Bot):
  
    buttons = [
        types.InlineKeyboardButton(
            text="MiniApp",
            web_app=types.WebAppInfo(url=MINIAPP_LINKS_URL),
        ),
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    await message.answer(text="Админ панель", reply_markup=keyboard)

    

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
