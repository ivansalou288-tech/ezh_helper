from aiogram import types, F, Router, Dispatcher, Bot
from aiogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
import asyncio
import random
import string
import html
from datetime import datetime

from config3 import *
from aiogram.utils.markdown import hlink
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.golden_rulet import router as golden_rulet_router
from modules.message_top import router as message_top_router
from modules.cubes import router as cubes_router
from modules.farm import router as farm_router
from modules.kasik import router as kasik_router
from aiogram.enums.chat_member_status import ChatMemberStatus
import main.secret 
# Add router to dispatcher
TOKEN = main.secret.main_token
router = Router(name=__name__)

page_b = 0
itog_b = []
itog = 0
page_c_b = 0





#? EN: Command for chat owners to bind their chat to admin panel
#* RU: Команда для владельцев чатов для привязки чата к админ-панели
@router.message(F.text.lower().startswith('!владелец'))
async def bind_chat_to_admin(message: types.Message, bot: Bot):
    """Привязывает чат к админ-панели для владельца чата"""
    
    # Проверяем, что команда используется в групповом чате
    if message.chat.id == message.from_user.id:
        await message.answer(f' {krest} Эта команда работает только в групповых чатах!', parse_mode='html')
        return
    
    # Проверяем, что чат в списке разрешенных

    init_all_db()
    init_admin_db() 
    init_chat_db(message.chat.id)


    try:
        # Получаем информацию о пользователе в чате
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        
        # Проверяем, что пользователь является владельцем
        if chat_member.status != ChatMemberStatus.CREATOR:
            await message.answer(f' {krest} Только владелец чата может использовать эту команду!', parse_mode='html')
            return
        connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute(f'UPDATE users SET rang = ? WHERE tg_id = ?',
                   (6, message.from_user.id))
        connection.commit()
        connection = sqlite3.connect(admin_path)
        cursor = connection.cursor()
        cursor.execute('INSERT OR IGNORE INTO creators (user_id, chat_id) VALUES (?, ?)', (message.from_user.id, message.chat.id))
        connection.commit()
       
        
    except Exception as e:
        print(f"Error in bind_chat_to_admin: {e}")
        await message.answer('❌ Произошла ошибка при выдачи прав. Попробуйте позже.')


#? EN: Handles /start command and shows main menu with options to join clan or indicate existing membership
#* RU: Обрабатывает команду /start и показывает главное меню с опциями вступления в клан или указания существующего членства
@router.message(CommandStart())
async def start(message: types.Message, bot: Bot):
    if message.chat.id != message.from_user.id:
        return
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass
    buttons = [
        types.InlineKeyboardButton(text="Вступить в клан", web_app=types.WebAppInfo(url='https://ezhqpy.ru/ezh_helper/new_chat_mem_dir/index.html')),

    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])

    await message.answer_photo(photo=FSInputFile(f'{curent_path}/photos/klan_ava.jpg'), reply_markup=keyboard, caption='Приветствуем тебя в нашем боте!\nЧто ты хочешь сделать?')




#? EN: Shows the saved custom nickname of a user in the chat, or warns if it is not set.
#* RU: Показывает сохранённый кастомный ник пользователя в чате или сообщает, что он не задан.
@router.message(F.text.lower().startswith(('ник')))
async def show_nik(message, bot: Bot):
    if len(message.text.split()[0]) != 3:
        return
    
    try:
        if len(message.text.split()[1]) > 0:
            try:
                message.text.split('@')[1]
            except IndexError:
                return
    except IndexError:
        pass
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        user_id = await get_user_id_self(message)
        name_user = GetUserByID(user_id, message.chat.id).nik

        tg_id = user_id
        try:
            nik = cursor.execute('SELECT nik FROM users WHERE tg_id = ?', (tg_id,)).fetchall()[0][0]
        except IndexError:
            await message.reply(f'<a href="tg://user?id={user_id}">Пользователь</a> не заполнил ник', parse_mode="html")
            return
        if nik == '':
            await message.reply(f'<a href="tg://user?id={user_id}">Пользователь</a> не заполнил ник', parse_mode="html")
        else:
            await message.reply(f'{desk_em}Ник <a href="tg://user?id={user_id}">пользователя</a>: «{nik}»', parse_mode="html")
    finally:
        connection.close()


#? EN: Changes your chat nickname (display name in clan tables) within a length limit.
#* RU: Изменяет твой ник в чате (отображаемое имя в клановых таблицах) с ограничением по длине.
@router.message(F.text.lower().startswith(('+ник')))
async def plus_nik(message, bot: Bot):
    if len(message.text.split()[0]) != 4:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        tg_id = message.from_user.id
        comments = " ".join(message.text.split(" ")[1:])

        if comments == '' or comments == " ":
            await message.reply('Ник не должен быть пустым')
            return
        if len(comments) > 50 and tg_id != 1240656726:
            await message.reply('Ник не должен быть длиннее 50 символов')
            return
        await message.reply(f'{gal} Ник {GetUserByID(message.from_user.id, message.chat.id).mention} изменён на «{comments}»',
                            parse_mode="html")
        cursor.execute('UPDATE users SET nik = ? WHERE tg_id = ?',
                       (comments, tg_id))
        connection.commit()
    finally:
        connection.close()


#? EN: Updates your in‑game nickname (PUBG nick) in clan-related tables.
#* RU: Обновляет твой игровой ник (PUBG ник) в клановых таблицах.
@router.message(F.text.lower().startswith(('+игровой ник')))
async def plus_igr_nik(message, bot: Bot):
    if len(message.text.split()[1]) != 3:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        tg_id = message.from_user.id
        comments = " ".join(message.text.split(" ")[2:])

        if comments == '' or comments == " ":
            await message.reply('Ник не должен быть пустым')
            return
        if len(comments) > 12:
            await message.reply('Не верный ник', parse_mode='html')
            return
        await message.reply(f' {gal} Игровой ник {GetUserByID(message.from_user.id, message.chat.id).mention} изменён на «{comments}»',
                            parse_mode="html")
        cursor.execute('UPDATE users SET nik_pubg = ? WHERE tg_id = ?',
                       (comments, tg_id))
        connection.commit()
    finally:
        connection.close()


#? EN: Updates your in‑game PUBG ID after validating its format (length and starting digit).
#* RU: Обновляет твой игровой PUBG ID после проверки формата (длина и первая цифра).
@router.message(F.text.lower().startswith(('+игровой айди')))
async def plus_igr_id(message, bot: Bot):
    if len(message.text.split()[1]) != 4:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        tg_id = message.from_user.id
        try:
            comments = int(message.text.split(" ")[2])
        except ValueError:
            await message.answer(f' {write_em} Некоректное айди', parse_mode='html')
            return

        def split_number(number):
            num = []
            while number > 0:
                digit = number % 10
                num.append(digit)
                number = number // 10
            return num[::-1]

        id_p = split_number(comments)
        if id_p[0] != 5 or len(str(comments)) < 9 or len(str(comments)) > 12:
            await message.answer(f' {write_em} Некоректное айди', parse_mode='html')
            return

        await message.reply(f' {gal} Айди {GetUserByID(message.from_user.id, message.chat.id).mention} изменён на «{comments}»',
                            parse_mode="html")
        cursor.execute('UPDATE users SET id_pubg = ? WHERE tg_id = ?',
                       (comments, tg_id))
        connection.commit()
    finally:
        connection.close()


#? EN: Shows a grouped list of chat admins by rank (owner, manager, deputies, etc.) with fun icons.
#* RU: Показывает сгруппированный по рангам список админов чата (владелец, менеджер, замы и т.д.) с веселыми иконками.
@router.message(F.text.lower().startswith(('кто админ')))
async def kto_admin(message, bot: Bot): 
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        shars = ['🎱', '🌍', '⚾', '🔮', '️🎾', '🥎', '🏐']
        
        # Get users by rank from users table
        cursor.execute('SELECT tg_id FROM users WHERE rang = ?', (6,))
        users_6rang = cursor.fetchall()
        rang_6 = []
        for user in users_6rang:
            nik = cursor.execute('SELECT nik FROM users WHERE tg_id = ?', (user[0],)).fetchall()[0][0]
            rang_6.append(f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{nik}</a>')

        cursor.execute('SELECT tg_id FROM users WHERE rang = ?', (5,))
        users_5rang = cursor.fetchall()
        rang_5 = []
        for user in users_5rang:
            nik = cursor.execute('SELECT nik FROM users WHERE tg_id = ?', (user[0],)).fetchall()[0][0]
            rang_5.append(f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{nik}</a>')

        cursor.execute('SELECT tg_id FROM users WHERE rang = ?', (4,))
        users_4rang = cursor.fetchall()
        rang_4 = []
        for user in users_4rang:
            nik = cursor.execute('SELECT nik FROM users WHERE tg_id = ?', (user[0],)).fetchall()[0][0]
            rang_4.append(f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{nik}</a>')

        cursor.execute('SELECT tg_id FROM users WHERE rang = ?', (3,))
        users_3rang = cursor.fetchall()
        rang_3 = []
        for user in users_3rang:
            nik = cursor.execute('SELECT nik FROM users WHERE tg_id = ?', (user[0],)).fetchall()[0][0]
            rang_3.append(f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{nik}</a>')

        cursor.execute('SELECT tg_id FROM users WHERE rang = ?', (2,))
        users_2rang = cursor.fetchall()
        rang_2 = []
        for user in users_2rang:
            nik = cursor.execute('SELECT nik FROM users WHERE tg_id = ?', (user[0],)).fetchall()[0][0]
            rang_2.append(f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{nik}</a>')

        cursor.execute('SELECT tg_id FROM users WHERE rang = ?', (1,))
        users_1rang = cursor.fetchall()
        rang_1 = []
        for user in users_1rang:
            nik = cursor.execute('SELECT nik FROM users WHERE tg_id = ?', (user[0],)).fetchall()[0][0]
            rang_1.append(f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{nik}</a>')
        
        r6 = "\n".join(rang_6)
        r5 = "\n".join(rang_5)
        r4 = "\n".join(rang_4)
        r3 = "\n".join(rang_3)
        r2 = "\n".join(rang_2)
        r1 = "\n".join(rang_1)
        
        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер', 'Владелец')
        
        rang6 = f'🎄🎄🎄🎄🎄🎄\n{rangs_name[6]}:\n{r6}\n\n' if r6 else ""
        rang5 = f'🎄🎄🎄🎄🎄\n{rangs_name[5]}:\n{r5}\n\n' if r5 else ""
        rang4 = f'🎄🎄🎄🎄\n{rangs_name[4]}:\n{r4}\n\n' if r4 else ""
        rang3 = f'🎄🎄🎄\n{rangs_name[3]}:\n{r3}\n\n' if r3 else ""
        rang2 = f'🎄🎄\n{rangs_name[2]}:\n{r2}\n\n' if r2 else ""
        rang1 = f'🎄\n{rangs_name[1]}:\n{r1}\n\n' if r1 else ""

        try:
            await message.reply(text=f'{rang6}{rang5}{rang4}{rang3}{rang2}{rang1}', parse_mode='html')
        except Exception:
            await message.reply('Админов в этом чате нет', parse_mode='html')
    
    except Exception as e:
        print(f"Error in kto_admin: {e}")
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
    finally:
        connection.close()


#? EN: Shows a full profile about yourself in this chat: status, description, warns, recommendations and activity.
#* RU: Показывает полный профиль о себе в этом чате: статус, описание, предупреждения, рекомендации и активность.
@router.message(F.text.lower().startswith(('кто я')))
async def kto_i(message, bot: Bot):
    if len(message.text) != 5:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        user_id = message.from_user.id
        try:
            clan_nik_user = cursor.execute("SELECT nik FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
        except IndexError:
            await message.reply(
                f'Полное описание <a href="tg://user?id={message.from_user.id}">Пользователя</a> не заполнено',
                parse_mode="html")
            return
        
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        status = chat_member.status
        
        if status == 'administrator':
            chat_status = '<i>👨🏻‍🔧 Телеграм-админ этого чата</i>'
        elif status == 'creator':
            chat_status = '<i>👨🏻‍🔧 Создатель этого чата</i>'
        elif status == 'member' or status == 'restricted':
            chat_status = '💚 Состоит в чате'
        else:
            chat_status = 'Неизвестно'

        about_user = await about_user_sdk(user_id, message.chat.id)
        try:
            rang = about_user.split('\n<b>👤Имя')[0]
        except AttributeError:
            return
        about_user = '\n<b>👤Имя' + about_user.split('\n<b>👤Имя')[1]
        
        warns = await warn_check_sdk(user_id, message.chat.id, clan_nik_user)
        profile_pictures = await bot.get_user_profile_photos(user_id)
        recom = await recom_check_sdk(user_id, clan_nik_user, message.chat.id)

        cursor.execute("SELECT * FROM users WHERE tg_id=?", (user_id,))
        users = cursor.fetchall()

        for user in users:
            user_about_list = {
                'last_date': user[8],
                'date_vhod': user[9]
            }
        
        if user_about_list['last_date'] == '' or user_about_list['last_date'] == None:
            lst_date = 'Неизвестно'
        else:
            last_date = user_about_list['last_date']
            lst = datetime.strptime(user_about_list['last_date'], "%H:%M:%S %d.%m.%Y")
            now = datetime.now()
            delta = now - lst

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

            if lst_date == '' or lst_date == None:
                lst_date = 'только что'

        if user_about_list['date_vhod'] == 'Неизвестно':
            date_vh = ''
        else:
            lst = datetime.strptime(user_about_list['date_vhod'], "%H:%M:%S %d.%m.%Y")
            now = datetime.now()
            delta = now - lst

            days = delta.days * 24
            sec = int(str(delta.total_seconds()).split('.')[0])

            hours = sec // 3600 - days
            minutes = (sec % 3600) // 60
            days = delta.days
            mouth = days // 30
            days = days % 30

            if mouth == 0:
                mouth_text = ''
            else:
                mouth_text = f'{mouth} мес '
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

            date_vh = f'({mouth_text}{days_text}{hours_text}{minutes_text})'
        
        itog_text = f'🎅Это пользователь <a href="tg://user?id={user_id}">{clan_nik_user}</a>\n{chat_status}\n\n{rang}\n\n<b>🧾Описание пользователя:</b>{about_user}\n<b>🕑Последнее сообщение:</b> {lst_date}\n🕰️<b>В клане c:</b> {user_about_list["date_vhod"]} {date_vh}\n\n📨Клановый ник: {clan_nik_user}\n\n{warns}\n\n{recom}'
        
        try:
            await bot.send_photo(chat_id=message.chat.id, photo=dict((profile_pictures.photos[0][0])).get("file_id"),
                                 caption=itog_text, parse_mode=ParseMode.HTML)
        except IndexError:
            await message.reply(itog_text, parse_mode=ParseMode.HTML)
    
    except Exception as e:
        print(f"Error in kto_i: {e}")
        await message.reply('Ошибка при получении информации о пользователе')
    finally:
        connection.close()


#? EN: Shows the same full profile as "кто я", but for another user mentioned or replied to.
#* RU: Показывает такой же полный профиль, как «кто я», но для другого пользователя (упоминание или ответ).
@router.message(F.text.lower().startswith(('кто ты')))
async def kto_ti(message, bot: Bot):
    if len(message.text.split()[1]) != 2:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        user_info = GetUserByMessage(message)
        if not user_info or not user_info.user_id:
            await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
            return

        user_id = user_info.user_id
        name_user = user_info.nik or "Пользователь"

        try:
            clan_nik_user = cursor.execute("SELECT nik FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
        except IndexError:
            await message.reply(
                f'Полное описание <a href="tg://user?id={user_id}">Пользователя</a> не заполнено',
                parse_mode="html")
            return
        
        chat_member = await bot.get_chat_member(message.chat.id, user_id)
        status = chat_member.status
        
        if status == 'administrator':
            chat_status = '<i>👨🏻‍🔧 Телеграм-админ этого чата</i>'
        elif status == 'creator':
            chat_status = '<i>👨🏻‍🔧 Создатель этого чата</i>'
        elif status == 'member' or status == 'restricted':
            chat_status = '💚 Состоит в чате'
        else:
            chat_status = 'Неизвестно'

        about_user = await about_user_sdk(user_id, message.chat.id)
        try:
            rang = about_user.split('\n<b>👤Имя')[0]
        except AttributeError:
            return
        about_user = '\n<b>👤Имя' + about_user.split('\n<b>👤Имя')[1]
        
        warns = await warn_check_sdk(user_id, message.chat.id, clan_nik_user)
        profile_pictures = await bot.get_user_profile_photos(user_id)
        recom = await recom_check_sdk(user_id, clan_nik_user, message.chat.id)

        cursor.execute("SELECT * FROM users WHERE tg_id=?", (user_id,))
        users = cursor.fetchall()

        for user in users:
            user_about_list = {
                'last_date': user[8],
                'date_vhod': user[9]
            }
        
        if user_about_list['last_date'] == '' or user_about_list['last_date'] == None:
            lst_date = 'Неизвестно'
        else:
            last_date = user_about_list['last_date']
            lst = datetime.strptime(user_about_list['last_date'], "%H:%M:%S %d.%m.%Y")
            now = datetime.now()
            delta = now - lst

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

            if lst_date == '' or lst_date == None:
                lst_date = 'только что'

        if user_about_list['date_vhod'] == 'Неизвестно':
            date_vh = ''
        else:
            lst = datetime.strptime(user_about_list['date_vhod'], "%H:%M:%S %d.%m.%Y")
            now = datetime.now()
            delta = now - lst

            days = delta.days * 24
            sec = int(str(delta.total_seconds()).split('.')[0])

            hours = sec // 3600 - days
            minutes = (sec % 3600) // 60
            days = delta.days
            mouth = days // 30
            days = days % 30

            if mouth == 0:
                mouth_text = ''
            else:
                mouth_text = f'{mouth} мес '
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

            date_vh = f'({mouth_text}{days_text}{hours_text}{minutes_text})'
        
        itog_text = f'🎅Это пользователь <a href="tg://user?id={user_id}">{clan_nik_user}</a>\n{chat_status}\n\n{rang}\n\n<b>🧾Описание пользователя:</b>{about_user}\n<b>🕑Последнее сообщение:</b> {lst_date}\n🕰️<b>В клане c:</b> {user_about_list["date_vhod"]} {date_vh}\n\n📨Клановый ник: {clan_nik_user}\n\n{warns}\n\n{recom}'
        
        try:
            await bot.send_photo(chat_id=message.chat.id, photo=dict((profile_pictures.photos[0][0])).get("file_id"),
                                 caption=itog_text, parse_mode=ParseMode.HTML)
        except IndexError:
            await message.reply(itog_text, parse_mode=ParseMode.HTML)
    
    except Exception as e:
        print(f"Error in kto_ti: {e}")
        await message.reply('Ошибка при получении информации о пользователе')
    finally:
        connection.close()


#? EN: Shows a paginated list of all removed warnings for a user, sent in private messages.
#* RU: Показывает постраничный список всех снятых предупреждений пользователя, отправляя его в личные сообщения.
@router.message(F.text.lower().startswith(('снятые преды', 'снятые варны')))
async def snatie_warns(message: types.Message, bot: Bot):
    global page, mes_id, itog, page_c
    # if len(message.text.split()[1:]) > 0 and '\n'.join(message.text.split('\n')[1:]) != ' '.join(message.text.split()[1:]):
    #     return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Check who can access this function
    can_chech_snat_pred = [8015726709, 1401086794, 1240656726]
    moder = message.from_user.id
    if moder not in can_chech_snat_pred:
        await message.reply(f'{write_em}Тебе не доступна эта функция', parse_mode='HTML')
        connection.close()
        return

    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        connection.close()
        return

    user_id = user_info.user_id
    name_user = user_info.nik or "Пользователь"
    
    # Reset pagination variables
    page = 0
    mes_id = 0
    itog = []
    page_c = 0
    
    # Query the warn_snat table for removed warnings
    cursor.execute("SELECT * FROM warn_snat WHERE user_id=?", (user_id,))
    all_warns = cursor.fetchall()
    connection.close()

    if not all_warns:
        await message.reply('Снятых предупреждений нет', parse_mode='html')
        return

    warns_count = len(all_warns)
    ar = []
    
    # Создаем кнопки навигации один раз перед циклом
    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="snat_list_back"),
        types.InlineKeyboardButton(text="▶️", callback_data="snat_list_next")
    ]
    
    for i, warn in enumerate(all_warns):
        warn_text = warn[1] if warn[1] else 'Без причины'
        moder_give_id = (warn[2]).split('ID: ')[1] if warn[2] else None
        moder_snat_id = warn[3] if warn[3] else None
        
        # Debug: print the raw values to see what's actually stored
        print(f"Debug: warn={warn}")
        print(f"Debug: warn[2] type={type(warn[2])}, value='{warn[2]}'")
        print(f"Debug: warn[3] type={type(warn[3])}, value='{warn[3]}'")
        
        # Simple text format without HTML to avoid parsing issues
        if moder_give_id and moder_snat_id:
            textt = f'🔸{i + 1}. От <a href="tg://user?id={moder_give_id}">{GetUserByID(moder_give_id, message.chat.id).nik}</a> | Снял: {moder_snat_id}\n&#8195&#8194Причина предупреждения: {warn_text}'
        elif moder_give_id:
            textt = f'🔸{i + 1}. От <a href="tg://user?id={moder_give_id}">{GetUserByID(moder_give_id, message.chat.id).nik}</a> | Снял: Неизвестный\n&#8195&#8194Причина предупреждения: {warn_text}'
        elif moder_snat_id:
            textt = f'🔸{i + 1}. От Неизвестный | Снял: {moder_snat_id}\n&#8195&#8194Причина предупреждения: {warn_text}'
        else:
            textt = f'🔸{i + 1}. От Неизвестный | Снял: Неизвестный\n&#8195&#8194Причина предупреждения: {warn_text}'
        ar.append(textt)
        if (i + 1) % 15 == 0 or i == warns_count - 1:
            itog.append('\n\n'.join(ar))
            ar.clear()

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])

    page_c = len(itog)
    try:
        await bot.send_message(message.from_user.id,
                            f'{desk_em}<b>Снятые предупреждения этого пользователя(страниц: {page_c}):</b>\n\n{itog[page]}',
                            parse_mode='html',
                            reply_markup=keyboard)
    except IndexError:
        await message.reply('Снятых предупреждений нет', parse_mode='html')
        return
    await message.answer(
        f'{desk_em}Список снятых предупреждений пользователя отправлен в <a href="https://t.me/werty_chat_manager_bot">лс</a>',
        parse_mode=ParseMode.HTML, disable_web_page_preview=True)


#? EN: Handles the "back" button in the removed-warns pagination, going to the previous page.
#* RU: Обрабатывает кнопку «◀️» в пагинации снятых предупреждений, переходя на предыдущую страницу.
@router.callback_query(F.data == "snat_list_back")
async def snat_list_back(call: types.CallbackQuery, bot: Bot):
    global page, page_c, itog
    
    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="snat_list_back"),
        types.InlineKeyboardButton(text="▶️", callback_data="snat_list_next")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])

    try:
        page -= 1
        if page < 0:
            await bot.answer_callback_query(call.id, text=f'{znak_yelow} это первая страница')
            page = 0  # Reset to first page
            return
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'{desk_em}<b>Снятые предупреждения этого пользователя(страниц: {page_c}):</b>\n\n{itog[page]}', 
            parse_mode='html',
            reply_markup=keyboard)
    except IndexError:
        page += 1  # Reset page if error
        await bot.answer_callback_query(call.id, text=f'{znak_yelow} это первая страница')
        return
    except Exception as e:
        print(f"Error in snat_list_back: {e}")
        return


#? EN: Handles the "next" button in the removed-warns pagination, going to the next page.
#* RU: Обрабатывает кнопку «▶️» в пагинации снятых предупреждений, переходя на следующую страницу.
@router.callback_query(F.data == "snat_list_next")
async def snat_list_next(call: types.CallbackQuery, bot: Bot):
    global page, page_c, itog

    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="snat_list_back"),
        types.InlineKeyboardButton(text="▶️", callback_data="snat_list_next")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])

    try:
        page += 1
        if page >= page_c:
            await bot.answer_callback_query(call.id, text=f'{znak_yelow} это последняя страница')
            page = page_c - 1  # Reset to last page
            return
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'{desk_em}<b>Снятые предупреждения этого пользователя(страниц: {page_c}):</b>\n\n{itog[page]}', 
            parse_mode='html',
            reply_markup=keyboard)
    except IndexError:
        page -= 1  # Reset page if error
        await bot.answer_callback_query(call.id, text=f'{znak_yelow} это последняя страница')
    except Exception as e:
        print(f"Error in snat_list_next: {e}")
        pass



#? EN: Replies with the current chat ID (useful for configuration and admin purposes).
#* RU: Отвечает айди текущего чата (удобно для настроек и админских задач).
@router.message(F.text.lower().startswith('/id') | F.text.startswith('!id') | F.text.startswith('! id'))  # * Функция узнавания айди чата
async def id_chat(message):
    await message.reply(f'айди чата "<code>{message.chat.id}</code>"', parse_mode='html')


#? EN: Simple latency check; when user sends "пинг", bot answers "ПОНГ" if command is correct.
#* RU: Простая проверка отклика; когда пользователь пишет «пинг», бот отвечает «ПОНГ» при корректной команде.
@router.message(F.text.lower().startswith('пинг'))  # * проверка работоспособности бота
async def ping(message):
    try:
        text = message.text.split(' ')[1]
    except IndexError:
        if len(message.text) > 4:
            return
        await message.reply("ПОНГ")


#? EN: Checks that the bot is alive; on "бот" without extra text replies that the bot is online.
#* RU: Проверяет, что бот работает; на «бот» без лишнего текста отвечает, что бот на месте.
@router.message(F.text.lower().startswith('бот'))  # * проверка работоспособности бота
async def bot_check(message):
    init_chat_db(message.chat.id)
    try:
        text = message.text.split(' ')[1]
    except IndexError:
        if len(message.text) > 3:
            return
        await message.reply(f'{gal} Бот на месте', parse_mode='html')

#? EN: Shows a paginated list of all banned users in the chat with ban details.
#* RU: Показывает постраничный список всех забаненных пользователей в чате с деталями бана.
@router.message(F.text.lower().startswith('банлист'))
async def ban_list(message: types.Message, bot: Bot):
    global page_b, page_c_b, itog_b
    print('ban list ')
    if len(message.text.split()[0]) != 7:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!', parse_mode='html')
        return
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    print('ban list 5')
    
    # Check if bans table exists
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='bans' ''')
    if not cursor.fetchone():
        await message.reply(f'{write_em}Таблица банов не найдена', parse_mode='html')
        connection.close()
        return
    
    try:
        cursor.execute(f"SELECT * FROM bans")
        all_bans = cursor.fetchall()
    except sqlite3.OperationalError:
        await message.reply(f'{write_em}Таблица банов не найдена', parse_mode='html')
        connection.close()
        return
    
    if not all_bans:
        await message.reply(f'{write_em}Список забаненных пуст', parse_mode='html')
        connection.close()
        return
    
    bans_count = len(all_bans)

    ar = []
    
    for i, ban in enumerate(all_bans):
        tg_id = ban[0]
        pubg_id = ban[1]
        prichina = ban[3]
        date = ban[4]
        user_men = ban[5]
        moder_men = ban[6]
        
        textt = f'{circle_em} {i + 1}. {user_men}\n👮♂️ Забанил: {moder_men}\n{mes_em} Причина: {prichina}\n⏰ Дата: {date}\n🎮 PUBG ID: <code>{pubg_id}</code>'
        ar.append(textt)
        print(ar)
        if (i+1) % 5 == 0 or i == bans_count - 1:
            itog_b.append(ar)
            ar = []
            
    

    page_b = 0
    page_c_b = len(itog_b)
    
    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="ban_back"),
        types.InlineKeyboardButton(text="▶️", callback_data="ban_next")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    print(itog_b, page_b, page_c_b)
    txt = "\n\n".join(itog_b[page_b])
    await message.reply(
        f'{desk_em}<b>Список забаненных пользователей (страниц: {page_c_b}):</b>\n\n{txt}',
        parse_mode='html',
        reply_markup=keyboard
    )
    connection.close()


#? EN: Handles the "back" button in the ban list pagination.
#* RU: Обрабатывает кнопку «◀️» в пагинации списка банов.
@router.callback_query(F.data == "ban_back")
async def ban_list_back(call: types.CallbackQuery, bot: Bot):
    global page_b, page_c_b, itog_b
    
    if page_b > 0:
        page_b -= 1
        buttons = [
            types.InlineKeyboardButton(text="◀️", callback_data="ban_back"),
            types.InlineKeyboardButton(text="▶️", callback_data="ban_next")
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
        txt = "\n\n".join(itog_b[page_b])
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'{desk_em}<b>Список забаненных пользователей (страниц: {page_c_b}):</b>\n\n{txt}',
            parse_mode='html',
            reply_markup=keyboard
        )
    await bot.answer_callback_query(call.id)


#? EN: Handles the "next" button in the ban list pagination.
#* RU: Обрабатывает кнопку «▶️» в пагинации списка банов.
@router.callback_query(F.data == "ban_next")
async def ban_list_next(call: types.CallbackQuery, bot: Bot):
    global page_b, page_c_b, itog_b
    
    if page_b < page_c_b - 1:
        page_b += 1
        buttons = [
            types.InlineKeyboardButton(text="◀️", callback_data="ban_back"),
            types.InlineKeyboardButton(text="▶️", callback_data="ban_next")
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
        txt = "\n\n".join(itog_b[page_b])
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'{desk_em}<b>Список забаненных пользователей (страниц: {page_c_b}):</b>\n\n{txt}',
            parse_mode='html',
            reply_markup=keyboard
        )
    await bot.answer_callback_query(call.id)


#? EN: Permanently bans a user from the chat with a specified reason; only for moderators with sufficient rank.
#* RU: Навсегда банит пользователя в чате с указанием причины; доступно только модераторам с достаточным рангом.
@router.message(F.text.lower().startswith('бан'))
async def ban(message, bot: Bot):
    # Проверка команды (бан = 3 символа)
    command = message.text.split()[0].lower()
    if len(command) != 3:
        return
    
    # Проверка, что команда используется в групповом чате
    
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    print('prover')
    # Проверка прав модератора
    moder_id = message.from_user.id
    moder_name = message.from_user.full_name
    moder_link = hlink(moder_name, f"tg://user?id={moder_id}")
    moder_permission = await is_successful_moder(moder_id, message.chat.id, 'ban')
    
    if moder_permission == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    
    if moder_permission == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    
    # Извлечение причины бана (текст после переноса строки)
    text_lines = message.text.split('\n')
    comments = '\n'.join(text_lines[1:]).strip() if len(text_lines) > 1 else ""
    
    # Получение информации о пользователе
    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        # Если GetUserByMessage не сработал, пробуем парсить юзернейм напрямую
        if len(message.text.split()) > 1:
            username = message.text.split()[1]
            if username.startswith('@'):
                # Создаем временный объект user_info для юзернейма
                user_id = username[1:]  # Убираем @
                name_user = username
                user_men = f'<a href="tg://user?id={user_id}">{name_user}</a>'
                moder_men = moder_link
                message_id = message.message_id
                
                # Выполняем бан напрямую
                result = await ban_user(user_id, message.chat.id, user_men, moder_men, comments, message_id, message, bot)
                if result == True:
                    await message.reply(
                        f'<b>{voscl}Внимание{voscl}</b>\n{circle_em}Злостный нарушитель {name_user} получает бан и покидает нас\n👮‍♂️Выгнал его: {moder_link}\n{mes_em}Выгнали его за: {comments}',
                        parse_mode='html')
                else:
                    await message.reply(result, parse_mode='html')
                return
            else:
                await message.reply(
                    f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',
                    parse_mode='html')
                return
        else:
            await message.reply(
                f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',
                parse_mode='html')
            return
    
    user_id = user_info.user_id
    
    # Проверка, что нельзя использовать команду на старшего/равного модератора
    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    
    # Получение имени пользователя
    name_user = user_info.nik or "Неизвестный"
    
    # Подготовка данных для бана
    user_men = f'<a href="tg://user?id={user_id}">{name_user}</a>'
    moder_men = moder_link
    message_id = message.message_id
    
    # Выполнение бана
    result = await ban_user(user_id, message.chat.id, user_men, moder_men, comments, message_id, message, bot)
    
    if result == True:
        await message.reply(
            f'<b>{voscl}Внимание{voscl}</b>\n{circle_em}Злостный нарушитель <a href="tg://user?id={user_id}">{name_user}</a> получает бан и покидает нас\n👮‍♂️Выгнал его: {moder_link}\n{mes_em}Выгнали его за: {comments}',
            parse_mode='html')
    else:
        await message.reply(result, parse_mode='html')
@router.message(F.text.lower().startswith(('анбан', 'разбан')))
async def unban(message, bot: Bot):
    if len(message.text.split()[0]) != 6:
        return
    
    try:
        if len(message.text.split()[1]) > 0:
            try:
                message.text.split('@')[1]
            except IndexError:
                return
    except IndexError:
        pass
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    moder_id = message.from_user.id
    moder_name = message.from_user.full_name
    moder_link = hlink(moder_name, f"tg://user?id={moder_id}")
    if await is_successful_moder(moder_id, message.chat.id, 'ban') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'ban') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    user_id = user_info.user_id
    name_user = user_info.nik or "Неизвестный"

    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    
    # Выполнение разбана
    result = await unban_user(message.chat.id, user_id, bot)
    if result == True:
        await message.reply(
            f'    Пользователь <a href="tg://user?id={user_id}">{name_user}</a> разбанен\n👮‍♂️Помиловал его: {moder_link}\n\n{mes_em}<a href="tg://user?id={user_id}">{name_user}</a>, мы ждем твоего возвращения!',
            parse_mode='html')
    else:
        await message.reply(result, parse_mode='html')


#? EN: Unbans a user and tries to send them an invite link to return to the chat.
#* RU: Разбанивает пользователя и пытается отправить ему ссылку-приглашение для возвращения в чат.
@router.message(F.text.lower().startswith('вернуть'))
async def returner(message, bot: Bot):
    if len(message.text.split()[0]) != 7:
        return
    
    try:
        if len(message.text.split()[1]) > 0:
            try:
                message.text.split('@')[1]
            except IndexError:
                return
    except IndexError:
        pass
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    moder_id = message.from_user.id
    moder_name = message.from_user.full_name
    moder_link = hlink(moder_name, f"tg://user?id={moder_id}")
    if await is_successful_moder(moder_id, message.chat.id, 'ban') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'ban') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    user_id = user_info.user_id
    name_user = user_info.nik or "Неизвестный"

    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    
    # Выполнение разбана
    result = await unban_user(message.chat.id, user_id, bot)
    if result == True:
        await message.reply(
            f'    Пользователь <a href="tg://user?id={user_id}">{name_user}</a> разбанен\n👮‍♂️Помиловал его: {moder_link}\n\n{mes_em}<a href="tg://user?id={user_id}">{name_user}</a>, мы ждем твоего возвращения!',
            parse_mode='html')
        try:
            link_chat = await bot.export_chat_invite_link(message.chat.id)
            await bot.send_message(chat_id=user_id, text=f'{desk_em} Вы были разбанены в чате <b>{message.chat.title}</b> вступить можно по ссылке: {link_chat}', parse_mode='html', disable_web_page_preview=True)
        except Exception as e:
            print(f"Error sending invite link: {e}")
    else:
        await message.reply(result, parse_mode='html')


#? EN: Shows the list of currently muted users in the chat when user sends the "муты" command.
#* RU: Показывает список текущих замьюченных пользователей в чате при вводе команды «муты».
@router.message(F.text.lower().startswith('муты'))  # * Функция размута
async def mutes_check(message, bot: Bot):
    print(f"Получена команда 'муты' от пользователя {message.from_user.id} в чате {message.chat.id}")
    
    # if len(message.text.split()[0]) != 4:
    #     return
    # Убираем строгую проверку на аргументы, позволяем использовать команду без дополнительных параметров


    if message.chat.id == message.from_user.id:
        print("Команда использована в личном чате")
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    print("Подключаюсь к базе данных...")
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()

    # Check if muts table exists
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='muts' ''')
    if not cursor.fetchone():
        print("Таблица muts не существует")
        await message.answer(f'⚪️ <b>Список пользователей, которым запрещено писать:</b>\n\n{mes_em} Список пока пуст', parse_mode=ParseMode.HTML)
        connection.close()
        return

    print("Таблица muts найдена, получаю данные...")
    cursor.execute(f"SELECT * FROM muts")
    all = cursor.fetchall()
    print(f"Найдено записей в muts: {len(all)}")

    if not all:
        print("Таблица muts пуста")
        await message.answer(f'⚪️ <b>Список пользователей, которым запрещено писать:</b>\n\n{mes_em} Список пока пуст', parse_mode=ParseMode.HTML)
        connection.close()
        return

    # Check if users table exists
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='users' ''')
    users_table_exists = cursor.fetchone() is not None
    print(f"Таблица users существует: {users_table_exists}")

    moders_mens = []
    dates = []
    rang_mut = []
    comments = []
    users_ids = []
    mutes_count = len(all)
    itog = []
    
    for i in range(mutes_count):
        users_ids.append(all[i][0])
        rang_mut.append(all[i][1])
        moders_mens.append(all[i][3])
        dates.append(all[i][4])
        comments.append(all[i][5])
    
    print(f"Обрабатываю {mutes_count} записей о мутах...")
    
    for i in range(mutes_count):
        print(users_ids[i])
        if users_table_exists:
            try:
                name_user = cursor.execute(f'SELECT nik FROM users WHERE tg_id = ?', (users_ids[i],)).fetchall()[0][0]
            except IndexError:
                name_user = 'Пользователь'
        else:
            name_user = 'Пользователь'
        print(name_user)
        textt = f'<b>{i + 1}</b>. <a href="tg://user?id={users_ids[i]}">{name_user}</a> [{rang_mut[i]}]\n⏱️ До {dates[i]}\n👮‍Заглушил: {moders_mens[i]}\n{mes_em}Причина: {comments[i]}'
        itog.append(textt)
    
    itog_text = '\n\n'.join(itog)
    if itog_text == '':
        itog_text = f'{mes_em} Список пока пуст'
    
    print("Отправляю ответ пользователю...")
    await message.answer(f'⚪️ <b>Список пользователей, которым запрещено писать:</b>\n\n{itog_text}',
                         parse_mode=ParseMode.HTML)
    connection.close()
    print("Функция mutes_check завершена")




#? EN: Mutes a user in the chat for a specified time with a reason; works only for allowed moderators.
#* RU: Замьючивает пользователя в чате на заданное время с указанием причины; доступно только разрешённым модераторам.
@router.message(F.text.lower().startswith('мут'))
async def mute(message, bot: Bot):
    global is_auto_unmute
    
    if len(message.text.split()[0]) != 3:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!', parse_mode='html')
        return
    
    # Парсинг аргументов команды
    parts = message.text.split()
    muteint = 1
    mutetype = "час"
    
    if len(parts) > 1:
        try:
            muteint = int(parts[1])
            mutetype = parts[2] if len(parts) > 2 else "час"
        except ValueError:
            mutetype = parts[1]
    
    # Проверка на упоминание пользователя в типе мута
    if '@' in mutetype:
        mutetype = 'час'
    
    # Валидация времени мута
    if muteint > 100:
        await message.reply('Слишком большое число! \n Делай меньше!', parse_mode='html')
        return
    if muteint <= 0:
        await message.reply('Неверное значение времени мута', parse_mode='html')
        return
    
    # Извлечение комментария
    comments = "\n".join(message.text.split("\n")[1:]).strip()
    
    # Проверка прав модератора
    moder_id = message.from_user.id
    
    moder_name = message.from_user.full_name
    moder_link = hlink(moder_name, f"tg://user?id={moder_id}")
    
    moder_status = await is_successful_moder(moder_id, message.chat.id, 'mut')
    if moder_status == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды', parse_mode='html')
        return
    elif moder_status == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    
    # Получение информации о пользователе
    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(
            f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',
            parse_mode='html')
        return
    
    user_id = user_info.user_id
    name_user = user_info.nik or "Пользователь"
    
    if not await is_more_moder(user_id, moder_id, message.chat.id):
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    
    # Выполнение мута
    result = await mute_user(user_id, message.chat.id, muteint, mutetype, message, comments, bot)
    
    if result == True:
        await message.reply(
            f'{mut_em} <b>Нарушитель:</b> <a href="tg://user?id={user_id}">{name_user}</a> лишается права слова\n'
            f'{time_em}<b>Срок наказания:</b> {muteint} {mutetype}\n'
            f'{zloy_cat}<b>Наказал его:</b> {moder_link}\n'
            f'{mes_em}<b>Нарушение: {comments}</b>',
            parse_mode='html')
    elif result != False:
        await message.reply(result, parse_mode='html')
    
    # if not is_auto_unmute:
    #     await auto_unmute(message, bot)


#? EN: Unmutes a user in the chat, returning them the ability to write messages.
#* RU: Размьючивает пользователя в чате, возвращая ему возможность писать сообщения.
@router.message(F.text.lower().startswith(('анмут', 'размут', '-мут')))
async def unmute(message, bot: Bot):
    # Проверка команды (unmute = 6 символов)
    command = message.text.split()[0].lower()
    if len(command) > 6:
        return
    
    # Проверка, что команда используется в групповом чате
    
    if len(message.text.split()[1:]) > 0 and '\n'.join(message.text.split('\n')[1:]) != ' '.join(message.text.split()[1:]):
        try:
            if message.text.split('@')[1] != "":
                pass
            else:
                return
        except IndexError:
            return
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!', parse_mode='html')
        return
    
    # Проверка прав модератора
    moder_id = message.from_user.id
    moder_permission = await is_successful_moder(moder_id, message.chat.id, 'mut')
    
    if moder_permission == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды', parse_mode='html')
        return
    
    if moder_permission == 'Need reg':
        await message.reply(
            f'{write_em} Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    
    # Получение информации о пользователе
    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(
            f'{write_em} Невозможно найти информацию о пользователе\n\n{mes_em} Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',
            parse_mode='html')
        return
    
    user_id = user_info.user_id
    
    # Проверка, что нельзя использовать команду на старшего/равного модератора
    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    
    # Получение имени пользователя
    name_user = user_info.nik or "Пользователь"
    
    # Подключение к базе данных
    connection = None
    try:
        connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
        cursor = connection.cursor()
        
        # Выполнение unmute
        result = await unmute_user(user_id, message.chat.id, message, bot)
        
        if result == True:
            await message.reply(
                f'{unmut_em}<a href="tg://user?id={user_id}">{name_user}</a> можешь говорить, но будь аккуратнее впредь\n\n{voscl}Правила чата можно посмотреть по команде «<code>правила</code>»',
                parse_mode='html')
        else:
            await message.reply(result, parse_mode='html')
        
        connection.commit()
    finally:
        if connection:
            connection.close()




# #? EN: Handles /start and /help commands in private chat, shows basic info, clan status and main navigation buttons.
# #* RU: Обрабатывает команды /start и /help в личных сообщениях, показывает основную информацию, статус в клане и основные кнопки навигации.
# @router.message(Command(commands=['start', 'help']))
# async def start(message, bot: Bot):
#     if message.chat.id != message.from_user.id:
#         return
    
#     # For private chat, we need to use a default chat or check if user is in any registered chat
#     # Let's use the first chat from the chats list as default for clan info
#     default_chat_id = chats[0] if chats else None
    
#     if default_chat_id:
#         about = await about_user_sdk(message.from_user.id, default_chat_id)
#         if about == '' or about == None:
#             is_in_klan = f'{krest}  Ты не участник клана'
#         else:
#             is_in_klan = f'Ты участник клана\n\n<b>Твое описание</b>\n{about}'
#     else:
#         is_in_klan = f'{krest}  Ты не участник клана'
    
#     buttons = [
#         types.InlineKeyboardButton(text="☎️  Менеджер", url='https://t.me/werty_pub'),
#         types.InlineKeyboardButton(text=f"📝 Регистрация", url="https://t.me/werty_clan_helper_bot"),
#         types.InlineKeyboardButton(text="Канал WERTY", url="https://t.me/Werty_Metro"),
#         types.InlineKeyboardButton(text="👨‍💻Нашел баг!(админ бота)", url="https://t.me/zzoobank")

#     ]

#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton(text="☎️  Менеджер", url='https://t.me/werty_pub')],
#         [types.InlineKeyboardButton(text=f"📝 Регистрация", url="https://t.me/werty_clan_helper_bot")],
#         [types.InlineKeyboardButton(text="Канал WERTY", url="https://t.me/Werty_Metro")],
#         [types.InlineKeyboardButton(text="👨‍💻Нашел баг!(админ бота)", url="https://t.me/zzoobank")],
#         [types.InlineKeyboardButton(text='⚒️ Команды', callback_data='commands')]
#     ])

#     await bot.send_photo(message.chat.id, photo=types.FSInputFile(f'{curent_path}/photos/klan_ava.jpg'), caption=f'Приветсвуем тебя в <b>WERTY | Чат-менеджер</b>\n\n{is_in_klan}\n\nЧто ты хочешь сделать?', parse_mode='html', reply_markup=keyboard)



#? EN: Shows active warnings (warns) for yourself or another user in this chat.
#* RU: Показывает активные предупреждения (варны) для себя или другого пользователя в этом чате.
@router.message(F.text.lower().startswith('варны') | F.text.lower().startswith('преды'))
async def warns_show(message, bot: Bot):
    if len(message.text.split()[0]) != 5:
        return
    
    if len(message.text.split()[1:]) > 0 and '\n'.join(message.text.split('\n')[1:]) != ' '.join(message.text.split()[1:]):
        try:
            message.text.split('@')[1]
        except IndexError:
            return
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em} Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!', parse_mode='html')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    
    user_id = await get_user_id_self(message)
    name_user = GetUserByID(user_id, message.chat.id).nik

    text = await warn_check_sdk(user_id, message.chat.id, name_user)
    await message.reply(text, parse_mode='html')


#? EN: Issues a new warning to a user with a reason, increases their warn counter and may auto-punish at 3 warns.
#* RU: Выдаёт пользователю новое предупреждение с указанием причины, увеличивает счётчик варнов и может автонаказать при трёх предупреждениях.
@router.message(F.text.lower().startswith('варн') | F.text.lower().startswith('пред'))
async def warns_give(message, bot: Bot):
    if len(message.text.split()[0]) != 4:
        return
    
    if len(message.text) > 0:
        a = ' '.join(message.text.split()[1:])
        print('text1', a)
        comm = ' '.join(message.text.split('\n')[1:])
        comm = ' '.join(comm.split())
        if comm == '' and len(a) > 1:
            return
        elif comm == a:
            pass
        else:
            print('text', comm)
            print((' '.join(a.split(comm))).strip())
            try:
                a = ' '.join(a.split(comm)).strip()
                username = a.split('@')[1]
            except IndexError:
                return
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    
    moder_id = message.from_user.id
    moder_link = GetUserByID(moder_id, message.chat.id).mention
    if await is_successful_moder(moder_id, message.chat.id, 'warn') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'warn') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    try:
        comments = "".join(message.text.split("\n")[1:])
    except IndexError:
        comments = ""
    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    user_id = user_info.user_id
    name_user = user_info.nik or "Пользователь"

    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    
    # Check current warn count
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM warns WHERE user_id = ?", (user_id,))
        warns_count = cursor.fetchone()[0]
        warn_count_new = warns_count + 1
        is_first = (warns_count == 0)
    except:
        warns_count = 0
        warn_count_new = 1
        is_first = True
    
    connection.close()

    await give_warn(message=message, comments=comments, user_id=user_id, is_first=is_first)
    await message.reply(
        f'🛑 Нарушитель <a href="tg://user?id={user_id}">{name_user}</a> нарушил правила и получает предупреждение <b>({warn_count_new}/3)</b>\n<b>👮‍♂️Поймал его:</b> {moder_link}\n<b>{mes_em}Нарушение:</b> {comments}\n\n<a href="tg://user?id={user_id}">{name_user}</a>, больше так не делай, соблюдай правила!',
        parse_mode='html')
    
    if warn_count_new == 3:
        await limit_warns(message)


#? EN: Removes a specific warning from a user (by warn number 1–3) and updates warn counter.
#* RU: Снимает конкретное предупреждение с пользователя (по номеру 1–3) и обновляет счётчик варнов.
@router.message(F.text.lower().startswith(('снять пред', 'снять варн')))
async def dell_warn(message, bot: Bot):
    if len(message.text.split()[1]) != 4:
        return
    
    a = 0
    if len(message.text.split()[2:]) > 0 and '\n'.join(message.text.split('\n')[2:]) != ' '.join(message.text.split()[2:]):
        try:
            message.text.split('@')[1]
            int(message.text.split(' ')[2])
        except IndexError:
            a += 1
        except ValueError:
             a += 1
    if a == 2:
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    
    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'warn') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'warn') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    user_id = user_info.user_id
    name_user = user_info.nik or "Пользователь"

    if message.chat.id == message.from_user.id:
        await message.answer('Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return

    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM warns WHERE user_id = ?", (user_id,))
        warns_count = cursor.fetchone()[0]
    except:
        warns_count = 0
    
    connection.close()

    if warns_count == 0:
        await message.reply(f'❕Предупреждения <a href="tg://user?id={user_id}">{name_user}</a> отсутствуют',
                            parse_mode='html')
        return

    try:
        warn_count_dell = int(message.text.split()[2])
    except ValueError:
        warn_count_dell = warns_count
    except IndexError:
        warn_count_dell = warns_count

    moder_link = GetUserByID(moder_id, message.chat.id).mention

    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя снять предупреждение выданное более старшим модером')
        return

    if int(warn_count_dell) not in range(1, 4):
        await message.reply('Номер предупреждения должен быть целым числом в диапозоне от 1 до 3', parse_mode='html')
        return
    if warn_count_dell > warns_count:
        await message.reply(
            '❕Предупреждение с таким номером отсутвует!\n\n{mes_em}<i>Предупреждения пользователя можно узнать по команде</i>«<code>преды @</code><i>юзер</i>»',
            parse_mode='html')
        return
    
    warn_count_new = warns_count - 1
    await snat_warn(user_id=user_id, number_warn=warn_count_dell, warn_count_new=warn_count_new, message=message)
    await message.reply(
        f'  <a href="tg://user?id={user_id}">{name_user}</a>, с тебя сняли одно предупреждение\n👮‍♂️Добрый модер: {moder_link}\n{mes_em}Количество твоих предупреждений: {warn_count_new} из 3\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»',
        parse_mode='html')


#? EN: Shows a paginated list of all removed warnings for a user, sent in private messages.
#* RU: Показывает постраничный список всех снятых предупреждений пользователя, отправляя его в личные сообщения.
@router.message(F.text.lower().startswith(('снятые преды', 'снятые варны')))
async def snatie_warns(message, bot: Bot):
    global page, mes_id, itog, page_c
    if len(message.text.split()[1]) != 5:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    
    can_chech_snat_pred = [8015726709, 1401086794, 1240656726]
    moder = message.from_user.id
    if moder in can_chech_snat_pred:
        pass
    else:
        await message.reply(f'{write_em}Тебе не доступна эта функция', parse_mode='HTML')
        return

    user_info = GetUserByMessage(message)
    if not user_info or not user_info.user_id:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = user_info.nik or "Пользователь"
    tg_id = user_info.user_id
    page = 0
    mes_id = 0
    itog = []
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM warn_snat WHERE user_id = ?", (tg_id,))
    all_snats = cursor.fetchall()
    
    if not all_snats:
        await message.reply(f'📝Снятые предупреждения <a href="tg://user?id={tg_id}">{name_user}</a> отсутствуют', parse_mode='html')
        return
    
    snats_count = len(all_snats)
    ar = []
    
    for i, snat in enumerate(all_snats):
        warn_text = snat[1]
        moder_give = snat[2]
        moder_snat = snat[3]
        
        textt = f'🔻 {i + 1}. {warn_text}\n&#8195&#8194Выдал: {moder_give}\n&#8195&#8194Снял: {moder_snat}'
        ar.append(textt)
        if (i + 1) % 5 == 0 or i == snats_count - 1:
            itog.append(ar)
            ar = []
    
    page = 0
    page_c = len(itog)
    
    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="snat_back"),
        types.InlineKeyboardButton(text="▶️", callback_data="snat_next")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    
    txt = "\n\n".join(itog[page])
    await bot.send_message(
        message.from_user.id,
        f'{desk_em}<b>Снятые предупреждения {name_user} (страниц: {page_c}):</b>\n\n{txt}',
        parse_mode='html',
        reply_markup=keyboard
    )
    connection.close()


#? EN: Handles situation when user reaches warning limit
#* RU: Обрабатывает ситуацию когда пользователь достигает лимита предупреждений
async def limit_warns(message):
    buttons = [
        types.InlineKeyboardButton(text="Бан", callback_data="banFromPred"),
        types.InlineKeyboardButton(text="Снять пред", callback_data="snat_pred")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.reply(f'❗Достигнут лимит предупреждений\n\nЧто делать с пользователем?', reply_markup=keyboard)


#? EN: Handles callback for banning user when warning limit is reached
#* RU: Обрабатывает callback для бана пользователя при достижении лимита предупреждений
@router.callback_query(F.data == "banFromPred")
async def ban_from_pred(call: types.CallbackQuery, bot: Bot):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Find user with 3 warnings
    cursor.execute("SELECT user_id FROM warns GROUP BY user_id HAVING COUNT(*) = 3")
    result = cursor.fetchone()
    
    if not result:
        await bot.answer_callback_query(call.id, text='Пользователь с 3 предупреждениями не найден', show_alert=True)
        return
    
    user_id = result[0]
    
    # Get the last warning's moderator info
    cursor.execute("SELECT moder_id FROM warns WHERE user_id = ? ORDER BY date DESC LIMIT 1", (user_id,))
    moder_result = cursor.fetchone()
    
    if not moder_result:
        await bot.answer_callback_query(call.id, text='Не удалось найти информацию о модераторе', show_alert=True)
        return
    
    last_moder_id = moder_result[0]
    
    if int(call.from_user.id) != int(last_moder_id):
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)
        return
    
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    name_narush = GetUserByID(user_id, call.message.chat.id).nik
    user_men = f'<a href="tg://user?id={user_id}">{name_narush}</a>'
    moder_name = call.from_user.full_name
    moder_men = hlink(moder_name, f"tg://user?id={call.from_user.id}")
    message_id = (call.message.message_id) + 1

    comments = 'Достигнут лимита предупреждений'
    await ban_user(user_id, call.message.chat.id, user_men, moder_men, comments, message_id, call.message, bot)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    moder_mention = f'<a href="tg://user?id={call.from_user.id}">{html.escape(call.from_user.full_name or call.from_user.username or "Модератор")}</a>'
    await bot.send_message(call.message.chat.id,
        f'<b>❗️Внимание❗️</b>\n🔴Злостный нарушитель <a href="tg://user?id={user_id}">{name_narush}</a> Получил достиг лимита предупреждений, получает бан и покидает нас\n👮‍♂Решение принял: {moder_mention}',
        parse_mode='html')
    
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM warns WHERE user_id = ?', (user_id,))
    connection.commit()
    connection.close()

#? EN: Handles callback for removing warning when limit is reached
#* RU: Обрабатывает callback для снятия предупреждения при достижении лимита
@router.callback_query(F.data == "snat_pred")
async def snat_pred(call: types.CallbackQuery, bot: Bot):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Find user with 3 warnings
    cursor.execute("SELECT user_id FROM warns GROUP BY user_id HAVING COUNT(*) = 3")
    result = cursor.fetchone()
    
    if not result:
        await bot.answer_callback_query(call.id, text='Пользователь с 3 предупреждениями не найден', show_alert=True)
        return
    
    user_id = result[0]
    
    # Get the last warning's moderator info
    cursor.execute("SELECT moder_id FROM warns WHERE user_id = ? ORDER BY date DESC LIMIT 1", (user_id,))
    moder_result = cursor.fetchone()
    
    if not moder_result:
        await bot.answer_callback_query(call.id, text='Не удалось найти информацию о модераторе', show_alert=True)
        return
    
    last_moder_id = moder_result[0]
    
    if int(call.from_user.id) != int(last_moder_id):
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)
        return
    
    buttons = [
        types.InlineKeyboardButton(text="1", callback_data="1warn"),
        types.InlineKeyboardButton(text="2", callback_data="2warn"),
        types.InlineKeyboardButton(text="3", callback_data="3warn")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    await bot.send_message(call.message.chat.id, 'Номер предупреждения который нужно снять:', reply_markup=keyboard)

#? EN: Handles callback for removing first warning
#* RU: Обрабатывает callback для снятия первого предупреждения
@router.callback_query(F.data == "1warn")
async def warn_1(call: types.CallbackQuery, bot: Bot):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Find user with 3 warnings
    cursor.execute("SELECT user_id FROM warns GROUP BY user_id HAVING COUNT(*) = 3")
    result = cursor.fetchone()
    
    if not result:
        await bot.answer_callback_query(call.id, text='Пользователь с 3 предупреждениями не найден', show_alert=True)
        return
    
    user_id = result[0]
    
    # Get the last warning's moderator info
    cursor.execute("SELECT moder_id FROM warns WHERE user_id = ? ORDER BY date DESC LIMIT 1", (user_id,))
    moder_result = cursor.fetchone()
    
    if not moder_result:
        await bot.answer_callback_query(call.id, text='Не удалось найти информацию о модераторе', show_alert=True)
        return
    
    last_moder_id = moder_result[0]

    if int(call.from_user.id) == int(last_moder_id):
        connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            name_user = cursor.execute(f'SELECT nik FROM users WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
        except IndexError:
            name_user = 'Пользователь'
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await snat_warn(user_id=user_id, number_warn=1, warn_count_new=2, message=call.message)
        await bot.send_message(call.message.chat.id, f'✅<a href="tg://user?id={user_id}">{name_user}</a>, тебя помиловали, теперь количество твоих предупреждений: 2 из 3\n👮‍♂️Помиловал: {GetUserByID(call.from_user.id, call.message.chat.id).mention}\n💬Сняли тебе первое предупреждение\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»', parse_mode='html')
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)

#? EN: Handles callback for removing second warning
#* RU: Обрабатывает callback для снятия второго предупреждения
@router.callback_query(F.data == "2warn")
async def warn_2(call: types.CallbackQuery, bot: Bot):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Find user with 3 warnings
    cursor.execute("SELECT user_id FROM warns GROUP BY user_id HAVING COUNT(*) = 3")
    result = cursor.fetchone()
    
    if not result:
        await bot.answer_callback_query(call.id, text='Пользователь с 3 предупреждениями не найден', show_alert=True)
        return
    
    user_id = result[0]
    
    # Get the last warning's moderator info
    cursor.execute("SELECT moder_id FROM warns WHERE user_id = ? ORDER BY date DESC LIMIT 1", (user_id,))
    moder_result = cursor.fetchone()
    
    if not moder_result:
        await bot.answer_callback_query(call.id, text='Не удалось найти информацию о модераторе', show_alert=True)
        return
    
    last_moder_id = moder_result[0]

    if int(call.from_user.id) == int(last_moder_id):
        connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            name_user = cursor.execute(f'SELECT nik FROM users WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
        except IndexError:
            name_user = 'Пользователь'
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await snat_warn(user_id=user_id, number_warn=2, warn_count_new=2, message=call.message)
        await bot.send_message(call.message.chat.id,
                               f'✅<a href="tg://user?id={user_id}">{name_user}</a>, тебя помиловали, теперь количество твоих предупреждений: 2 из 3\n👮‍♂️Помиловал: {GetUserByID(call.from_user.id, call.message.chat.id).mention}\n💬Сняли тебе второе предупреждение\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»',
                               parse_mode='html')
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)

#? EN: Handles callback for removing third warning
#* RU: Обрабатывает callback для снятия третьего предупреждения
@router.callback_query(F.data == "3warn")
async def warn_3(call: types.CallbackQuery, bot: Bot):
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Find user with 3 warnings
    cursor.execute("SELECT user_id FROM warns GROUP BY user_id HAVING COUNT(*) = 3")
    result = cursor.fetchone()
    
    if not result:
        await bot.answer_callback_query(call.id, text='Пользователь с 3 предупреждениями не найден', show_alert=True)
        return
    
    user_id = result[0]
    
    # Get the last warning's moderator info
    cursor.execute("SELECT moder_id FROM warns WHERE user_id = ? ORDER BY date DESC LIMIT 1", (user_id,))
    moder_result = cursor.fetchone()
    
    if not moder_result:
        await bot.answer_callback_query(call.id, text='Не удалось найти информацию о модераторе', show_alert=True)
        return
    
    last_moder_id = moder_result[0]

    if int(call.from_user.id) == int(last_moder_id):
        connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            name_user = cursor.execute(f'SELECT nik FROM users WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
        except IndexError:
            name_user = 'Пользователь'
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await snat_warn(user_id=user_id, number_warn=3, warn_count_new=2, message=call.message)
        await bot.send_message(call.message.chat.id,
                               f'✅<a href="tg://user?id={user_id}">{name_user}</a>, тебя помиловали, теперь количество твоих предупреждений: 2 из 3\n👮‍♂️Помиловал: {GetUserByID(call.from_user.id, call.message.chat.id).mention}\n💬Сняли тебе третье предупреждение\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»',
                               parse_mode='html')
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)


#? EN: Handles the "back" button in the removed warnings pagination.
#* RU: Обрабатывает кнопку «◀️» в пагинации снятых предупреждений.
@router.callback_query(F.data == "snat_back")
async def snat_list_back(call: types.CallbackQuery, bot: Bot):
    global page, page_c, itog
    
    if page > 0:
        page -= 1
        buttons = [
            types.InlineKeyboardButton(text="◀️", callback_data="snat_back"),
            types.InlineKeyboardButton(text="▶️", callback_data="snat_next")
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
        txt = "\n\n".join(itog[page])
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=f'{desk_em}<b>Снятые предупреждения (страниц: {page_c}):</b>\n\n{txt}',
            parse_mode='html',
            reply_markup=keyboard
        )
    await bot.answer_callback_query(call.id)


#? EN: Handles the "next" button in the removed warnings pagination.
#* RU: Обрабатывает кнопку «▶️» в пагинации снятых предупреждений.
@router.callback_query(F.data == "snat_next")
async def snat_list_next(call: types.CallbackQuery, bot: Bot):
    global page, page_c, itog
    
    if page < page_c - 1:
        page += 1
        buttons = [
            types.InlineKeyboardButton(text="◀️", callback_data="snat_back"),
            types.InlineKeyboardButton(text="▶️", callback_data="snat_next")
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
        txt = "\n\n".join(itog[page])
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=f'{desk_em}<b>Снятые предупреждения (страниц: {page_c}):</b>\n\n{txt}',
            parse_mode='html',
            reply_markup=keyboard
        )
    await bot.answer_callback_query(call.id)


#? EN: Starts a background loop that automatically unmutes users when their mute time expires.
# #* RU: Запускает фоновый цикл, автоматически размутивший пользователей по истечении времени мута.
# @router.message(Command(commands='auto_unmute'))
# async def auto_unmute(message: types.Message, bot: Bot):
#     global is_auto_unmute
#     is_auto_unmute = True
#
#     while True:
#         try:
#             # Get all active chats
#             for chat_id in chats:
#                 try:
#                     connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
#                     cursor = connection.cursor()
#
#                     # Check if muts table exists, create it if not
#                     cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='muts' ''')
#                     if not cursor.fetchone():
#                         # Create muts table
#                         cursor.execute('''CREATE TABLE muts (
#                             user_id INTEGER,
#                             rang_moder INTEGER,
#                             moder_id INTEGER,
#                             moder_men TEXT,
#                             date TEXT,
#                             comments TEXT
#                         )''')
#                         connection.commit()
#                         continue  # Skip to next chat since this one has no muts yet
#
#                     dates = cursor.execute(f"SELECT date FROM muts").fetchall()
#                     dates_muts = []
#                     for date in dates:
#                         dates_muts.append(date[0])
#                     now_time = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
#                     await asyncio.sleep(1)
#                     connection.commit()
#                     if now_time in dates_muts:
#
#                         now_time = (datetime.now() - timedelta(seconds=1)).strftime('%H:%M:%S %d.%m.%Y')
#
#                         user_id = cursor.execute(f"SELECT user_id FROM muts WHERE date = ?",
#                                                  (now_time,)).fetchall()[0][0]
#
#                         chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=int(user_id))
#                         name_user = chat_member.user.first_name
#                         try:
#                             cursor.execute(f'DELETE FROM muts WHERE date = ?', (now_time,))
#                             connection.commit()
#                         except sqlite3.OperationalError:
#                             print('error')
#                             continue
#
#                         await bot.send_message(chat_id,
#                                                f'{unmut_em}<a href="tg://user?id={user_id}">{name_user}</a> твой срок молчания подошел к концу, можешь говорить, но будь аккуратнее впредь\n\n{voscl}Правила чата можно посмотреть по команде «<code>правила</code>»',
#                                                parse_mode='html')
#
#                     connection.close()
#                 except Exception as e:
#                     print(f"Error in auto_unmute for chat {chat_id}: {e}")
#                     try:
#                         connection.close()
#                     except:
#                         pass
#         except Exception as e:
#             print(f"Global error in auto_unmute: {e}")
#         await asyncio.sleep(1)
#

#? EN: Mentions all admins/overseers in the chat to gather them, optionally with an announcement text.
#* RU: Созывает всех админов/ответственных в чате, отмечая их и при необходимости добавляя объявление.
@router.message(F.text.lower().startswith(('созвать админов', 'созвать отв')))
async def admn_sbor(message, bot: Bot):
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id))
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT tg_id FROM users WHERE rang > 0')
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
        return

    users_count = 0
    mentions = []
    for user in users:
        users_count += 1
        mentions.append(f'<a href="tg://user?id={user[0]}">&#x200b</a>')

    name1 = GetUserByID(message.from_user.id, message.chat.id).mention

    comments = " ".join(message.text.split("\n")[1:])
    if comments == "":
        await message.reply(f'{soziv} {name1} объявляет созыв админов', parse_mode='html')
    else:
        await message.reply(f'{soziv} {name1} объявляет созыв админов\n\n{mes_em} Объявление:\n{comments}', parse_mode='html')
    a = ''
    for r in range(users_count):
        a += mentions[r]
        print(a)
        print(r)
        if (r + 1) % 5 == 0 or r == users_count - 1:
            await message.reply(f'<b>⬆️Созват{a}ь Админов ({(r // 6) + 1})</b>', parse_mode='html')
            a = ''


#? EN: Organizes a general gathering for all chat members, formatting and validating the announcement text.
#* RU: Организует общий сбор для всех участников чата, проверяя и красиво оформляя текст объявления.
@router.message(F.text.lower().startswith(('созыв', 'созвать', 'общий сбор')))
async def all_sbor(message):
    
    #
    try:
        if len(message.text.split()[1]) > 4:
            return
    except IndexError:
        pass
    if len(message.text) > 0:
        a = ' '.join(message.text.split()[2:])
        print('text1', a)
        comm = ' '.join(message.text.split('\n')[1:])
        comm = ' '.join(comm.split())
        if comm == '' and len(a) > 1:
            return
        elif comm == a:
            pass
        else:
            print('text', comm)

            print((' '.join(a.split(comm))).strip())
            return
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!', parse_mode='html')
        return
    moder_id = message.from_user.id
    moder_link = GetUserByID(moder_id, message.chat.id).mention
    if await is_successful_moder(moder_id, message.chat.id, 'all') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды', parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'all') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'all') == 'chat error':
        await message.reply(f'{write_em}Непредвиденная ошибка!\n{mes_em}<i>Для решения обратитесь к админу этого бота: @zzoobank</i>', parse_mode='html')
        return
    
    # Проверка кулдауна - используем общую базу данных для default_periods
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        period_str = cursor.execute('SELECT period FROM default_periods WHERE command = ? AND chat = ?', ('all', message.chat.id)).fetchall()[0][0]
        time_value, time_unit = period_str.split()
        time_value = int(time_value)
        if time_unit in ['ч', 'час', 'часа', 'часов']:
            cd_delta = timedelta(hours=time_value)
        elif time_unit in ['мин', 'минут', 'минута', 'минуты']:
            cd_delta = timedelta(minutes=time_value)
        elif time_unit in ['д', 'день', 'дня', 'дней', 'сутки']:
            cd_delta = timedelta(days=time_value)
        else:
            cd_delta = None
    except (IndexError, ValueError):
        cd_delta = None

    if cd_delta is not None:
        cursor.execute('CREATE TABLE IF NOT EXISTS all_sbor_cd (chat_id INTEGER PRIMARY KEY, last_date TEXT)')
        connection.commit()
        try:
            cursor.execute("SELECT last_date FROM all_sbor_cd WHERE chat_id = ?", (message.chat.id,))
            if message.from_user.id in [8015726709, 1401086794, 1240656726]:
                lst = datetime.now() - cd_delta - cd_delta
            else:
                lst = datetime.strptime(cursor.fetchall()[0][0], "%H:%M:%S %d.%m.%Y")
            now = datetime.now()
            delta = now - lst
            if delta > cd_delta:
                pass
            else:
                delta = cd_delta - delta
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
                await message.answer(f'{krest} Можно использовать общий сбор только раз в {period_str}. Следующий сбор через {lst_date}', parse_mode=ParseMode.HTML)
                return
        except IndexError:
            pass

    # Используем базу данных конкретного чата для получения пользователей
    
    connection = sqlite3.connect(get_db_path(message.chat.id))
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT tg_id FROM users')
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
        return

    users_count = 0
    mentions = []
    for user in users:
        users_count += 1
        mentions.append(f'<a href="tg://user?id={user[0]}">&#x200b</a>')

    name1 = GetUserByID(message.from_user.id, message.chat.id).mention

    comments = "\n".join(message.text.split("\n")[1:])
    if comments == "":
        await message.reply(f'{soziv} {name1} объявляет общий сбор', parse_mode='html')
    else:
        await message.reply(f'{soziv} {name1} объявляет общий сбор\n\n{mes_em} Объявление:\n{comments}', parse_mode='html')
    
    # Обновляем время последнего использования - используем общую базу для кулдауна
    if cd_delta is not None:
        connection_main = sqlite3.connect(main_path, check_same_thread=False)
        cursor_main = connection_main.cursor()
        try:
            cursor_main.execute('INSERT INTO all_sbor_cd (chat_id, last_date) VALUES (?, ?)', (message.chat.id, datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
        except sqlite3.IntegrityError:
            cursor_main.execute('UPDATE all_sbor_cd SET last_date = ? WHERE chat_id = ?', (datetime.now().strftime("%H:%M:%S %d.%m.%Y"), message.chat.id))
        connection_main.commit()
        connection_main.close()
    
    a = ''
    for r in range(users_count):
        a += mentions[r]
        print(a)
        print(r)
        if (r + 1) % 5 == 0 or r == users_count - 1:
            await message.reply(f'<b>⬆️Общи{a}й сбор ({(r // 6) + 1})</b>', parse_mode='html')
            a = ''



#? EN: Promotes a user to a higher moderator rank in the chat if the caller has enough rights.
#* RU: Повышает пользователя до более высокого ранга модератора в чате, если вызывающий имеет достаточно прав.
@router.message(F.text.lower().startswith(("повысить",'завысить'))) # * повысить пользователя
async def rang_up(message: types.Message, bot: Bot):
    if len(message.text.split()[0]) != 8:
        return
    

    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    moder_id = message.from_user.id
    moder_link = GetUserByID(moder_id, message.chat.id).mention
    if await is_successful_moder(moder_id, message.chat.id, 'rang') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'rang') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id, message.chat.id).nik

    try:
        rang_moder = \
        cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    # * Повышаем
    try:
        first_rang_user = \
        cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply("Не могу повысить самого себя", parse_mode='html')
        return
    try:
        rang_delta = int(message.text.split()[1])

        new_rang_user = rang_delta
    except ValueError:
        rang_delta = 1
        new_rang_user = first_rang_user + rang_delta
    except IndexError:
        rang_delta = 1
        new_rang_user = first_rang_user + rang_delta

    if new_rang_user > rang_moder:
        await message.reply("Нельзя повысить на более старший ранг чем ты", parse_mode='html')
        return
    if new_rang_user < first_rang_user:
        await message.reply("Пользователь уже на этой должности или выше", parse_mode='html')
        return
    cursor.execute(f'UPDATE users SET rang = ? WHERE tg_id = ?',
                   (new_rang_user, user_id))
    connection.commit()
    new = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    await message.reply(
        f' {gal} Ранг <a href="tg://user?id={user_id}">{name_user}</a> назначен(а): {rangs_name[new]}[{new}]',
        parse_mode="html")
    connection.commit()
    connection.close()


#? EN: Demotes a user's moderator rank in the chat to a lower level, with safety checks on allowed range.
#* RU: Понижает ранг модератора пользователя в чате до более низкого уровня, с проверками допустимого диапазона.
@router.message(F.text.lower().startswith(("понизить", "занизить"))) # * понизить пользователя
async def rang_down(message: types.Message, bot: Bot):
    if len(message.text.split()[0]) != 8:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    moder_id = message.from_user.id
    moder_link = GetUserByID(moder_id, message.chat.id).mention
    if await is_successful_moder(moder_id, message.chat.id, 'rang') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'rang') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id, message.chat.id).nik

    try:
        rang_moder = \
        cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return

    try:
        first_rang_user = \
        cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply("Не могу понизить самого себя")
        return
    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    try:
        rang_delta = int(message.text.split()[1])

        new_rang_user = rang_delta
    except ValueError:
        rang_delta = 1
        new_rang_user = first_rang_user - rang_delta
    except IndexError:
        rang_delta = 1
        new_rang_user = first_rang_user - rang_delta
    if new_rang_user > 6 or new_rang_user < 0:
        await message.reply("Такого ранга не существует")
        return
    if new_rang_user > rang_moder:
        await message.reply("Пользователь уже на этой должности или выше")
        return
    if new_rang_user > first_rang_user:
        await message.reply("Пользователь уже на этой должности или выше")
        return
    cursor.execute(f'UPDATE users SET rang = ? WHERE tg_id = ?',
                   (new_rang_user, user_id))
    connection.commit()
    new = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    await message.reply(
        f' {gal} Модератору <a href="tg://user?id={user_id}">{name_user}</a> понижен ранг до {rangs_name[new]}[{new}]',
        parse_mode="html")
    connection.commit()
    connection.close()


#? EN: Completely strips a user of moderator rights in the chat (sets their rank to 0).
#* RU: Полностью снимает с пользователя права модератора в чате (устанавливает ранг 0).
@router.message(F.text.lower().startswith(("снять", "разжаловать"))) # * снять пользователя с поста модератора
async def rang_snat(message: types.Message, bot: Bot):
    if len(message.text.split()[0]) > 11:
        return
    

    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    moder_id = message.from_user.id
    moder_link = GetUserByID(moder_id, message.chat.id).mention
    if await is_successful_moder(moder_id, message.chat.id, 'rang') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'rang') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id, message.chat.id).nik

    try:
        rang_moder = \
        cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    try:
        first_rang_user = \
        cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply("Не могу понизить самого себя")
        return
    if first_rang_user >= rang_moder:
        await message.reply("Нельзя понизить старшего или равного по званию")
        return
    cursor.execute(f'UPDATE users SET rang = ? WHERE tg_id = ?',
                   (0, user_id))

    connection.commit()
    new = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    await message.reply(
        f'❎ Модератор <a href="tg://user?id={user_id}">{name_user}</a> разжалован(а)',
        parse_mode="html")
    connection.commit()
    connection.close()


#? EN: Shows a detailed profile/description of the user (PUBG ID, rank, etc.) and gives a copy button for PUBG ID.
#* RU: Показывает подробное описание пользователя (PUBG ID, ранг и т.д.) и даёт кнопку для копирования PUBG ID.
@router.message(F.text.lower().startswith(('описание')))
async def about_user(message):
    if len(message.text.split()[0]) != 8:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    user_id = await get_user_id_self(message)
    name_user = GetUserByID(user_id, message.chat.id).nik

    try:
        tg_id = user_id
        print(tg_id)

        cursor.execute(f"SELECT * FROM users WHERE tg_id=?", (tg_id,))
        users = cursor.fetchall()
        print(users)
        for user in users:
            user_about = {
                'tg_id': user[0],
                'usename': user[1],
                'name': user[2],
                'age': user[3],
                'nik_pubg': user[4],
                'id_pubg': user[5],
                'nik': user[6],
                'rang': user[7]
            }

        # * Выводим в нормальном формате описание

        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель',
                      'Менеджер',
                      'Владелец')
        print(rangs_name[4])
        sm = "🎄"
        stars = ""
        for i in range(int(user_about['rang'])):
            stars += sm
        text = await about_user_sdk(user_id, message.chat.id)
        itog_text = f'{write_em} Описание пользователя:\n\n{text}'
        cursor.execute(f"SELECT id_pubg FROM users WHERE tg_id=?", (user_id,))
        id_pubg = cursor.fetchall()[0][0]

        # * Создаём текст для копирования
        id_copy = types.CopyTextButton(text=str(id_pubg))

        id_btn = types.InlineKeyboardButton(text="📋Скопировать айди",
                                            copy_text=id_copy)  # * Внедряем текст для копирования в инлайн-кнопки

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[id_btn]])
        await message.reply(text=text, reply_markup=keyboard, parse_mode="html")

    except UnboundLocalError:
        await message.reply(f'Описание <a href="tg://user?id={user_id}">Пользователя</a> не заполнено',
                            parse_mode="html")
    finally:
        connection.close()


#? EN: Closes the chat for regular users (read-only) and shows a button to reopen it.
#* RU: Закрывает чат для обычных пользователей (только чтение) и выводит кнопку для повторного открытия.
@router.message(F.text.lower().startswith(('-чат')))
async def close_chat(message, bot: Bot):
    if len(message.text.split()[0]) != 4:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'close_chat') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'close_chat') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    await bot.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=False))
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Открыть чат", callback_data="open_chat")]
    ])
    await message.reply(
        f'🤐 <b>Чат закрыт для общения</b>\nТеперь писать в чат могут только администраторы\n\n{mes_em}<i> Чат можно открыть по команде «</i><code>+чат</code><i>»</i> или нажав на кнопку снизу',
        reply_markup=keyboard, parse_mode="HTML")


#? EN: Deletes a replied message and the command message, used by moderators to clean up single messages.
#* RU: Удаляет отвеченное сообщение и команду, используется модераторами для точечной очистки сообщений.
@router.message(F.text.lower().startswith(('-смс')))
async def minus_sms(message, bot: Bot):
    if len(message.text.split()[0]) != 4:
        return
    
    if not message.reply_to_message:
        return
    
    
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return

    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'dell') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'dell') == 'Need reg':
        await message.reply(f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    try:
        await bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        await bot.delete_message(message.chat.id, message.message_id)
    except TelegramBadRequest:
        await message.answer('Не могу удалить сообщение т.к у меня нет таких прав')


#? EN: Reopens the chat for all members, restoring full send permissions.
#* RU: Открывает чат для всех участников, возвращая полные права на отправку сообщений.
@router.message(F.text.lower().startswith(('+чат')))
async def open_chat(message, bot: Bot):
    moder_id = message.from_user.id
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    if await is_successful_moder(moder_id, message.chat.id, 'close_chat') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'close_chat') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    try:
        await bot.set_chat_permissions(message.chat.id,
                                    ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                                    can_send_photos=True, can_send_videos=True,
                                                    can_send_audios=True, can_send_documents=True,
                                                    can_send_other_messages=True,
                                                    can_send_video_notes=True, can_send_voice_notes=True,
                                                    can_pin_messages=True,
                                                    can_add_web_page_previews=True, can_send_polls=True))
    except TelegramBadRequest:
        return
    await message.reply(f' {gal} Чат открыт для общения\n<i>Теперь у всех есть разрешение на отправку сообщений</i>',
                        parse_mode="HTML")


#? EN: Handles the inline "open chat" button and reopens the chat if the user has enough rights.
#* RU: Обрабатывает инлайн‑кнопку «Открыть чат» и открывает чат, если у пользователя достаточно прав.
@router.callback_query(F.data == 'open_chat')  # * * обработчик открытия чата
async def open_chat_button(call, bot: Bot):
    moder_id = call.from_user.id
    if await is_successful_moder(moder_id, call.message.chat.id, 'close_chat') == False:
        await call.answer(f'{write_em}Ранг модератора не достаточен для использования этой команды', show_alert=True)
        return
    elif await is_successful_moder(moder_id, call.message.chat.id, 'close_chat') == 'Need reg':
        await call.answer(f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>', show_alert=True)
        return
    try:
        await bot.set_chat_permissions(call.message.chat.id,
                                    ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                                    can_send_photos=True, can_send_videos=True,
                                                    can_send_audios=True, can_send_documents=True,
                                                    can_send_other_messages=True,
                                                    can_send_video_notes=True, can_send_voice_notes=True,
                                                    can_pin_messages=True,
                                                    can_add_web_page_previews=True, can_send_polls=True))
    except TelegramBadRequest:
        await call.answer('Не могу открыть чат', show_alert=True)
        return
    await call.message.edit_text(f'{gal} Чат открыт для общения\n<i>Теперь у всех есть разрешение на отправку сообщений</i>',
                                 parse_mode="HTML")
    await call.answer(text='Чат открыт', show_alert=False)


#? EN: Shows current chat rules stored for this chat.
#* RU: Показывает текущие правила чата, сохранённые для этого чата.
@router.message(F.text.lower().startswith(('правила')))
async def pravila(message, bot: Bot):
    if len(message.text) != 7:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    try:
        rules =cursor.execute(f'SELECT text FROM texts WHERE text_name=?', ('rules',)).fetchall()[0][0]
        text = f"{desk_em}<b>Правила чата</b>\n\n{rules if rules and rules!=None and rules!='None' else 'Правила не установлены'}"
        await message.reply(text, parse_mode='HTML')
        return text
    except IndexError:
        await message.reply(f"{desk_em}<b>Правила чата</b>\n\nПравила не установлены", parse_mode='HTML')
    finally:
        connection.close()


#? EN: Sets or updates the full text of chat rules (everything after the first line is stored).
#* RU: Устанавливает или обновляет полный текст правил чата (всё после первой строки команды записывается).
@router.message(F.text.lower().startswith(('+правила')))
async def plus_pravila(message, bot: Bot):

    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return

    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'change_pravils') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'change_pravils') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='HTML')
        return

    # Initialize database for this chat if it doesn't exist
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        comments = ' '.join(message.text.split()[1:])
        if comments == '':
            await message.reply(f'{write_em} Правила не заданы')
            return
        
        cursor.execute(f'SELECT text FROM texts WHERE text_name=?', ('rules',))
        if cursor.fetchall() == []:
            cursor.execute(f'INSERT INTO texts (text_name, text) VALUES (?, ?)', ('rules', comments))
        else:
            cursor.execute(f'UPDATE texts SET text = ? WHERE text_name = ?', (comments, 'rules'))
        connection.commit()
        await message.answer('   Правила чата обновлены', parse_mode='html')
    finally:
        connection.close()


#? EN: Changes the global "entry rules" text that is used when new users join (only for main admins via PM).
#* RU: Изменяет общий текст «правил входа», который показывается новым пользователям (только для главных админов в ЛС).
@router.message(F.text.lower().startswith('!изменить правила входа'))
async def set_new_pravil_vhod(message, bot: Bot):
    if message.chat.id != message.from_user.id:
        return
    if message.from_user.id in [8015726709, 1401086794, 1240656726]:
        pass
    else:
        await message.answer('не, не, не')
        return

    comments = ' '.join(message.text.split()[3:])
    if comments == '':
        await message.reply(f'{write_em}Правила не заданы')
        return
    
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'UPDATE texts SET text = ? WHERE text_name = ?', (comments, 'pravils'))
    connection.commit()
    connection.close()
    await message.answer('   Правила для новых пользователей обновлено', parse_mode='html')


#? EN: Shows the current global "entry rules" text for new users (admin PM command).
#* RU: Показывает текущий глобальный текст «правил входа» для новых пользователей (админская команда в ЛС).
@router.message(F.text.lower().startswith('!правила входа'))
async def show_pravil_vhod(message, bot: Bot):
    if message.chat.id != message.from_user.id:
        return
    if message.from_user.id in [8015726709, 1401086794, 1240656726]:
        pass
    else:
        return

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('pravils',)).fetchall()[0][0]
    connection.close()
    await message.answer(text, parse_mode='html')


#? EN: Changes the minimum moderator rank required to use a specific command (mute, ban, etc.) in this chat.
#* RU: Изменяет минимальный ранг модератора, с которого доступна конкретная команда (мут, бан и т.п.) в этом чате.
@router.message(F.text.lower().startswith(('дк')))
async def dk(message, bot: Bot):
    if len(message.text.split()[0]) != 2:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    # Initialize database for this chat if it doesn't exist
    
    
    # Get current user's rank from per-chat database
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        rang_moder = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (message.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await message.reply("Вы не зарегистрированы в этом чате")
        connection.close()
        return
    
    # Get required rank for dk command from main database


    rang_up_dk = int(cursor.execute("SELECT dk FROM dk WHERE comand=?", ("dk",)).fetchall()[0][0])
   
    

    
    if rang_moder < rang_up_dk:
        await message.reply("Ранг модератора не достаточен для использования этой команды")
        connection.close()
        return

    try:
        command = message.text.split(' ')[1]
        rang_dk = int(message.text.split(' ')[2])
    except IndexError:
        await message.reply(f'Неверное использование команды дк\nПример: дк мут 3')
        connection.close()
        return
    except ValueError:
        try:
            command = message.text.split(' ')[1] + ' ' + message.text.split(' ')[2]
            rang_dk = int(message.text.split(' ')[3])
        except IndexError:
            await message.reply(f'Неверное использование команды дк\nПример: дк мут 3')
            connection.close()
            return
        except ValueError:
            await message.reply(f'Неверное использование команды дк\nПример: дк мут 3')
            connection.close()
            return

    # Command mapping
    if command == 'мут' or command == 'анмут' or command == 'размут':
        command_en = 'mut'
    elif command == 'бан' or command == 'разбан' or command == 'анбан':
        command_en = 'ban'
    elif command == 'пред' or command == 'варн' or command == 'снять пред' or command == 'снять варн':
        command_en = 'warn'
    elif command == 'общий сбор' or command == 'созвать' or command == 'созыв':
        command_en = 'all'
    elif command == 'повысить' or command == 'понизить' or command == "снять":
        command_en = 'rang'
    elif command == 'дк':
        command_en = 'dk'
    elif command == 'изменение правил' or command == '+правила':
        command_en = 'change_pravils'
    elif command == '-чат' or command == 'закрыть чат':
        command_en = 'close_chat'
    elif command == 'изменение приветствия' or command == '+приветствие':
        command_en = 'change_priv'
    elif command == 'создание объявления' or command == '+объявление':
        command_en = 'obavlenie'
    elif command == 'турниры' or command == 'турнир':
        command_en = 'tur'
    elif command == '-смс' or command == 'удаление сообщения':
        command_en = 'dell'
    elif command == 'период':
        command_en = 'period'
    else:
        await message.reply('Настройки для этой команды нет', parse_mode='html')
        connection.close()
        return
    
    num = ['0', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер', 'Владелец')
    
    if rang_dk > 6 or rang_dk < 0:
        await message.reply(f'{write_em}Такого ранга не существует')
        connection.close()
        return
    
    # Update command rank requirements in main database

    

    cursor.execute(f"UPDATE dk SET dk = ? WHERE comand = ?", (rang_dk, command_en,))

    connection.commit()
    connection.close()
    connection.close()
    
    if rang_dk > 0 and rang_dk <= 6:
        await message.reply(
            f"{num[rang_dk]} Команда «{command}» теперь доступна с ранга модератора {rangs_name[rang_dk]} ({rang_dk})")
    if rang_dk == 0:
        await message.reply(f'  Команда «{command}» теперь доступна всем')
    connection.close()


#? EN: Welcomes a new chat member, updates their usernames in clan tables and sends greeting + rules.
#* RU: Приветствует нового участника, обновляет его username в клановых таблицах и отправляет приветствие и правила.
@router.message(F.new_chat_members)  # * приветсвие нового участника
async def new_chat_mem(message, bot: Bot):
    new = message.new_chat_members[0]
    username = new.username
    user_id = new.id
    user = new.mention_html()
    print(user_id, username)
    
    
    # Update username in main database clan tables
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    try:
        cursor.execute(f'UPDATE users username = ? WHERE tg_id = ?', (username, user_id))
        connection.commit()
    except sqlite3.OperationalError:
        pass

    
    # Initialize database for this chat if it doesn't exist
    
    
    # Get greeting text from per-chat database
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    try:
        text = cursor.execute(f'SELECT text FROM texts WHERE text_name=?', ('priv',)).fetchall()[0][0]
        await bot.send_message(message.chat.id, f'{desk_em} Приветствие: {user}\n{text}', parse_mode='html')
    except IndexError:
        # If no greeting is set, send default message
        await bot.send_message(message.chat.id, f'{desk_em} Приветствие: {user}\nДобро пожаловать в чат!', parse_mode='html')
    finally:
        connection.close()
    
    # Send chat rules using the refactored pravila_sdk function
    text = await pravila_sdk(message)
    await bot.send_message(message.chat.id, text, parse_mode='HTML')


#? EN: Sets or updates the greeting text that is shown when new members join the chat.
#* RU: Устанавливает или обновляет текст приветствия, который показывается новым участникам чата.
@router.message(F.text.lower().startswith('+приветствие'))
async def add_privetstvie(message, bot: Bot):
    moder_id = message.from_user.id
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    if await is_successful_moder(moder_id, message.chat.id, 'change_priv') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'change_priv') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    try:
        comments = '\n'.join(message.text.split("\n")[1:])
        if comments == '':
            await message.reply(f'{write_em} Приветствие не задано')
            return
        
        cursor.execute(f'SELECT text FROM texts WHERE text_name=?', ('priv',))
        if cursor.fetchall() == []:
            cursor.execute(f'INSERT INTO texts (text_name, text) VALUES (?, ?)', ('priv', comments))
        else:
            cursor.execute(f'UPDATE texts SET text = ? WHERE text_name = ?', (comments, 'priv'))
        connection.commit()
        await message.answer('   Приветствие новых пользователей обновлено', parse_mode='html')
    finally:
        connection.close()


#? EN: Shows the current greeting text for new members in this chat.
#* RU: Показывает текущий текст приветствия для новых участников этого чата.
@router.message(F.text.lower().startswith('приветствие'))  # * просмотр приветсвия
async def privetstvie(message, bot: Bot):
    if len(message.text) != 11:
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    try:
        greeting = cursor.execute(f'SELECT text FROM texts WHERE text_name=?', ('priv',)).fetchall()[0][0]
        text = f"{desk_em}<b>Приветствие новых пользователей</b>\n\n{greeting if greeting and greeting!=None and greeting!='None' else 'Добро пожаловать!'}"
        await message.reply(text, parse_mode='HTML')
    except IndexError:
        await message.reply(
            f"{desk_em}<b>Приветствие новых пользователей</b>\n\nДобро пожаловать!",
            parse_mode='HTML')
    finally:
        connection.close()


#? EN: Shows all stored recommendations for the specified user (by @ or PUBG ID).
#* RU: Показывает все сохранённые рекомендации для указанного пользователя (по @ или PUBG ID).
@router.message(F.text.lower().startswith('рекомендации'))
async def recom_check(message, bot: Bot):

    if len(message.text.split()[0]) != 12:
        return

    
    
    # Initialize database for this chat if it doesn't exist
    init_chat_db(message.chat.id)
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        connection.close()
        return

    name_user = GetUserByID(user_id, message.chat.id).nik
    tg_id=user_id
    text = await recom_check_sdk(tg_id, name_user, message.chat.id)
    if text == '':
        await message.reply(f'{write_em} Рекомендации <a href="tg://user?id={tg_id}">{name_user}</a> отсутвуют',
                            parse_mode='html')
    else:
        await message.reply(f'{text}', parse_mode='html')
    
    connection.close()


#? EN: Handles the "successful_recom1" callback and saves a prepared recommendation from temp storage to main table.
#* RU: Обрабатывает колбэк «successful_recom1» и сохраняет подготовленную рекомендацию из временного хранилища в основную таблицу.
@router.callback_query(F.data == "successful_recom1")
async def successful_recom1(call: types.CallbackQuery, bot: Bot):
    if call.from_user.id not in can_recommend_users:
        await bot.answer_callback_query(call.id, text=f'{znak_yelow} Тебе не доступна эта функция')
        return
    
    connection = sqlite3.connect(get_db_path(call.message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    all = cursor.execute('SELECT * FROM din_admn_user_data WHERE moder = ?', (call.from_user.id,)).fetchall()[0]

    user_id = all[0]
    pubg_id = all[1]
    moder = all[2]
    comments = all[3]
    recom = all[4]
    date = all[5]
    id_recom = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    cursor.execute(
        'INSERT INTO recommendation (user_id, pubg_id, moder, comments, rang, date, recom_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, pubg_id, moder, comments, recom, date, id_recom))
    await call.message.edit_text('  Рекомендация заполнена')
    connection.commit()
    cursor.execute('DELETE FROM din_admn_user_data WHERE moder = ?', (moder,))
    connection.commit()
    connection.close()


#? EN: Handles the "not_successful_user1" callback and simply cancels recommendation creation.
#* RU: Обрабатывает колбэк «not_successful_user1» и просто отменяет создание рекомендации.
@router.callback_query(F.data == "not_successful_user1")
async def not_successful_user1(call: types.CallbackQuery, bot: Bot):
    if call.from_user.id not in can_recommend_users:
        await bot.answer_callback_query(call.id, text=f'{znak_yelow} Тебе не доступна эта функция')
        return
    await call.message.edit_text(f'{krest} Отменено')



#? EN: Creates a new recommendation for a clan member with reason and target rank, only for allowed moderators.
#* RU: Создаёт новую рекомендацию для участника клана с указанием причины и ранга, доступно только выбранным модераторам.
@router.message(F.text.lower().startswith(('+рекомендация', 'рекомендовать')))
async def add_recom(message, bot: Bot):
    moder = message.from_user.id
    if moder in can_recommend_users:
        pass
    else:
        await message.reply(f'{write_em}Тебе не доступна эта функция')
        return
    
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    text = message.text
    try:
        us = text.split()[1]
  
    except IndexError:
        await message.reply(
            f'{write_em}Неверное использование команды \n\n{mes_em}Правильное использование этой команды:\n\n<code>+рекомендация [юзер или пабг айди]\nПричина: \nРекомендую на: </code>',
            parse_mode='HTML')
        return
    try:
        pubg_id = int(us)
        user_id = cursor.execute(f"SELECT tg_id FROM users WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        _ = cursor.execute(f"SELECT nik FROM users WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        _ = cursor.execute(f"SELECT nik_pubg FROM users WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        username = cursor.execute(f"SELECT username FROM users WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
    except ValueError:
        try:
            username = us.split('@')[1]


            user_id = cursor.execute(f"SELECT tg_id FROM users WHERE username=?", (username,)).fetchall()[0][0]
            _ = cursor.execute(f"SELECT nik FROM users WHERE username=?", (username,)).fetchall()[0][0]
            _ = cursor.execute(f"SELECT nik_pubg FROM users WHERE username=?", (username,)).fetchall()[0][
                0]
            pubg_id = cursor.execute(f"SELECT id_pubg FROM users WHERE username=?", (username,)).fetchall()[0][0]
        except IndexError:
            await message.reply(
                f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>) или напиши игровой айди пользователя',
                parse_mode='html')
            return
    if user_id == message.from_user.id:
        await message.reply(f'{write_em}Жулик, не рекомендуй!\n\n{mes_em}<i>Нельзя рекомендовать самого себя</i>', parse_mode='html')
        return
    moder_men = message.from_user.id
    users_idss = cursor.execute(f"SELECT user_id FROM recommendation WHERE moder=?", (moder_men,)).fetchall()
  
    for user_ids in users_idss:
        

        if user_ids[0] == user_id:
            await message.reply(
                f'{write_em}Жулик, не рекомендуй!\n\n{mes_em}<i>Нельзя рекомендовать одного человека больше одного раза</i>',
                parse_mode='html')
            return
    try:
        comments = (text.split('Причина:')[1:])[0].split('\n')[0]

    except IndexError:
        try:
            comments = (text.split('причина:')[1:])[0].split('\n')[0]
        except IndexError:
            await message.reply(
                f'{write_em}Неверное использование команды \n\n{mes_em}Правильное использование этой команды:\n\n<code>+рекомендация [юзер или пабг айди]\nПричина: \nРекомендую на: </code>',
                parse_mode='HTML')
            return
    try:
        recom = text.split('Рекомендую на:')[1:][0]
    except IndexError:
        try:
            recom = text.split('Рекомендую на:')[1:][0]
        except IndexError:
            await message.reply(
                f'{write_em}Неверное использование команды \n\n{mes_em}Правильное использование этой команды:\n\n<code>+рекомендация [юзер или пабг айди]\nПричина: \nРекомендую на: </code>',
                parse_mode='HTML')
            return
    import random
    import string
    _ = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    moder = message.from_user.id
    date = datetime.now().strftime('%d.%m.%Y')
    buttons = [
        types.InlineKeyboardButton(text="Верно", callback_data="successful_recom1"),
        types.InlineKeyboardButton(text="Не правильно", callback_data="not_successful_user1"),

    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    connection.commit()
    cursor.execute(
        'INSERT INTO din_admn_user_data (user_id, pubg_id, moder, comments, rang, date) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, pubg_id, moder, comments, recom, date))
    connection.commit()
    await message.answer(
        f'Рекомендация <a href="tg://user?id={user_id}">Пользователя</a>:\n\n🟢 <b>1</b>. От <a href="tg://user?id={moder}">{message.from_user.first_name}</a>:\n<b>&#8195Чем отличился:</b> {comments}\n<b>&#8195Рекомендован на:</b> {recom}',
        parse_mode='html', reply_markup=keyboard)


#? EN: Deletes an existing recommendation for a user, optionally specifying which moderator it was from.
#* RU: Удаляет существующую рекомендацию пользователя, при необходимости указывая, от какого модератора.
@router.message(F.text.lower().startswith('-рекомендация'))
async def dell_recom(message, bot: Bot):
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        us = message.text.split()[1]
        print(us)
    except IndexError:
        await message.reply(
            f'{write_em}Неверное использование команды \n\n{mes_em}Правильное использование этой команды:\n\n«<code>-рекомендация [юзер или пабг айди] от [юзер или пабг айди]</code>»',
            parse_mode='HTML')
        return
    moder = message.from_user.id
    if moder in can_snat_recommend_users:
        pass
    else:
        await message.reply(f'{write_em}Тебе не доступна эта функция\n\n{mes_em}<i>Снять свою рекомендацию можно в админ боте</i>',
                            parse_mode='HTML')
        return

    try:
        pubg_id = int(us)
        user_id = cursor.execute(f"SELECT tg_id FROM users WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
    except ValueError:
        try:
            username = us.split('@')[1]
            user_id = cursor.execute(f"SELECT tg_id FROM users WHERE username=?", (username,)).fetchall()[0][0]
        except IndexError:
            await message.reply(
                f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>) или напиши игровой айди пользователя',
                parse_mode='html')
            return

    try:
        moder_t = message.text.split('от ')[1].split()[0]
        try:
            pubg_id = int(moder_t)
            moder_id = cursor.execute(f"SELECT tg_id FROM users WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        except ValueError:
            try:
                username = moder_t.split('@')[1]
                moder_id = cursor.execute(f"SELECT tg_id FROM users WHERE username=?", (username,)).fetchall()[0][
                    0]
            except IndexError:
                await message.reply(
                    f'{write_em}Невозможно найти информацию о модераторе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>) или напиши игровой айди модератора',
                    parse_mode='html')
                return
    except IndexError:
        moder_id = message.from_user.id

    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    alll = cursor.execute('SELECT moder FROM recommendation WHERE user_id = ?', (user_id,)).fetchall()
    if alll == []:
        await bot.send_message(message.chat.id, f'{write_em}Рекомендации пользователя отсутвуют')
        return
    mod_count = 0
    idss = []
    for _ in alll:
        mod_count += 1
    is_this_moder = False
    for t in range(mod_count):
        num = t
        b = (alll[num][0])
        idss.append(b)
    for y in range(mod_count):
        print(idss[y], moder_id)

        if int(idss[y]) == moder_id:
            is_this_moder = True

    if is_this_moder == False:
        await bot.send_message(message.chat.id, f'{write_em}Этот пользователь не рекомендовал этого пользователя')
        return
    recom_id = cursor.execute('SELECT recom_id FROM recommendation WHERE user_id = ? AND moder = ?',
                              (user_id, moder_id,)).fetchall()[0][0]
    print(recom_id)
    cursor.execute('DELETE FROM recommendation WHERE recom_id = ?', (recom_id,))
    await bot.send_message(message.chat.id, '  Рекомендация удалена')
    connection.commit()


#? EN: Shows Telegram ID of a user (by @, reply, or yourself) in a copyable format.
#* RU: Показывает Telegram ID пользователя (по @, ответу или себе) в удобном для копирования виде.
@router.message(Command(commands=['ид'], prefix='/!. '))
async def id_user_check(message: types.Message, bot: Bot):
    
    username = GetUserByMessage(message).username
    user_id = await get_user_id_self(message)
    if user_id == False:                                
        await message.reply(f'{write_em}Невозможно найти информацию о пользователе\n\n{mes_em}Введите корректный юзернейм(<code>@</code><i>юзер</i>) или ответь на сообщение',parse_mode='html')
        return
    name_user = GetUserByID(user_id, message.chat.id).nik
    tg_id=user_id
    await message.answer(
        f'👤 Пользователь <a href="https://t.me/{username}">{name_user}</a>\n🆔 равен @<code>{tg_id}</code>',
        parse_mode='html', disable_web_page_preview=True)



#? EN: Sends formatted commands list to the user in PM when called from a chat.
#* RU: Отправляет оформленный список команд пользователю в ЛС при вызове из чата.
@router.message(F.text.lower().startswith(('!команды', '! команды')))
async def show_commands(message: types.Message, bot: Bot):
    
    commands = types.InlineKeyboardButton(text='⚒️ Команды', url='https://ivansalou288-tech.github.io/chat_manager_bot/html/USER_GUIDE.html')
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[commands]])
    await message.answer(f'{desk_em}Список команд ', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=keyboard)
         
@router.message(F.text.lower().startswith('+объявление'))
async def abavlenie(message, bot: Bot):
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    moder_name = message.from_user.full_name
    moder_link = hlink(moder_name, f"tg://user?id={moder_id}")
    if await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'chat error':
        await message.reply(f'{write_em}Непредвиденная ошибка!\n{mes_em}<i>Для решения обратитесь к админу этого бота: @zzoobank</i>')
        return

    comments = "\n".join(message.text.split("\n")[1:])

    message_id = (await bot.send_message(message.chat.id, f'{voscl}️<b>ОБЪЯВЛЕНИЕ</b> {voscl}️\n\n{comments}\n\n▫️Объявил {moder_link}', parse_mode='html')).message_id
    print(message_id)
    await bot.pin_chat_message(chat_id=message.chat.id, message_id=message_id)

@router.message(F.text.lower().startswith('+важное объявление'))
async def vagn_abavlenie(message, bot: Bot):
    if message.chat.id == message.from_user.id:
        await message.answer(
            f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    moder_name = message.from_user.full_name
    moder_link = hlink(moder_name, f"tg://user?id={moder_id}")
    if await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'Need reg':
        await message.reply(
            f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'chat error':
        await message.reply(f'{write_em}Непредвиденная ошибка!\n{mes_em}<i>Для решения обратитесь к админу этого бота: @zzoobank</i>')
        return

    comments = "\n".join(message.text.split("\n")[1:])

    message_id = (await bot.send_message(message.chat.id, f'{voscl}️<b>ВАЖНОЕ ОБЪЯВЛЕНИЕ</b> {voscl}️\n\n{comments}\n\n▫️Объявил {moder_link}', parse_mode='html')).message_id
    connection = sqlite3.connect(get_db_path(message.chat.id))
    cursor = connection.cursor()
    try:
        cursor.execute(f'SELECT tg_id FROM users')
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
        return

    users_count = 0
    mentions = []
    for user in users:
        users_count += 1
        mentions.append(f'<a href="tg://user?id={user[0]}">&#x200b</a>')

    a = ''
    for r in range(users_count):
        a += mentions[r]
 
        if (r + 1) % 5 == 0 or r == users_count - 1:
            await bot.send_message(chat_id=message.chat.id, text=f'<b>⬆️Общи{a}й сбор ({(r // 6) + 1})</b>', parse_mode='html', reply_to_message_id=message_id)
            a = ''

    await bot.pin_chat_message(chat_id=message.chat.id, message_id=message_id)


@router.message(F.text.lower().startswith('период'))
async def set_period(message):
    if message.chat.id == message.from_user.id:
        await message.answer(f'{write_em}Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'period') == False:
        await message.reply(f'{write_em}Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'period') == 'Need reg':
        await message.reply(f'{write_em}Для использования бота нужно зарегистрироваться\n\n{mes_em}<i>Для регистрации напиши @zzoobank, он все объяснит</i>', parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'period') == 'chat error':
        await message.reply(f'{write_em}Непредвиденная ошибка!\n{mes_em}<i>Для решения обратитесь к админу этого бота: @zzoobank</i>', parse_mode='html')
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.reply(f'{write_em}Неверный формат команды!\n\nИспользуйте: <code>период [команда/модуль] [число] [единица]</code>\nПример: <code>период мут 30 мин</code>', parse_mode='html')
            return
        
        command_ru = parts[1].lower()

        commands = {
            'мут': 'mut',
            'общий-сбор': 'all',
            'созыв': 'all',
            'созвать': 'all',
            'казик': 'kas ik',
            'рулетка': 'slot_roulette'
        }

        try:
            command = commands[command_ru]
        except KeyError:
            await message.reply(f'{write_em}Неверная команда!\n\nИспользуйте: <code>период [команда/модуль] [число] [единица]</code>\nПример: <code>период казик 30 мин</code>', parse_mode='html')
            return

        time_value = int(parts[2])
        time_unit = parts[3].lower() if len(parts) > 3 else 'мин'
        
        # Initialize database for this chat if it doesn't exist
        init_chat_db(message.chat.id)
        connection = sqlite3.connect(get_db_path(message.chat.id))
        cursor = connection.cursor()
        
        # The default_periods table is already created by init_chat_db() from test.sql schema
        period = f"{time_value} {time_unit}"
        cursor.execute('INSERT OR REPLACE INTO default_periods (command, period) VALUES (?, ?)', (command, period))
        connection.commit()
        connection.close()
        
        await message.reply(f'  Установлен дефолтный период для команды <b>{command}</b>: {period}', parse_mode='html')
    except ValueError:
        await message.reply(f'{write_em}Ошибка! Время должно быть числом.\nПример: <code>период казик 10 мин</code>', parse_mode='html')
    except Exception as e:
        await message.reply(f'{write_em} Произошла ошибка: {str(e)}')




async def shedul_posting(message, bot: Bot):
    global posting
    posting = True
    while True:
        now_time = datetime.now().strftime("%H:%M:%S")
        await asyncio.sleep(1)
        if now_time == "00:00:00":
            # For the states table, we might need to decide if this should be per-chat or remain centralized
            # For now, keeping it centralized as it might be a global state table

            
            global week_count
            if datetime.today().weekday() == 1:
                await bot.send_message(chat_id=-1003101400599, text=tuesday)
            if datetime.today().weekday() == 2:
                await bot.send_message(chat_id=-1003101400599, text=wednesday)
            if datetime.today().weekday() == 3:
                await bot.send_message(chat_id=-1003101400599, text=thursday)
            if datetime.today().weekday() == 4:
                await bot.send_message(chat_id=-1003101400599, text=friday)
            if datetime.today().weekday() == 5:
                await bot.send_message(chat_id=-1003101400599, text=saturday)
            if datetime.today().weekday() == 6:
                await bot.send_message(chat_id=-1003101400599, text=sunday)
            if datetime.today().weekday() == 0:
                await bot.send_message(chat_id=-1003101400599, text=monday)

#? EN: Command for chat owners to bind their chat to admin panel
#* RU: Команда для владельцев чатов для привязки чата к админ-панели
@router.message(F.text.lower().startswith('!привязать'))
async def bind_chat_to_admin(message: types.Message, bot: Bot):
    """Привязывает чат к админ-панели для владельца чата"""
    
    # Проверяем, что команда используется в групповом чате
    if message.chat.id == message.from_user.id:
        await message.answer(f' {krest} Эта команда работает только в групповых чатах!', parse_mode='html')
        return
    
    # Проверяем, что чат в списке разрешенных

    init_all_db()
    init_admin_db() 
    init_chat_db(message.chat.id)


    try:
        # Получаем информацию о пользователе в чате
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        
        # Проверяем, что пользователь является владельцем
        if chat_member.status != ChatMemberStatus.CREATOR:
            await message.answer(f' {krest} Только владелец чата может использовать эту команду!', parse_mode='html')
            return
        
        connection = sqlite3.connect(admin_path)
        cursor = connection.cursor()

        cursor.execute('SELECT can_links FROM admins WHERE user_id = ? AND chat_id = ?', (message.from_user.id, message.chat.id))
        result = cursor.fetchone()
        
        if result:
            await message.answer(f' {krest} Этот чат уже привязан к админ-панели!', parse_mode='html')
            return
        chat_title = message.chat.title
        cursor.execute('INSERT INTO admins (user_id,chat_id,chat_name,can_see_users,can_do_admin,can_recom,can_links,can_dk) VALUES (?, ?, ?, 1, 1, 1, 1, 1)', (message.from_user.id, message.chat.id, chat_title))

        connection.commit()
        connection = sqlite3.connect(admin_path)
        cursor = connection.cursor()
        cursor.execute('INSERT OR IGNORE INTO creators (user_id, chat_id) VALUES (?, ?)', (message.from_user.id, message.chat.id))
        connection.commit()
        
       

        await message.answer(
            f'✅ Чат "{chat_title}" успешно привязан к админ-панели!\n'
            f'👤 Владелец: {message.from_user.first_name}\n'
            f'🔗 Теперь вы можете управлять чатом через админ-панель\n'
        )
        
    except Exception as e:
        print(f"Error in bind_chat_to_admin: {e}")
        await message.answer('❌ Произошла ошибка при привязке чата. Попробуйте позже.')


@router.message()
async def get_username(message: types.Message, bot: Bot):
    global is_auto_unmute
    global is_quests
    username = message.from_user.username
    user_id = int(message.from_user.id)
    # print(user_id, username, message.text)
    # if message.chat.id not in chats:
    #     await message.answer('кыш')
    #     await bot.send_message(chat_id=1240656726,text= f'{message.from_user.username} | {message.text} | {message.chat.title}')
    #     return
    
    # Initialize database for this chat if it doesn't exist
    init_chat_db(message.chat.id)
    
    try:
        connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
        cursor = connection.cursor()
        
        # Update user data in the current chat's database
        now = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        cursor.execute('UPDATE users SET username = ?, last_date = ?, mess_count = mess_count+1 WHERE tg_id = ?', 
                      (username, now, user_id))
        connection.commit()
        
        # Update chat member count in the current chat's database
        chat_mem = await bot.get_chat_member_count(chat_id=message.chat.id)
        try:
            cursor.execute('INSERT INTO count_users (chat_id, count) VALUES (?, ?)', (message.chat.id, chat_mem))
        except sqlite3.IntegrityError:
            cursor.execute('UPDATE count_users SET count = ? WHERE chat_id = ?', (chat_mem, message.chat.id))
        connection.commit()
        
    except sqlite3.OperationalError:
        pass
    finally:
        if 'connection' in locals():
            connection.close()
    
    # Note: The old centralized tables like [{-(sost_1)}], [{-(klan)}], [{-(sost_2)}], [1003101400599}, all_users
    # are not part of the new per-chat database structure. These would need to be handled differently
    # if they are still required for the application's functionality.
    
    # if is_auto_unmute == False:
    #     print('auto_unmute')
    #     await auto_unmute(message, bot)
    # if is_quests == False:
    #     print('quests')
        # await quests_funk(message, bot)
    if posting == False:
        print('posting')
        await shedul_posting(message, bot)
    return username



async def main() -> None:
    try:
        bot = Bot(token=TOKEN)
        dp = Dispatcher()

        dp.include_router(message_top_router)
        dp.include_router(farm_router)
        dp.include_router(cubes_router)
        # dp.include_router(kasik_router)
        dp.include_router(golden_rulet_router)
        dp.include_router(router)
        
    
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(e)
        await main()
 

if __name__ == "__main__":

    asyncio.run(main())
