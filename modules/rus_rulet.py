import sys
import os
import random
from datetime import datetime, timedelta
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ParseMode, ChatPermissions

from main.config import dp, bot, chats, mute_user, main_path


#? EN: Chat command for playing Russian roulette: user risks getting muted for a short time (1/6 chance) in group chats.
#* RU: Команда чата для игры в русскую рулетку: пользователь рискует получить короткий мут (шанс 1 из 6) в групповых чатах.
@dp.message_handler(
    Text(startswith=["! русская рулетка", "!русская рулетка", ".русская рулетка", "/русская рулетка", "русская рулетка"], ignore_case=True),
    content_types=ContentType.TEXT,
    is_forwarded=False,
)
async def russian_roulette(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return
    MUTE_TIME = 5
    # Только групповые чаты
    if message.chat.id == message.from_user.id:
        await message.answer("📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!")
        return
    
    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    user = message.from_user
    user_id = user.id
    user_mention = user.get_mention(as_html=True)
    
    # Не даем играть ботам
    if getattr(user, "is_bot", False):
        await message.answer("🤖 Боты не могут играть в русскую рулетку!")
        return

    # Русская рулетка: 1 из 6 патронов (вероятность смерти 1/6)
    is_dead = random.randint(1, 6) == 1

    if is_dead:
        # Пользователь умер - даем мут на 5 минут


            a = await mute_user(user_id, message.chat.id, MUTE_TIME, 'мин', message, '')
            if a == True:
                result_text = (
                    f"💀 <b>Русская рулетка</b>\n\n"
                    f"{user_mention} нажал на спусковой крючок...\n\n"
                    f"🔫 <b>БАБАХ!</b>\n\n"
                    f"❌ К сожалению, в патроннике был патрон. Вы получили мут на 5 минут.\n\n"
                    f"⏰ Мут закончится через {MUTE_TIME} минут"
                )
            else:
                result_text = (
                    f"💀 <b>Русская рулетка</b>\n\n"
                    f"{user_mention} нажал на спусковой крючок...\n\n"
                    f"🔫 <b>БАБАХ!</b>\n\n"
                    f"❌ К сожалению, в патроннике был патрон. Вы получили мут на 5 минут.\n\n"
                    f"⏰ Мут закончится через {MUTE_TIME} минут"
                )

    
    else:
        # Пользователь выжил
        result_text = (
            f"🎰 <b>Русская рулетка</b>\n\n"
            f"{user_mention} нажал на спусковой крючок...\n\n"
            f"✨ <i>Щелчок</i>\n\n"
            f"✅ Вам повезло! Патронник был пуст. Вы остались живы!"
        )

    await bot.send_message(
        message.chat.id,
        result_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

