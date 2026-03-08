import random

from aiogram import Router, types
from aiogram.types import ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main.config31 import *

router = Router()

#? EN: Main farm command – gives a random amount of eZ¢ once every 4 hours to the user's bag.
#* RU: Основная команда фарма – добавляет случайное количество eZ¢ в мешок пользователя не чаще одного раза в 4 часа.
@router.message(lambda message: message.text and any(message.text.lower().startswith(cmd) for cmd in ['фарма', 'ферма', 'раб раб работать']))
async def farm(message: Message):
    # Initialize database for this chat if it doesn't exist
    init_chat_db(message.chat.id)
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Check black list
    black_list = []
    try:
        blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
        for i in blk:
            black_list.append(i[0])
    except sqlite3.OperationalError:
        pass

    if message.from_user.id in black_list:
        await message.answer(text=f'{krest}<b>НЕЗАЧЕТ!</b> Работать на ферме можно только с процентами ежу, а ты не скидывался на покушать н1 разрабу)', parse_mode='html')
        connection.close()
        return
    
    user_id = message.from_user.id
    delta_bust = random.randint(3, 150)
    
    # Use all_path database for farma table
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()
    try:
        meshok_old = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        meshok_old = 0
    
    try:
        cursor_all.execute(f"SELECT last_date FROM farma WHERE user_id = ?", (user_id,))
        date_result = cursor_all.fetchall()
        if not date_result:
            # First time farming - create record and give reward
            meshok_new = meshok_old + delta_bust
            cursor_all.execute('INSERT INTO farma (user_id, meshok, last_date) VALUES (?, ?, ?)', 
                         (user_id, meshok_new, datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
            await message.answer(f'{gal} <b>ЗАЧЁТ!</b> {money} +{delta_bust} eZ¢', parse_mode='html')
            connection_all.commit()
            connection_all.close()
            return
        
        lst = datetime.strptime(date_result[0][0], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst
        print(delta)
        
        if delta > timedelta(hours=4):
            meshok_new = meshok_old + delta_bust
            cursor_all.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (meshok_new, user_id))
            cursor_all.execute('UPDATE farma SET last_date = ? WHERE user_id = ?', 
                         (datetime.now().strftime("%H:%M:%S %d.%m.%Y"), user_id))
            await message.answer(f'{gal} <b>ЗАЧЁТ!</b> {money} +{delta_bust} eZ¢', parse_mode='html')
            connection_all.commit()
        else:
            delta = timedelta(hours=4) - delta
            days = delta.days * 24
            sec = int(str(delta.total_seconds()).split('.')[0])

            hours = sec // 3600 - days
            minutes = (sec % 3600) // 60
            days = delta.days

            if days == 0:
                days_text = ''
            else:
                days_text = f'{days} дн '
            if hours == 0:
                hours_text = ''
            else:
                hours_text = f'{hours} ч '
            if minutes == 0:
                minutes_text = ''
            else:
                minutes_text = f'{minutes} мин '

            lst_date = f'{days_text}{hours_text}{minutes_text}'
            await message.answer(f'{krest}<b>НЕЗАЧЕТ!</b> Фармить можно раз в 4 часа.\nСледующая добыча через {lst_date}', parse_mode='html')
    except IndexError:
        meshok_new = meshok_old + delta_bust
        cursor_all.execute('INSERT INTO farma (user_id, meshok, last_date) VALUES (?, ?, ?)', 
                     (user_id, meshok_new, datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
        await message.answer(f'{gal} <b>ЗАЧЁТ!</b> {money} +{delta_bust} eZ¢', parse_mode='html')
        connection_all.commit()
    finally:
        connection.close()
        connection_all.close()


#? EN: Shows how many eZ¢ are currently stored in the specified user's bag (by @, reply, or self).
#* RU: Показывает, сколько eZ¢ сейчас лежит в мешке указанного пользователя (по @, ответу или себе).
@router.message(lambda message: message.text and message.text.lower().startswith('мешок'))
async def mesh(message: Message):
    # Initialize database for this chat if it doesn't exist
    init_chat_db(message.chat.id)
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()

    user_id = await get_user_id_self(message)
    username = GetUserByID(user_id, message.chat.id).username
    name_user = GetUserByID(user_id, message.chat.id).nik
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()
    try:
        meshok_old = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        meshok_old = 0
    
    await message.answer(f'{mesh_money} В мешке <a href="https://t.me/{username}">{name_user}</a>: {money} {meshok_old}  eZ¢', 
                        parse_mode='html', disable_web_page_preview=True)
    connection.close()
    connection_all.close()


#? EN: Starts the transfer UI to send eZ¢ from your bag to another user with adjustable amount.
#* RU: Запускает интерфейс перевода eZ¢ из твоего мешка другому пользователю с настраиваемой суммой.
@router.message(lambda message: message.text and message.text.lower().startswith('! перевести'))
async def perevod_start(message: Message):
    # Initialize database for this chat if it doesn't exist
    init_chat_db(message.chat.id)
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    if message.chat.id not in chats:
        await message.answer('кыш')
        connection.close()
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply(
            '📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',
            parse_mode='html')
        connection.close()
        return
    
    self_id = message.from_user.id
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()
    try:
        meshok_self = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (self_id,)).fetchall()[0][0]
    except IndexError:
        await message.answer('Твой мешок пустой! Иди работай а потом переводи')
        connection_all.close()
        return
    
    if meshok_self < 100:
        await message.answer('Твой мешок пустой! Иди работай а потом переводи')
        connection_all.close()
        return
    
    try:
        meshok_user = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.answer('Не удалось найти информацию о мешке получателя')
        connection_all.close()
        return

    perev = 100

    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])
    
    message_id = (await message.answer(text=f'{mesh_money} В твоем мешке: {money} {meshok_self}  eZ¢\nТвой перевод: {perev}', 
                                       parse_mode='html', reply_markup=keyboard)).message_id
    
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()
    
    try:
        cursor_all.execute('INSERT INTO perevod (self_id, user_id, mess_id, stavka) VALUES (?, ?, ?, ?)', 
                     (self_id, user_id, message_id, 100))
        connection_all.commit()
    except sqlite3.IntegrityError:
        cursor_all.execute('UPDATE perevod SET stavka = ? WHERE self_id = ?', (100, self_id))
        connection_all.commit()
        cursor_all.execute('UPDATE perevod SET mess_id = ? WHERE self_id = ?', (message_id, self_id))
        connection_all.commit()
        cursor_all.execute('UPDATE perevod SET user_id = ? WHERE self_id = ?', (user_id, self_id))
        connection_all.commit()
    finally:
        connection.close()
        connection_all.close()


#? EN: Increases the planned transfer amount by 1000 eZ¢ (if the sender has enough coins).
#* RU: Увеличивает сумму перевода на 1000 eZ¢ (если у отправителя достаточно монет).
@router.callback_query(lambda query: query.data == 'pls_1000')
async def plus_1000(call: CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    try:
        meshok = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Твой мешок пустой!')
        connection.close()
        connection_all.close()
        return

    try:
        stavka = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', 
                              (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Не для тебя кнопку создавали')
        connection.close()
        connection_all.close()
        return
    
    if (int(stavka) + 1000) > int(meshok):
        await call.answer(text='У тебя нет столько деняг!')
        connection.close()
        connection_all.close()
        return
    
    cursor_all.execute('UPDATE perevod SET stavka = stavka+1000 WHERE self_id = ?', (call.from_user.id,))
    connection_all.commit()
    
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_text(text=f'{mesh_money} В твоем мешке: {money} {meshok}  eZ¢\nТвой перевод: {stavka+1000}',
                               parse_mode='html', reply_markup=keyboard)
    await call.answer()
    connection.close()
    connection_all.close()
    connection_all.close()

#? EN: Decreases the planned transfer amount by 1000 eZ¢ but not below 100.
#* RU: Уменьшает сумму перевода на 1000 eZ¢, но не ниже 100.
@router.callback_query(lambda query: query.data == 'min_1000')
async def minus_1000(call: CallbackQuery):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    try:
        meshok = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Твой мешок пустой!')
        connection.close()
        connection_all.close()
        return

    try:
        stavka = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', 
                              (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Не для тебя кнопку создавали')
        connection.close()
        connection_all.close()
        return
    
    if (int(stavka) - 1000) < 100:
        await call.answer(text='перевод не может быть меньше 100')
        connection.close()
        connection_all.close()
        return
    
    cursor_all.execute('UPDATE perevod SET stavka = stavka-1000 WHERE self_id = ?', (call.from_user.id,))
    connection_all.commit()
    
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])
    
    await call.message.edit_text(text=f'{mesh_money} В твоем мешке: {money} {meshok}  eZ¢\nТвой перевод: {stavka-1000}',
                               parse_mode='html', reply_markup=keyboard)
    await call.answer()
    connection.close()
    connection_all.close()

#? EN: Increases the planned transfer amount by 50 000 eZ¢ (large step).
#* RU: Увеличивает сумму перевода на 50 000 eZ¢ (крупный шаг).
@router.callback_query(lambda query: query.data == 'pls_50')
async def plus_50k(call: CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    try:
        meshok = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Твой мешок пустой!')
        connection.close()
        connection_all.close()
        return

    try:
        stavka = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', 
                              (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Не для тебя кнопку создавали')
        connection.close()
        connection_all.close()
        return
    
    if (int(stavka) + 50000) > int(meshok):
        await call.answer(text='У тебя нет столько деняг!')
        connection.close()
        connection_all.close()
        return
    
    cursor_all.execute('UPDATE perevod SET stavka = stavka+50000 WHERE self_id = ?', (call.from_user.id,))
    connection_all.commit()
    
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_text(text=f'{mesh_money} В твоем мешке: {money} {meshok}  eZ¢\nТвой перевод: {stavka+50000}',
                               parse_mode='html', reply_markup=keyboard)
    await call.answer()
    connection.close()
    connection_all.close()

#? EN: Decreases the planned transfer amount by 50 000 eZ¢ but not below 100.
#* RU: Уменьшает сумму перевода на 50 000 eZ¢, но не ниже 100.
@router.callback_query(lambda query: query.data == 'min_50')
async def minus_50k(call: CallbackQuery):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    try:
        meshok = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Твой мешок пустой!')
        connection.close()
        connection_all.close()
        return

    try:
        stavka = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', 
                              (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Не для тебя кнопку создавали')
        connection.close()
        connection_all.close()
        return
    
    if (int(stavka) - 50000) < 100:
        await call.answer(text='перевод не может быть меньше 100')
        connection.close()
        connection_all.close()
        return
    
    cursor_all.execute('UPDATE perevod SET stavka = stavka-50000 WHERE self_id = ?', (call.from_user.id,))
    connection_all.commit()
    
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_text(text=f'{mesh_money} В твоем мешке: {money} {meshok}  eZ¢\nТвой перевод: {stavka-50000}',
                               parse_mode='html', reply_markup=keyboard)
    await call.answer()
    connection.close()
    connection_all.close()

#? EN: Increases the planned transfer amount by 100 eZ¢ (small step).
#* RU: Увеличивает сумму перевода на 100 eZ¢ (малый шаг).
@router.callback_query(lambda query: query.data == 'pls_100')
async def plus_100(call: CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    try:
        meshok = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Твой мешок пустой!')
        connection.close()
        connection_all.close()
        return

    try:
        stavka = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', 
                              (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Не для тебя кнопку создавали')
        connection.close()
        connection_all.close()
        return
    
    if (int(stavka) + 100) > int(meshok):
        await call.answer(text='У тебя нет столько деняг!')
        connection.close()
        connection_all.close()
        return
    
    cursor_all.execute('UPDATE perevod SET stavka = stavka+100 WHERE self_id = ?', (call.from_user.id,))
    connection_all.commit()
    
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_text(text=f'{mesh_money} В твоем мешке: {money} {meshok}  eZ¢\nТвой перевод: {stavka+100}',
                               parse_mode='html', reply_markup=keyboard)
    await call.answer()
    connection.close()
    connection_all.close()

#? EN: Decreases the planned transfer amount by 100 eZ¢ but not below 100.
#* RU: Уменьшает сумму перевода на 100 eZ¢, но не ниже 100.
@router.callback_query(lambda query: query.data == 'min_100')
async def minus_100(call: CallbackQuery):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    try:
        meshok = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Твой мешок пустой!')
        connection.close()
        connection_all.close()
        return

    try:
        stavka = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', 
                              (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Не для тебя кнопку создавали')
        connection.close()
        connection_all.close()
        return
    
    if (int(stavka) - 100) < 100:
        await call.answer(text='перевод не может быть меньше 100')
        connection.close()
        connection_all.close()
        return
    
    cursor_all.execute('UPDATE perevod SET stavka = stavka-100 WHERE self_id = ?', (call.from_user.id,))
    connection_all.commit()
    
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_text(text=f'{mesh_money} В твоем мешке: {money} {meshok}  eZ¢\nТвой перевод: {stavka-100}',
                               parse_mode='html', reply_markup=keyboard)
    await call.answer()
    connection.close()
    connection_all.close()

#? EN: Sets the planned transfer amount to the full current balance of the sender's bag.
#* RU: Устанавливает сумму перевода равной всему текущему балансу мешка отправителя.
@router.callback_query(lambda query: query.data == 'all_p')
async def all_perevod(call: CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    try:
        meshok = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Твой мешок пустой!')
        connection.close()
        connection_all.close()
        return

    try:
        stavka = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', 
                              (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.answer(text='Не для тебя кнопку создавали')
        connection.close()
        connection_all.close()
        return

    cursor_all.execute('UPDATE perevod SET stavka = ? WHERE self_id = ?', (meshok, call.from_user.id,))
    connection_all.commit()
    
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_text(text=f'{mesh_money} В твоем мешке: {money} {meshok}  eZ¢\nТвой перевод: {meshok}',
                               parse_mode='html', reply_markup=keyboard)
    await call.answer()
    connection.close()
    connection_all.close()

#? EN: Confirms and performs the transfer: moves the selected eZ¢ from sender to recipient.
#* RU: Подтверждает и выполняет перевод: списывает выбранные eZ¢ с отправителя и зачисляет получателю.
@router.callback_query(lambda query: query.data == 'perev')
async def perev_confirm(call: CallbackQuery):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    connection_all = sqlite3.connect(all_path, check_same_thread=False)
    cursor_all = connection_all.cursor()

    result = cursor_all.execute('SELECT user_id FROM perevod WHERE self_id = ? AND mess_id = ?', 
                           (call.from_user.id, call.message.message_id)).fetchall()
    if not result:
        await call.message.answer('Запись о переводе не найдена. Попробуйте начать заново.')
        connection.close()
        connection_all.close()
        return
    
    user_id = result[0][0]
    self_id = call.from_user.id
    
    try:
        meshok_self = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (self_id,)).fetchall()[0][0]
    except IndexError:
        await call.message.answer('Твой мешок пустой! Иди работай а потом переводи')
        connection.close()
        connection_all.close()
        return
    
    try:
        meshok_user = cursor_all.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await call.message.answer('Не удалось найти информацию о мешке получателя')
        connection.close()
        connection_all.close()
        return

    stavka_result = cursor_all.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?',
                                (call.from_user.id, call.message.message_id)).fetchall()
    if not stavka_result:
        await call.message.answer('Запись о сумме перевода не найдена. Попробуйте начать заново.')
        connection.close()
        connection_all.close()
        return
    
    perev = stavka_result[0][0]

    cursor_all.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (meshok_user + perev, user_id))
    connection_all.commit()
    cursor_all.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (meshok_self - perev, self_id))
    connection_all.commit()
    cursor_all.execute('DELETE FROM perevod WHERE self_id = ?', (call.from_user.id,))
    connection_all.commit()
    
    await call.message.delete()
    await call.message.answer(text=f'Успешно', parse_mode='html')
    connection.close()
    connection_all.close()
