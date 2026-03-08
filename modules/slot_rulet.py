import sys
import os
import sqlite3
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ParseMode

from main.config import dp, bot, chats, main_path
from path import Path

curent_path = Path(__file__).parent.parent
kasik_path = curent_path / 'databases' / 'kasik.db'

TRIPLES = {1: "бар", 64: "777", 22: "ягоды", 43: "лимон"}

@dp.message_handler(
    Text(startswith=["!рулетка", "! рулетка"], ignore_case=True),
    content_types=ContentType.TEXT,
    is_forwarded=False,
)
async def slot_roulette(message: types.Message):
    X_BET = 10
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list = []
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return

    if message.chat.id == message.from_user.id:
        await message.answer("📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!")
        return

    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    user = message.from_user
    user_id = user.id
    user_mention = user.get_mention(as_html=True)

    if getattr(user, "is_bot", False):
        await message.answer("🤖 Боты не могут играть в рулетку!")
        return

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        period_str = cursor.execute('SELECT period FROM default_periods WHERE command = ? AND chat = ?', ('slot_roulette', message.chat.id)).fetchall()[0][0]
        time_value, time_unit = period_str.split()
        time_value = int(time_value)
        if time_unit in ['ч', 'час', 'часа', 'часов']:
            cd_delta = timedelta(hours=time_value)
        elif time_unit in ['мин', 'минут', 'минута', 'минуты']:
            cd_delta = timedelta(minutes=time_value)
        elif time_unit in ['д', 'день', 'дня', 'дней', 'сутки']:
            cd_delta = timedelta(days=time_value)
        else:
            cd_delta = timedelta(minutes=15)

    except (IndexError, ValueError):
        cd_delta = timedelta(minutes=15)


    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS ruletka (user_id INTEGER PRIMARY KEY, last_date TEXT)')
    connection.commit()
    try:
        cursor.execute("SELECT last_date FROM ruletka WHERE user_id = ?", (user_id,))
        lst = datetime.strptime(cursor.fetchall()[0][0], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst
        if delta > cd_delta:
            pass
        else:
            delta = cd_delta - delta
            sec = int(str(delta.total_seconds()).split('.')[0])
            hours = sec // 3600
            minutes = (sec % 3600) // 60
            hours_text = f'{hours} ч ' if hours else ''
            minutes_text = f'{minutes} мин ' if minutes else ''
            try:
                await message.answer(f'❌Можно играть в рулетку только раз в {period_str}. Следующая игра через {hours_text}{minutes_text}', parse_mode=ParseMode.HTML)
            except UnboundLocalError:
                await message.answer(f'❌Можно играть в рулетку только раз в 15 минут. Следующая игра через {hours_text}{minutes_text}', parse_mode=ParseMode.HTML)
        
            connection.close()
            return
    except IndexError:
        pass
    connection.close()

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    bet = None
    for part in message.text.replace(",", " ").split():
        if part.isdigit():
            bet = int(part)
            break

    if bet is None or bet <= 0:
        await message.answer("📝Укажи ставку: !рулетка {число}")
        return

    try:
        row = cursor.execute("SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchone()
        meshok = row[0] if row is not None else 0
    except sqlite3.Error:
        connection.close()
        await message.answer("⚠️Ошибка доступа к базе данных.")
        return

    if meshok < bet:
        await message.answer(f"💰 У тебя недостаточно монет.\nВ мешке: 🍊 {meshok} eZ¢\nСтавка: 🍊 {bet} eZ¢")
        connection.close()
        return

    connection_kasik = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor_kasik = connection_kasik.cursor()
    cursor_kasik.execute('CREATE TABLE IF NOT EXISTS ruletka (user_id INTEGER PRIMARY KEY, last_date TEXT)')
    connection_kasik.commit()
    try:
        cursor_kasik.execute('INSERT INTO ruletka (user_id, last_date) VALUES (?, ?)', (user_id, datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
    except sqlite3.IntegrityError:
        cursor_kasik.execute('UPDATE ruletka SET last_date = ? WHERE user_id = ?', (datetime.now().strftime("%H:%M:%S %d.%m.%Y"), user_id))
    connection_kasik.commit()
    connection_kasik.close()

    dice_msg = await bot.send_dice(message.chat.id, emoji="🎰")
    dice_value = dice_msg.dice.value

    triple_name = TRIPLES.get(dice_value)
    
    if triple_name:
        win_amount = bet*X_BET
        new_meshok = meshok + win_amount
        cursor.execute("UPDATE farma SET meshok = ? WHERE user_id = ?", (new_meshok, user_id))
        connection.commit()
        result_text = (
            f"🎰 <b>Рулетка</b>\n\n"
            f"{user_mention} ставит 🍊 <b>{bet} eZ¢</b>\n\n"
            f"🎉 <b>ТРИПЛЛ {triple_name.upper()}!</b>\n"
            f"✅ Выигрыш: 🍊 <b>{win_amount} eZ¢</b> (x{X_BET})\n\n"
            f"💼 В мешке: 🍊 <b>{new_meshok} eZ¢</b>"
        )
    else:
        new_meshok = meshok - bet
        cursor.execute("UPDATE farma SET meshok = ? WHERE user_id = ?", (new_meshok, user_id))
        connection.commit()
        result_text = (
            f"🎰 <b>Рулетка</b>\n\n"
            f"{user_mention} ставит 🍊 <b>{bet} eZ¢</b>\n\n"
            f"❌ Не повезло. Ставка сгорела.\n\n"
            f"💼 В мешке: 🍊 <b>{new_meshok} eZ¢</b>"
        )
    await asyncio.sleep(2)
    connection.close()
    await bot.send_message(message.chat.id, result_text, parse_mode=ParseMode.HTML)
