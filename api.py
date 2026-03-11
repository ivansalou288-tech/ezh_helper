from math import log
import sqlite3
import os
import ssl
import random
import string
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import asyncio
from datetime import datetime
import password_generator
from typing import Any, Optional
import time
import json

# Добавляем корневую директорию проекта в путь
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from main.config3 import *
from main.secret import main_token as bot_token

# Импортируем бота для проверки статуса пользователей
try:
    from aiogram import Bot
    bot = Bot(token=bot_token)
except ImportError:
    bot = None
except Exception as e:
    bot = None

curent_path = (Path(__file__)).parent
all_path = curent_path / 'databases' / 'All.db'
admin_path = curent_path / 'databases' / 'admin.db'
main_path = curent_path / 'databases' / 'Base_bot.db'
app = FastAPI()

# Словарь имен чатов (из api copy.py)
chats_names = {
    'klan': 1002143434937, 
    'sost-1': 1002274082016, 
    'sost-2': 1002439682589
}

def get_db_path(chat_id: int):
    """Получает путь к базе данных чата"""
    if chat_id < 0 :
        chat_id_str = str(-chat_id)
    else:
        chat_id_str = str(chat_id)
    return curent_path / 'databases' / f'{chat_id_str}.db'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecomRemoveAction(BaseModel):
    rec_id: str
    user_id: Optional[int] = None
    chat_id: Optional[int] = None
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    admin_username: Optional[str] = None

class RecomGiveAction(BaseModel):
    user_id: int
    chat_id: int
    rank: str
    reason: str
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    admin_username: Optional[str] = None

class SnatWarnAction(BaseModel):
    chat: str
    userid: str
    num: int
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    admin_username: Optional[str] = None

class SetPermissionsAction(BaseModel):
    chat_id: str
    user_id: str
    view_users: bool
    grant_admin: bool
    manage_recommendations: bool
    manage_links: bool
    change_team_ranks: bool

class DeletePermissionsAction(BaseModel):
    chat_id: str
    user_id: str

class LinkCreateAction(BaseModel):
    activations: int
    chat_id: Optional[int] = None
    target_chats: Optional[list] = []
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    admin_username: Optional[str] = None

_cached_bot_username: Optional[str] = None

def get_bot_username() -> str:
    global _cached_bot_username
    if _cached_bot_username:
        return _cached_bot_username
    try:
        import requests
        r = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=5)
        data = r.json() if r.ok else {}
        username = (data.get("result") or {}).get("username")
        if username:
            _cached_bot_username = username
            return username
    except Exception:
        pass
    # Fallback: project default bot username (used in main_bot.py links)
    _cached_bot_username = "werty_clan_helper_bot"
    return _cached_bot_username






#? EN: Removes specific warning from user and reorganizes warning list
#* RU: Снимает конкретное предупреждение с пользователя и реорганизует список предупреждений
async def snat_warn_admn(user_id, chat_id,moder_id, number_warn, warn_count_new):
    chat_db_path = get_db_path(chat_id)
    connection = sqlite3.connect(chat_db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Получаем все предупреждения пользователя, отсортированные по дате
        cursor.execute("SELECT * FROM warns WHERE user_id = ? ORDER BY date", (user_id,))
        all_warns = cursor.fetchall()
        
        if not all_warns or number_warn > len(all_warns):
            return
            
        # Удаляем указанное предупреждение (1 = самое старое, 2 = второе, 3 = самое новое)
        warn_index = number_warn - 1
        if warn_index < len(all_warns):
            warn_to_delete = all_warns[warn_index]
            # Delete by user_id and reason to identify the specific warning
            cursor.execute("DELETE FROM warns WHERE user_id = ? AND reason = ? AND moder_id = ? AND date = ?", 
                        (user_id, warn_to_delete[1], warn_to_delete[2], warn_to_delete[3]))
            connection.commit()
            
        # Записываем в историю снятых предупреждений
        moder_name = GetUserByID(moder_id, chat_id).nik
        moder_mention = f'<a href="tg://user?id={moder_id}">{moder_name}</a>'
        
        try:
            cursor.execute('INSERT INTO warn_snat (user_id, warn_text, moder_give, moder_snat) VALUES (?, ?, ?, ?)', 
                        (user_id, warn_to_delete[1] if warn_index < len(all_warns) else 'Предупреждение', f'ID: {warn_to_delete[2]}' if warn_index < len(all_warns) else 'Неизвестен', moder_mention))
            connection.commit()
        except:
            pass
            
    except Exception as e:
        print(f"Error in snat_warn: {e}")
    finally:
        connection.close()

async def ban_user_admn(chat_id: int, user_id: int, admin_id: int, reason: str):
    """Банит пользователя в чате"""
    try:
        # Проверяем, состоит ли пользователь в чате
        
        
        # Кикаем пользователя из чата
        try:
            await bot.ban_chat_member(chat_id, user_id)
        except Exception:
            print('Всем похуй')
        user = GetUserByID(user_id, chat_id)
        moder = GetUserByID(admin_id, chat_id)
        
        # Записываем в историю банов (если есть таблица)
        chat_db_path = get_db_path(chat_id)
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()

        await snat_warn_admn(user_id, chat_id, admin_id, 3, 2)
        await snat_warn_admn(user_id, chat_id, admin_id, 2, 1)
        await snat_warn_admn(user_id, chat_id, admin_id, 1, 0)

        pubg_id = user.pubg_id
        date = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
        user_men = user.mention
        moder_men = moder.mention
        message_idd = (await bot.send_message(chat_id, f'<b>{voscl}Внимание{voscl}</b>\n{circle_em}Злостный нарушитель {user_men} получает бан и покидает нас\n👮‍♂️Выгнал его: {moder_men}\n{mes_em}Выгнали его за: {reason}', parse_mode='html')).message_id
        
        try:
            cursor.execute(f'INSERT INTO bans (tg_id, id_pubg, message_id, prichina, date, user_men, moder_men) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, pubg_id, message_idd, reason, date, user_men, moder_men))
        except sqlite3.IntegrityError:
            cursor.execute(f'UPDATE bans SET id_pubg = ? WHERE tg_id = ?', (pubg_id, user_id))
            cursor.execute(f'UPDATE bans SET message_id = ? WHERE tg_id = ?', (message_idd, user_id))
            cursor.execute(f'UPDATE bans SET prichina = ? WHERE tg_id = ?', (reason, user_id))
            cursor.execute(f'UPDATE bans SET date = ? WHERE tg_id = ?', (date, user_id))
            cursor.execute(f'UPDATE bans SET user_men = ? WHERE tg_id = ?', (user_men, user_id))
            cursor.execute(f'UPDATE bans SET moder_men = ? WHERE tg_id = ?', (moder_men, user_id))
        connection.commit()
        try:
            cursor.execute(f'DELETE FROM users WHERE tg_id = ?', (user_id, ))
            connection.commit()
        except sqlite3.OperationalError:
            pass
        
        print(f"Пользователь {user_id} успешно забанен в чате {chat_id}")
        return {"status": "success", "message": "Пользователь успешно забанен"}
        
    except Exception as e:
        error_msg = str(e)
        print(f"Ошибка при выполнении бана пользователя {user_id}: {error_msg}")
        
        if "PARTICIPANT_ID_INVALID" in error_msg:
            return {
                "status": "error",
                "message": f"Пользователь {user_id} не найден в чате. Возможно, он уже вышел или был удален."
            }
        elif "CHAT_ADMIN_REQUIRED" in error_msg:
            return {
                "status": "error", 
                "message": "У бота недостаточно прав для бана пользователей. Убедитесь, что бот является администратором."
            }
        else:
            return {
                "status": "error",
                "message": f"Ошибка при бане пользователя: {error_msg}"
            }






@app.get('/user-admin-chats/{user_id}')
def get_user_admin_chats(user_id: int):
    """
    Получает список чатов, где пользователь имеет админские права
    """
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        print(user_id)
        # Получаем все записи для пользователя из таблицы admins
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        print(rows)
        cursor.execute('SELECT * FROM admins')
        rowrr = cursor.fetchall()
        print(rowrr)
        
        if not rows:
            return {"status": "success", "admin_chats": []}
        
        admin_chats = []
        for row in rows:
            # Структура таблицы: user_id, chat_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk
            chat_data = {
                "user_id": row[0],
                "chat_id": row[1], 
                "chat_name": row[2] if row[2] else f"Chat {row[1]}",
                "permissions": {
                    "can_see_users": bool(row[3]) if len(row) > 3 else False,
                    "can_do_admin": bool(row[4]) if len(row) > 4 else False,
                    "can_recom": bool(row[5]) if len(row) > 5 else False,
                    "can_links": bool(row[6]) if len(row) > 6 else False,
                    "can_dk": bool(row[7]) if len(row) > 7 else False
                }
            }
            admin_chats.append(chat_data)
        
        connection.close()
        
        return {
            "status": "success",
            "user_id": user_id,
            "admin_chats": admin_chats,
            "count": len(admin_chats)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при получении админских чатов: {str(e)}"
        }

@app.get('/chat-avatar/{chat_id}')
def get_chat_avatar(chat_id: int):
    """
    Получает URL аватара чата через Telegram Bot API
    """
    try:
        import requests
        from main.config3 import bot_token
        
        # Получаем информацию о чате через Bot API
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {"chat_id": chat_id}
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("ok"):
            chat_info = data.get("result", {})
            photo = chat_info.get("photo")
            
            if photo:
                # Ищем фото в разных размерах
                avatar_file_id = None
                
                # Проверяем все возможные размеры фото
                if "big_file_id" in photo:
                    avatar_file_id = photo["big_file_id"]
                elif "small_file_id" in photo:
                    avatar_file_id = photo["small_file_id"]
                elif "file_id" in photo:
                    avatar_file_id = photo["file_id"]
                
                if avatar_file_id:
                    # Получаем URL файла
                    file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={avatar_file_id}"
                    
                    file_response = requests.get(file_url)
                    file_data = file_response.json()
                    
                    if file_data.get("ok"):
                        file_path = file_data["result"]["file_path"]
                        avatar_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                        
                        return {
                            "status": "success",
                            "avatar_url": avatar_url
                        }
            
        # Если фото нет или произошла ошибка, возвращаем пустой результат
        return {
            "status": "success",
            "avatar_url": None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при получении аватара чата: {str(e)}"
        }

@app.get('/chat-admin-panel/{chat_id}/{user_id}')
def get_chat_admin_panel(chat_id: int, user_id: int):
    """
    Получает данные для админ панели конкретного чата
    """
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Проверяем права пользователя на этот чат
        cursor.execute('SELECT * FROM admins WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        admin_data = cursor.fetchone()
        
        if not admin_data:
            return {
                "status": "error",
                "message": "У вас нет прав на этот чат"
            }
        
        # Получаем информацию о чате
        chat_name = admin_data[2] if admin_data[2] else f"Chat {chat_id}"
        
        # Получаем права пользователя
        permissions = {
            "can_see_users": bool(admin_data[3]) if len(admin_data) > 3 else False,
            "can_do_admin": bool(admin_data[4]) if len(admin_data) > 4 else False,
            "can_recom": bool(admin_data[5]) if len(admin_data) > 5 else False,
            "can_links": bool(admin_data[6]) if len(admin_data) > 6 else False,
            "can_dk": bool(admin_data[7]) if len(admin_data) > 7 else False
        }
        
        # Собираем данные для панели в зависимости от прав
        panel_data = {
            "status": "success",
            "chat_id": chat_id,
            "chat_name": chat_name,
            "permissions": permissions,
            "available_functions": []
        }
        
        # Добавляем доступные функции в зависимости от прав
        if permissions["can_see_users"]:
            panel_data["available_functions"].append({
                "id": "see_users",
                "name": "Просмотр пользователей",
                "description": "Просмотр списка пользователей чата"
            })
        
        if permissions["can_do_admin"]:
            panel_data["available_functions"].extend([
                {
                    "id": "admin_functions",
                    "name": "Административные функции",
                    "description": "Управление пользователями и настройками чата"
                },
                {
                    "id": "warn_management",
                    "name": "Управление предупреждениями",
                    "description": "Выдача и снятие предупреждений"
                }
            ])
        
        if permissions["can_recom"]:
            panel_data["available_functions"].append({
                "id": "recommendations",
                "name": "Рекомендации",
                "description": "Управление рекомендациями пользователей"
            })
        
        if permissions["can_links"]:
            panel_data["available_functions"].append({
                "id": "links",
                "name": "Ссылки",
                "description": "Управление ссылками чата"
            })
        
        if permissions["can_dk"]:
            panel_data["available_functions"].append({
                "id": "dk_functions",
                "name": "DK функции",
                "description": "Специальные функции DK"
            })
        
        connection.close()
        return panel_data
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при загрузке админ панели: {str(e)}"
        }

async def get_users_sdk(chat: int):
    """
    Получение пользователей чата как в api copy.py с правильной обработкой статуса
    """

    
    connection = sqlite3.connect(get_db_path(chat), check_same_thread=False)
    cursor = connection.cursor()
    
    # Получаем данные из таблицы чата
    userss = cursor.execute(f'SELECT * FROM users').fetchall()
    users = {}
    index = 1
    
    for user in userss:
        tg_ids = user[0]
        usernames = user[1]
        names = user[2]
        age = user[3]
        nik_pubg = user[4]
        id_pubg = user[5]
        nik = user[6]
        rang = user[7]
        last_date = user[8]
        date_vhod = user[9]
        mess_count = user[10]
        try:
        # Пытаемся получить статус участника в чате; если его больше нет в чате,
        # Telegram может вернуть ошибку "member not found" — тогда используем ранг
            chat_status = '� Состоит в чате'  # по умолчанию считаем, что состоит


            chat_member = await bot.get_chat_member(chat, tg_ids)
            status = chat_member.status
   
            if status == 'administrator':
                        chat_status = '👨🏻‍🔧 Телеграм-админ этого чата'
            elif status == 'creator':
                        chat_status = '👨🏻‍🔧 Создатель этого чата'
            elif status == 'member' or status == 'restricted':
                        chat_status = '💚 Состоит в чате'
            else:
                        chat_status = '💔 Не состоит в чате'
        except Exception:
            chat_status = '💔 Не состоит в чате'

            

        users[index] = {
            'tg_ids': tg_ids,
            'username': usernames,
            'name': names,
            'age': age,
            'nik_pubg': nik_pubg,
            'id_pubg': id_pubg,
            'nik': nik,
            'rang': rang,
            'last_date': last_date,
            'date_vhod': date_vhod,
            'mess_count': mess_count,
            'status': chat_status,
        }
        index += 1
    
    connection.close()
    return users

@app.get("/users/{chat}")
async def get_users(chat: int):
    """
    Получение пользователей чата (как в api copy.py)
    """
    try:
        
        users = await get_users_sdk(chat)
        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{chat}/{user_id}")
async def get_user(chat: int, user_id: int):
    """
    Получение одного пользователя по chat_id и user_id
    """
    try:
        users = await get_users_sdk(chat)
        
        # Ищем пользователя по tg_ids
        for user_key, user_data in users.items():
            if user_data and user_data.get('tg_ids') == user_id:
                return user_data
        
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/warns/{chat}/{user_id}")
async def get_user_warnings(chat: int, user_id: int):
    """
    Получение предупреждений пользователя по chat_id и user_id
    """
    try:
        # Используем базу данных конкретного чата
        connection = sqlite3.connect(get_db_path(chat), check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM warns WHERE user_id=?", (user_id,))
        warns = cursor.fetchall()
        
        if not warns:
            return []
        
        # Формируем массив предупреждений
        warns_data = []
        for i, warn in enumerate(warns, 1):
            reason = warn[1] if warn[1] else 'Без причины'
            moder_id = warn[2]
            date = warn[3] if warn[3] else 'Неизвестна'
            
            # Получаем имя модератора
            try:
                moder_cursor = connection.cursor()
                moder_cursor.execute("SELECT nik FROM users WHERE tg_id=?", (moder_id,))
                moder_result = moder_cursor.fetchall()
                moder_name = moder_result[0][0] if moder_result else f"ID: {moder_id}"
            except:
                moder_name = f"ID: {moder_id}"
            
            warns_data.append({
                "num": i,
                "reason": reason,
                "moder_link": GetUserByID(moder_id, chat).mention,
                "moder": moder_name,
                "date": date
            })
        connection.close()
        return warns_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get('/chat-users/{chat_id}')
def get_chat_users(chat_id: int):
    """
    Получает список пользователей чата
    """
    try:
        # Получаем путь к базе данных чата
        chat_db_path = get_db_path(chat_id)
        
        if not os.path.exists(chat_db_path):
            return {
                "status": "error",
                "message": "База данных чата не найдена"
            }
        
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Упрощенный запрос - получаем только то, что точно есть
        cursor.execute('''
            SELECT tg_id, nik, rang, date_vhod, last_date 
            FROM users 
            ORDER BY rang DESC, nik
        ''')
        users = cursor.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                "tg_id": user[0],
                "nik": user[1] or f"User {user[0]}",
                "rang": user[2] if user[2] is not None else 0,
                "join_date": user[3],
                "last_active": user[4],
                "username": "",
                "name": "",
                "status": "member" if (user[2] or 0) >= 1 else "guest",
                "last_message": "Нет сообщений",
                "last_message_date": None
            })
        
        connection.close()
        
        return {
            "status": "success",
            "users": users_list,
            "count": len(users_list)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при получении пользователей: {str(e)}"
        }

@app.get('/search-users/{chat_id}')
def search_users(chat_id: int, q: str = ''):
    """
    Поиск пользователей по частичному совпадению username
    """
    try:
        chat_db_path = get_db_path(chat_id)
        
        if not os.path.exists(chat_db_path):
            return {"status": "error", "message": "База данных чата не найдена"}
        
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Поиск по частичному совпадению (регистронезависимый)
        search_pattern = f"%{q.lower()}%"
        cursor.execute('''
            SELECT tg_id, nik, rang, date_vhod, last_date 
            FROM users 
            WHERE LOWER(nik) LIKE ?
            ORDER BY rang DESC, nik
            LIMIT 50
        ''', (search_pattern,))
        
        users = cursor.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                "tg_id": user[0],
                "nik": user[1] or f"User {user[0]}",
                "rang": user[2] if user[2] is not None else 0,
                "join_date": user[3],
                "last_active": user[4]
            })
        
        connection.close()
        
        return {
            "status": "success",
            "users": users_list,
            "count": len(users_list)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка поиска: {str(e)}"
        }

@app.get('/recom/{chat_id}/{user}')
def get_recom(chat_id: int, user: int):
    try:
        # Получаем путь к базе данных конкретного чата (как в main_bot.py)
        chat_db_path = curent_path / 'databases' / f'{-chat_id}.db'
        
        if not chat_db_path.exists():
            return []
        
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Получаем рекомендации пользователя
        all_recs = cursor.execute('SELECT * FROM recommendation WHERE user_id = ?', (user,)).fetchall()
        
        # Получаем ранги для должностей
        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер', 'Владелец')
        
        recommendations = []
        for rec in all_recs:
            # Структура таблицы: user_id, pubg_id, moder, comments, rang, date, recom_id
            user_id = rec[0]
            pubg_id = rec[1]
            moder_id = rec[2]
            reason = rec[3]
            rang = rec[4]
            date = rec[5]
            rec_id = rec[6]
            
            # Получаем имя модератора
            try:
                moder_name = cursor.execute("SELECT nik FROM users WHERE tg_id=?", (int(moder_id),)).fetchall()[0][0]
            except (IndexError, ValueError):
                moder_name = str(moder_id)
            
            # Получаем ранг модератора
            try:
                rang_m = cursor.execute("SELECT rang FROM users WHERE tg_id=?", (int(moder_id),)).fetchall()[0][0]
                # Ensure rang value is within bounds
                if rang_m < 0:
                    rang_m = 0
                elif rang_m >= len(rangs_name):
                    rang_m = len(rangs_name) - 1
                moder_rang = rangs_name[rang_m]
            except (IndexError, ValueError):
                moder_rang = 'Неизвестная должность'
            
            recommendation = {
                "rec_id": rec_id,
                "user_id": user_id,
                "pubg_id": pubg_id,
                "moder_id": moder_id,
                "moder_name": moder_name,
                "moder_rang": moder_rang,
                "reason": reason,
                "rang": rang,
                "date": date
            }
            recommendations.append(recommendation)
        
        connection.close()
        return recommendations
        
    except Exception as e:
        return []

@app.get('/recom/{user}')
def get_recom_fallback(user: int):
    # Временный fallback для совместимости - используем основной групповой чат
    return get_recom(1003012971064, user)

@app.post('/recom-remove')
def recom_remove(action: RecomRemoveAction):
    # Проверка прав доступа - используем основную базу админов
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (action.admin_id,))
        admin_check = cursor.fetchall()
        connection.close()
        
        if not admin_check:
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Если указан конкретный chat_id, используем только его
    if action.chat_id:
        try:
            chat_db_path = curent_path / 'databases' / f'{-action.chat_id}.db'
            
            if not chat_db_path.exists():
                raise HTTPException(status_code=404, detail="Chat database not found")
                
            connection = sqlite3.connect(chat_db_path, check_same_thread=False)
            cursor = connection.cursor()
            
            if action.user_id is None:
                cursor.execute('DELETE FROM recommendation WHERE recom_id = ?', (action.rec_id,))
            else:
                cursor.execute('DELETE FROM recommendation WHERE recom_id = ? AND user_id = ?', (action.rec_id, action.user_id))
            
            deleted = cursor.rowcount
            connection.commit()
            connection.close()
            
            if deleted == 0:
                raise HTTPException(status_code=404, detail="Recommendation not found")
                
            return {"status": "ok", "deleted": deleted, "chat_id": action.chat_id}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Иначе ищем по всем чатам (старое поведение)
    else:
        chat_found = False
        deleted_count = 0
        
        for chat_name, chat_id in chats_names.items():
            try:
                chat_db_path = curent_path / 'databases' / f'{-chat_id}.db'
                
                if not chat_db_path.exists():
                    continue
                    
                connection = sqlite3.connect(chat_db_path, check_same_thread=False)
                cursor = connection.cursor()
                
                if action.user_id is None:
                    cursor.execute('DELETE FROM recommendation WHERE recom_id = ?', (action.rec_id,))
                else:
                    cursor.execute('DELETE FROM recommendation WHERE recom_id = ? AND user_id = ?', (action.rec_id, action.user_id))
                
                deleted = cursor.rowcount
                if deleted > 0:
                    deleted_count += deleted
                    chat_found = True
                    
                connection.commit()
                connection.close()
                
            except Exception as e:
                continue
        
        if not chat_found or deleted_count == 0:
            raise HTTPException(status_code=404, detail="Recommendation not found")
            
        return {"status": "ok", "deleted": deleted_count}

@app.post('/recom-give')
def recom_give(action: RecomGiveAction):
    print("="*50)
    print("Получен запрос на выдачу рекомендации:")
    print(f"Chat ID: {action.chat_id}")
    print(f"User ID: {action.user_id}")
    print(f"Rank: {action.rank}")
    print(f"Reason: {action.reason}")
    print(f"Admin ID: {action.admin_id}")
    print(f"Admin Name: {action.admin_name}")
    print(f"Admin Username: {action.admin_username}")
    print("="*50)
    connection = sqlite3.connect(get_db_path(action.chat_id), check_same_thread=False)
    cursor = connection.cursor()
    if action.admin_id == action.user_id:
        raise HTTPException(status_code=400, detail="Нельзя выдать рекомендацию самому себе")
        return {"status": "error", "message": "Нельзя выдать рекомендацию самому себе"} 
    id_recom = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    cursor.execute(
        'INSERT INTO recommendation (user_id, pubg_id, moder, comments, rang, date, recom_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (action.user_id, action.chat_id, action.admin_id, action.reason, action.rank, datetime.now(), id_recom))
    connection.commit()
    connection.close()
    return {"status": "ok", "message": "Данные получены"}

@app.get('/api/links/all')
def get_all_links(chat_id: Optional[int] = None):
    """
    Получает все ссылки из таблицы links
    """
    try:
        connection = sqlite3.connect(all_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Создаем таблицу если не существует
        cursor.execute('''CREATE TABLE IF NOT EXISTS links (
            chat_id INTEGER,
            link TEXT,
            activate_cnt INTEGER,
            target_chats TEXT
        )''')
        
        # Добавляем колонку target_chats если она не существует
        try:
            cursor.execute('ALTER TABLE links ADD COLUMN target_chats TEXT')
        except sqlite3.OperationalError:
            # Колонка уже существует
            pass
        
        connection.commit()
        
        if chat_id:
            # Получаем ссылки для конкретного чата
            cursor.execute('SELECT chat_id, link, activate_cnt FROM links WHERE chat_id = ? ORDER BY chat_id', (chat_id,))
        else:
            # Получаем все ссылки
            cursor.execute('SELECT chat_id, link, activate_cnt FROM links ORDER BY chat_id')
        
        links = cursor.fetchall()
        connection.close()
        
        links_list = []
        for link in links:
            links_list.append({
                "chat_id": link[0],
                "link": link[1],
                "activate_cnt": link[2] if link[2] is not None else 0
            })
        print(links_list)
        return {
            "status": "success",
            "links": links_list,
            "count": len(links_list)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при получении ссылок: {str(e)}"
        }

class LinkDeleteAction(BaseModel):
    link: str
    chat_id: Optional[int] = None

class CheckCodeAction(BaseModel):
    code: str

class SubmitFormAction(BaseModel):
    telegram_id: Optional[int] = None
    user: Optional[str] = None
    name: str
    age: int
    nick: str
    gameId: str
    invite_code: str
    target_chats: Optional[list] = []

class GenerateLinksAction(BaseModel):
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    chat_id: int
    target_chats: Optional[list] = []

@app.post('/api/links/delete')
def delete_link(action: LinkDeleteAction):
    """
    Удаляет ссылку из таблицы links
    """
    try:
        link = action.link
        chat_id = action.chat_id
        
        if not link:
            return {"status": "error", "message": "link is required"}
        
        connection = sqlite3.connect(all_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Создаем таблицу если не существует
        cursor.execute('''CREATE TABLE IF NOT EXISTS links (
            chat_id INTEGER,
            link TEXT,
            activate_cnt INTEGER,
            target_chats TEXT
        )''')
        
        # Добавляем колонку target_chats если она не существует
        try:
            cursor.execute('ALTER TABLE links ADD COLUMN target_chats TEXT')
        except sqlite3.OperationalError:
            # Колонка уже существует
            pass
        
        connection.commit()
        
        # Удаляем ссылку
        if chat_id:
            cursor.execute('DELETE FROM links WHERE link = ? AND chat_id = ?', (link, chat_id))
        else:
            cursor.execute('DELETE FROM links WHERE link = ?', (link,))
        
        deleted = cursor.rowcount
        connection.commit()
        connection.close()
        
        if deleted == 0:
            return {"status": "error", "message": "Ссылка не найдена"}
        
        return {
            "status": "success",
            "message": "Ссылка успешно удалена",
            "deleted": deleted
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при удалении ссылки: {str(e)}"
        }

@app.post('/check_invite_code')
def check_invite_code(action: CheckCodeAction):
    """
    Проверяет действительность кода приглашения
    """
    try:
        code = action.code
        
        if not code:
            return {"status": "error", "message": "Код не указан"}
        
        connection = sqlite3.connect(all_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Создаем таблицу если не существует
        cursor.execute('''CREATE TABLE IF NOT EXISTS links (
            chat_id INTEGER,
            link TEXT,
            activate_cnt INTEGER,
            target_chats TEXT
        )''')
        
        # Добавляем колонку target_chats если она не существует
        try:
            cursor.execute('ALTER TABLE links ADD COLUMN target_chats TEXT')
        except sqlite3.OperationalError:
            # Колонка уже существует
            pass
        
        connection.commit()
        
        # Ищем код в таблице
        cursor.execute('SELECT chat_id, activate_cnt, target_chats FROM links WHERE link = ?', (code,))
        result = cursor.fetchone()
        connection.close()
        
        if not result:
            return {"status": "error", "message": "Неверный код приглашения"}
        
        chat_id, activate_cnt, target_chats_json = result
        
        if activate_cnt <= 0:
            return {"status": "error", "message": "Код больше не действителен"}
        
        # Парсим список целевых чатов
        import json
        target_chats = []
        try:
            target_chats = json.loads(target_chats_json) if target_chats_json else []
        except:
            target_chats = []
        
        # Определяем состав на основе chat_id
        sost = "sost-1" if chat_id == chats_names['sost-1'] else "sost-2" if chat_id == chats_names['sost-2'] else "unknown"
        
        return {
            "status": "success",
            "data": {
                "link": code,
                "chat_id": chat_id,
                "activate_count": activate_cnt,
                "target_chats": target_chats,
                "sost": sost
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при проверке кода: {str(e)}"
        }

@app.post('/submit_form')
async def submit_form(action: SubmitFormAction):
    """
    Принимает данные пользователя из формы заявки
    """
    try:
        # Валидация обязательных полей
        if not action.name or not action.nick or not action.gameId or not action.invite_code:
            return {"status": "error", "message": "Заполните все обязательные поля"}
        
        if action.age < 7 or action.age > 50:
            return {"status": "error", "message": "Возраст должен быть от 7 до 50"}

        connection = sqlite3.connect(all_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('SELECT chat_id, target_chats FROM links WHERE link = ?', (action.invite_code,))
        link_data = cursor.fetchone()
        
        if not link_data:
            return {"status": "error", "message": "Код приглашения не найден"}
        
        chat_id, target_chats_json = link_data
        
        # Парсим список целевых чатов
        import json
        target_chats = []
        try:
            target_chats = json.loads(target_chats_json) if target_chats_json else []
        except:
            target_chats = []
        
        # Если список целевых чатов пуст, используем основной chat_id
        if not target_chats:
            target_chats = [chat_id]
        
        connection.commit()
        connection.close()
        
        # Добавляем пользователя во все целевые чаты
        added_chats = []
        failed_chats = []
        
        for target_chat_id in target_chats:
            try:
                connection = sqlite3.connect(get_db_path(target_chat_id), check_same_thread=False)
                cursor = connection.cursor()
                
                cursor.execute('INSERT INTO users (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod, mess_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (action.telegram_id, action.user, action.name, action.age, action.nick, action.gameId, action.nick, 0, '', datetime.now().strftime('%H:%M:%S %d.%m.%Y'), 0))
                connection.commit()
                connection.close()
                added_chats.append(target_chat_id)
                
            except Exception as e:
                print(f"Ошибка при добавлении пользователя в чат {target_chat_id}: {e}")
                failed_chats.append(target_chat_id)
        
        print("="*50)
        print("Новая заявка в клан:")
        print(f"Telegram ID: {action.telegram_id}")
        print(f"Username: {action.user}")
        print(f"Имя: {action.name}")
        print(f"Возраст: {action.age}")
        print(f"Ник: {action.nick}")
        print(f"Game ID: {action.gameId}")
        print(f"Код приглашения: {action.invite_code}")
        print(f"Целевые чаты: {target_chats}")
        print(f"Успешно добавлено в чаты: {added_chats}")
        print(f"Не удалось добавить в чаты: {failed_chats}")
        print("="*50)
        
        # Отправляем уведомление в основной чат
        if added_chats:
            try:
                chat_names = []
                for chat_id in added_chats:
                    chat_name = f"Chat {chat_id}"
                    # Пытаемся получить имя чата из admin базы
                    try:
                        admin_conn = sqlite3.connect(admin_path, check_same_thread=False)
                        admin_cursor = admin_conn.cursor()
                        admin_cursor.execute('SELECT chat_name FROM admins WHERE chat_id = ? LIMIT 1', (chat_id,))
                        chat_name_result = admin_cursor.fetchone()
                        if chat_name_result and chat_name_result[0]:
                            chat_name = chat_name_result[0]
                        admin_conn.close()
                    except:
                        pass
                    chat_names.append(chat_name)
                
                message = f"Новая заявка в клан:\nTelegram ID: {action.telegram_id}\nUsername: {action.user}\nИмя: {action.name}\nВозраст: {action.age}\nНик: {action.nick}\nGame ID: {action.gameId}\nКод приглашения: {action.invite_code}\nДобавлен в чаты: {', '.join(chat_names)}"
                
                if failed_chats:
                    message += f"\nНе удалось добавить в чаты: {', '.join([f'Chat {cid}' for cid in failed_chats])}"
                
                await bot.send_message(chat_id, message)
            except Exception as e:
                print(f"Ошибка при отправке уведомления: {e}")
        
        return {
            "status": "success",
            "message": f"Заявка успешно отправлена. Добавлен в {len(added_chats)} чатов.",
            "application_id": action.telegram_id,
            "added_chats": added_chats,
            "failed_chats": failed_chats
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при отправке заявки: {str(e)}"
        }

class GenerateLinksByCodeAction(BaseModel):
    code: str
    telegram_id: Optional[int] = None
    username: Optional[str] = None

@app.post('/generate_invite_links_by_code')
async def generate_invite_links_by_code(action: GenerateLinksByCodeAction):
    """
    Генерирует ссылки-приглашения для всех чатов указанных в коде приглашения
    """
    try:
        if not action.code:
            return {"status": "error", "message": "код приглашения обязателен"}
        
        # Сначала проверяем код и получаем информацию о нем
        connection = sqlite3.connect(all_path, check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute('SELECT chat_id, activate_cnt, target_chats FROM links WHERE link = ?', (action.code,))
        result = cursor.fetchone()
        connection.close()
        
        if not result:
            return {"status": "error", "message": "Неверный код приглашения"}
        
        chat_id, activate_cnt, target_chats_json = result
        
        if activate_cnt <= 0:
            return {"status": "error", "message": "Код больше не действителен"}
        
        # Парсим список целевых чатов
        import json
        target_chats = []
        try:
            target_chats = json.loads(target_chats_json) if target_chats_json else []
        except:
            target_chats = []
        
        # Если target_chats пустой, используем основной chat_id
        if not target_chats:
            target_chats = [chat_id]
        
        # Получаем аватары чатов через Telegram Bot API
        import requests
        
        def get_chat_info(chat_id):
            try:
                url = f"https://api.telegram.org/bot{bot_token}/getChat"
                params = {"chat_id": chat_id}
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if data.get("ok"):
                    chat_info = data.get("result", {})
                    return {
                        "name": chat_info.get("title", "Unknown"),
                        "avatar": get_chat_avatar_from_info(chat_info)
                    }
                
                return {"name": "Unknown", "avatar": None}
                
            except Exception as e:
                print(f"Ошибка при получении информации о чате {chat_id}: {e}")
                return {"name": "Unknown", "avatar": None}
        
        def get_chat_avatar_from_info(chat_info):
            try:
                photo = chat_info.get("photo")
                
                if photo:
                    # Ищем фото в разных размерах
                    avatar_file_id = None
                    
                    if "big_file_id" in photo:
                        avatar_file_id = photo["big_file_id"]
                    elif "small_file_id" in photo:
                        avatar_file_id = photo["small_file_id"]
                    elif "file_id" in photo:
                        avatar_file_id = photo["file_id"]
                    
                    if avatar_file_id:
                        # Получаем URL файла
                        file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={avatar_file_id}"
                        
                        file_response = requests.get(file_url)
                        file_data = file_response.json()
                        
                        if file_data.get("ok"):
                            file_path = file_data["result"]["file_path"]
                            avatar_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                            return avatar_url
                
                return None
                
            except Exception as e:
                print(f"Ошибка при получении аватара чата: {e}")
                return None
        
        # Получаем информацию о всех чатах
        chats_data = []
        for chat_id in target_chats:
            try:
                chat_info = get_chat_info(chat_id)
                chat_link = await bot.export_chat_invite_link(chat_id)
                
                chats_data.append({
                    "chat_id": chat_id,
                    "name": chat_info.get("name", "Unknown"),
                    "link": chat_link,
                    "avatar": chat_info.get("avatar") or "/avatars/clan.png"
                })
            except Exception as e:
                print(f"Ошибка при генерации ссылки для чата {chat_id}: {e}")
                continue
        
        # Формируем данные для ответа
        links_data = {
            "chats": chats_data,
            "count": len(chats_data),
            "code": action.code,
            "main_chat_id": chat_id
        }
        
        print("="*50)
        print("Сгенерированы ссылки по коду приглашения:")
        print(f"Код: {action.code}")
        print(f"Telegram ID: {action.telegram_id}")
        print(f"Username: {action.username}")
        print(f"Основной Chat ID: {chat_id}")
        print(f"Целевые чаты: {target_chats}")
        print(f"Сгенерировано ссылок: {len(chats_data)}")
        for chat in chats_data:
            print(f"  - {chat['name']} ({chat['chat_id']}): {chat['link']}")
        print("="*50)
 
        return {
            "status": "success",
            "data": links_data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при генерации ссылок: {str(e)}"
        }

@app.post('/generate_invite_links')
async def generate_invite_links(action: GenerateLinksAction):
    """
    Генерирует ссылки-приглашения для чатов на основе chat_id с получением аватаров
    """
    try:
        if not action.chat_id:
            return {"status": "error", "message": "chat_id обязателен"}
        
        # Получаем аватары чатов через Telegram Bot API
        import requests
        
        def get_chat_info(chat_id):
            try:
                url = f"https://api.telegram.org/bot{bot_token}/getChat"
                params = {"chat_id": chat_id}
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if data.get("ok"):
                    chat_info = data.get("result", {})
                    return {
                        "name": chat_info.get("title", "Unknown"),
                        "avatar": get_chat_avatar_from_info(chat_info)
                    }
                
                return {"name": "Unknown", "avatar": None}
                
            except Exception as e:
                print(f"Ошибка при получении информации о чате {chat_id}: {e}")
                return {"name": "Unknown", "avatar": None}
        
        def get_chat_avatar_from_info(chat_info):
            try:
                photo = chat_info.get("photo")
                
                if photo:
                    # Ищем фото в разных размерах
                    avatar_file_id = None
                    
                    if "big_file_id" in photo:
                        avatar_file_id = photo["big_file_id"]
                    elif "small_file_id" in photo:
                        avatar_file_id = photo["small_file_id"]
                    elif "file_id" in photo:
                        avatar_file_id = photo["file_id"]
                    
                    if avatar_file_id:
                        # Получаем URL файла
                        file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={avatar_file_id}"
                        
                        file_response = requests.get(file_url)
                        file_data = file_response.json()
                        
                        if file_data.get("ok"):
                            file_path = file_data["result"]["file_path"]
                            avatar_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                            return avatar_url
                
                return None
                
            except Exception as e:
                print(f"Ошибка при получении аватара чата: {e}")
                return None
        
        # Определяем список чатов для генерации ссылок
        target_chats = action.target_chats if action.target_chats else [action.chat_id]
        
        # Получаем информацию о всех чатах
        chats_data = []
        for chat_id in target_chats:
            try:
                chat_info = get_chat_info(chat_id)
                chat_link = await bot.export_chat_invite_link(chat_id)
                
                chats_data.append({
                    "chat_id": chat_id,
                    "name": chat_info.get("name", "Unknown"),
                    "link": chat_link,
                    "avatar": chat_info.get("avatar") or "/avatars/clan.png"
                })
            except Exception as e:
                print(f"Ошибка при генерации ссылки для чата {chat_id}: {e}")
                continue
        
        # Формируем данные для ответа
        links_data = {
            "chats": chats_data,
            "count": len(chats_data)
        }
        
        print("="*50)
        print("Сгенерированы ссылки для пользователя:")
        print(f"Telegram ID: {action.telegram_id}")
        print(f"Username: {action.username}")
        print(f"Основной Chat ID: {action.chat_id}")
        print(f"Целевые чаты: {target_chats}")
        print(f"Сгенерировано ссылок: {len(chats_data)}")
        for chat in chats_data:
            print(f"  - {chat['name']} ({chat['chat_id']}): {chat['link']}")
        print("="*50)
 
        return {
            "status": "success",
            "data": links_data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при генерации ссылок: {str(e)}"
        }

@app.get('/admin-chats/{user_id}')
def get_admin_chats(user_id: int):
    """
    Получает список чатов, где пользователь является администратором
    """
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Получаем все чаты, где пользователь является админом
        cursor.execute('SELECT DISTINCT chat_id, chat_name FROM admins WHERE user_id = ? AND can_links = 1', (user_id,))
        admin_chats = cursor.fetchall()
        
        connection.close()
        
        chats_list = []
        for chat in admin_chats:
            chats_list.append({
                "chat_id": chat[0],
                "chat_name": chat[1] or f"Chat {chat[0]}"
            })
        
        return {
            "status": "success",
            "chats": chats_list,
            "count": len(chats_list)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при получении чатов админа: {str(e)}"
        }

@app.post('/links-create')
def links_create(action: LinkCreateAction):
    connection = sqlite3.connect(all_path, check_same_thread=False)
    cursor = connection.cursor()
    print("="*50)
    print("Получен запрос на создание ссылки:")
    print(f"Chat ID: {action.chat_id}")
    print(f"Target Chats: {action.target_chats}")
    print(f"Activations: {action.activations}")
    print(f"Admin ID: {action.admin_id}")
    print(f"Admin Name: {action.admin_name}")
    print(f"Admin Username: {action.admin_username}")
    print("="*50)

    # Базовая серверная валидация
    if not isinstance(action.activations, int):
        raise HTTPException(status_code=400, detail="activations must be int")
    if action.activations < 1 or action.activations > 50:
        raise HTTPException(status_code=400, detail="activations must be in range 1..50")

    if action.chat_id is None:
        raise HTTPException(status_code=400, detail="chat_id is required")
    if not isinstance(action.chat_id, int):
        raise HTTPException(status_code=400, detail="chat_id must be int")

    # Генерируем telegram deep-link (рефералку) для бота:
    # при переходе Telegram отправит боту: /start <payload>
    # payload компактный и легко парсится ботом
    bot_username = get_bot_username()
    # payload = f"lk_{action.chat_id}_{action.activations}"
    # link = f"https://t.me/{bot_username}?start={payload}"
    link = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    # Конвертируем список чатов в JSON строку для хранения
    import json
    target_chats_json = json.dumps(action.target_chats) if action.target_chats else "[]"
    
    # Создаем таблицу если не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS links (
        chat_id INTEGER,
        link TEXT,
        activate_cnt INTEGER,
        target_chats TEXT
    )''')
    
    # Добавляем колонку target_chats если она не существует
    try:
        cursor.execute('ALTER TABLE links ADD COLUMN target_chats TEXT')
    except sqlite3.OperationalError:
        # Колонка уже существует
        pass
    
    connection.commit()
    cursor.execute('INSERT INTO links (chat_id, link, activate_cnt, target_chats) VALUES (?, ?, ?, ?)', 
                   (action.chat_id, link, action.activations, target_chats_json))
    connection.commit()

    return {"status": "ok", "link": link, "activations": action.activations, "target_chats": action.target_chats}

class BanUserAction(BaseModel):
    chat_id: int
    user_id: int
    reason: str
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    admin_username: Optional[str] = None

class DeleteUserAction(BaseModel):
    chat_id: int
    user_id: int
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    admin_username: Optional[str] = None

@app.post('/ban_user')
async def ban_user(action: BanUserAction):
    """
    Банит пользователя в чате
    """
    try:
        print("="*50)
        print("Получен запрос на бан пользователя:")
        print(f"Chat ID: {action.chat_id}")
        print(f"User ID: {action.user_id}")
        print(f"Reason: {action.reason}")
        print(f"Admin ID: {action.admin_id}")
        print(f"Admin Name: {action.admin_name}")
        print(f"Admin Username: {action.admin_username}")
        print("="*50)

        # Проверяем, не является ли пользователь владельцем чата
        try:
            if bot:
                chat_member = await bot.get_chat_member(action.chat_id, action.user_id)
                if chat_member.status == 'creator':
                    return {
                        "status": "error", 
                        "message": "Нельзя забанить владельца чата"
                    }
        except Exception as e:
            print(f"Ошибка при проверке статуса пользователя: {e}")

        # Здесь можно добавить логику бана пользователя
        # Например, добавление в специальную таблицу забаненных пользователей
        # или вызов Telegram Bot API для бана
        
        ban_result = await ban_user_admn(action.chat_id, action.user_id, action.admin_id, action.reason)
        
        if ban_result and ban_result.get("status") == "error":
            return ban_result

        return {
            "status": "success",
            "message": f"Пользователь {action.user_id} забанен в чате {action.chat_id}",
            "reason": action.reason
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при бане пользователя: {str(e)}"
        }

@app.post('/delete_user')
async def delete_user(action: DeleteUserAction):
    """
    Удаляет пользователя из базы данных чата
    """
    try:
        print("="*50)
        print("Получен запрос на удаление пользователя:")
        print(f"Chat ID: {action.chat_id}")
        print(f"User ID: {action.user_id}")
        print(f"Admin ID: {action.admin_id}")
        print(f"Admin Name: {action.admin_name}")
        print(f"Admin Username: {action.admin_username}")
        print("="*50)

        # Проверяем, не является ли пользователь владельцем чата
        try:
            if bot:
                chat_member = await bot.get_chat_member(action.chat_id, action.user_id)
                if chat_member.status == 'creator':
                    return {
                        "status": "error", 
                        "message": "Нельзя удалить владельца чата из базы данных"
                    }
        except Exception as e:
            print(f"Ошибка при проверке статуса пользователя: {e}")

        # Удаляем пользователя из базы данных чата
        connection = sqlite3.connect(get_db_path(action.chat_id), check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute('DELETE FROM users WHERE tg_id = ?', (action.user_id,))
        deleted = cursor.rowcount
        
        connection.commit()
        connection.close()
        
        if deleted == 0:
            return {"status": "error", "message": "Пользователь не найден в базе данных"}
        
        return {
            "status": "success",
            "message": f"Пользователь {action.user_id} удален из базы данных чата {action.chat_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при удалении пользователя: {str(e)}"
        }

@app.post('/set_permissions')
def set_permissions(action: SetPermissionsAction):
    """
    Устанавливает права пользователю для чата
    """
    print("="*50)
    print("Получены данные для установки прав:")
    print(f"Chat ID: {action.chat_id}")
    print(f"User ID: {action.user_id}")
    print(f"Просмотр пользователей: {action.view_users}")
    print(f"Выдача админки: {action.grant_admin}")
    print(f"Управление рекомендациями: {action.manage_recommendations}")
    print(f"Управление ссылками: {action.manage_links}")
    print(f"Изменение рангов команд: {action.change_team_ranks}")
    print("="*50)
    
    try: 
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Проверяем, есть ли уже запись для этого пользователя и чата
        cursor.execute('SELECT * FROM admins WHERE user_id = ? AND chat_id = ?', (int(action.user_id), int(action.chat_id)))
        existing = cursor.fetchone()
        
        if existing:
            # Обновляем существующую запись
            print("Обновляем существующую запись для пользователя в этом чате")
            cursor.execute('''
                UPDATE admins 
                SET can_see_users = ?, can_do_admin = ?, can_recom = ?, can_links = ?, can_dk = ?
                WHERE user_id = ? AND chat_id = ?
            ''', (
                int(action.view_users),
                int(action.grant_admin),
                int(action.manage_recommendations),
                int(action.manage_links),
                int(action.change_team_ranks),
                int(action.user_id),
                int(action.chat_id)
            ))
        else:
            # Вставляем новую запись
            print("Вставляем новую запись для пользователя в этом чате")
            cursor.execute('''
                INSERT INTO admins (user_id, chat_id, can_see_users, can_do_admin, can_recom, can_links, can_dk)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(action.user_id),
                int(action.chat_id),
                int(action.view_users),
                int(action.grant_admin),
                int(action.manage_recommendations),
                int(action.manage_links),
                int(action.change_team_ranks)
            ))
        
        connection.commit()
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



    return {
        "status": "success",
        "message": "Права успешно установлены",
        "data": {
            "chat_id": action.chat_id,
            "user_id": action.user_id,
            "permissions": {
                "view_users": action.view_users,
                "grant_admin": action.grant_admin,
                "manage_recommendations": action.manage_recommendations,
                "manage_links": action.manage_links,
                "change_team_ranks": action.change_team_ranks
            }
        }
    }

@app.get('/user_permissions/{chat_id}/{user_id}')
def get_user_permissions(chat_id: int, user_id: int):
    """
    Проверяет имеет ли пользователь какие-либо права в чате
    """
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Проверяем есть ли у пользователя права в этом чате
        cursor.execute('SELECT * FROM admins WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        admin_record = cursor.fetchone()
        
        connection.close()
        
        if admin_record:
            # Структура: user_id, chat_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk
            permissions = {
                "has_permissions": True,
                "can_see_users": bool(admin_record[3]) if len(admin_record) > 3 else False,
                "can_do_admin": bool(admin_record[4]) if len(admin_record) > 4 else False,
                "can_recom": bool(admin_record[5]) if len(admin_record) > 5 else False,
                "can_links": bool(admin_record[6]) if len(admin_record) > 6 else False,
                "can_dk": bool(admin_record[7]) if len(admin_record) > 7 else False
            }
        else:
            permissions = {
                "has_permissions": False,
                "can_see_users": False,
                "can_do_admin": False,
                "can_recom": False,
                "can_links": False,
                "can_dk": False
            }
        
        return {
            "status": "success",
            "data": permissions
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при проверке прав: {str(e)}"
        }

@app.post('/delete_permissions')
def delete_permissions(action: DeletePermissionsAction):
    """
    Удаляет все права пользователя для чата
    """
    print("="*50)
    print("Получен запрос на удаление прав:")
    print(f"Chat ID: {action.chat_id}")
    print(f"User ID: {action.user_id}")
    print("="*50)
    
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute('DELETE FROM admins WHERE user_id = ? AND chat_id = ?', (int(action.user_id), int(action.chat_id)))
        deleted = cursor.rowcount
        
        connection.commit()
        connection.close()
        
        print(f"Удалено записей: {deleted}")
        print("="*50)
        
        return {
            "status": "success",
            "message": "Права успешно удалены",
            "deleted": deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat_warns/{chat_id}")
async def get_chat_warns(chat_id: int):
    """
    Получает все предупреждения чата
    """
    try:
        chat_db_path = get_db_path(chat_id)
        
        if not os.path.exists(chat_db_path):
            return {"status": "error", "message": "База данных чата не найдена"}
        
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute("SELECT user_id, reason, moder_id, date FROM warns ORDER BY date DESC")
        warns = cursor.fetchall()
        
        warns_list = []
        for warn in warns:
            user_id = warn[0]
            reason = warn[1] if warn[1] else 'Без причины'
            moder_id = warn[2]
            date = warn[3]
            
            # Получаем имя пользователя
            try:
                cursor.execute("SELECT nik FROM users WHERE tg_id=?", (user_id,))
                user_result = cursor.fetchone()
                user_name = user_result[0] if user_result else f"ID: {user_id}"
            except:
                user_name = f"ID: {user_id}"
            
            # Получаем имя модератора
            try:
                cursor.execute("SELECT nik FROM users WHERE tg_id=?", (moder_id,))
                moder_result = cursor.fetchone()
                moder_name = moder_result[0] if moder_result else f"ID: {moder_id}"
            except:
                moder_name = f"ID: {moder_id}"
            
            warns_list.append({
                "user_id": user_id,
                "user_name": user_name,
                "reason": reason,
                "moder_id": moder_id,
                "moder_name": moder_name,
                "date": date
            })
        
        connection.close()
        return {"status": "success", "warns": warns_list, "count": len(warns_list)}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/snat_warn")
async def snat_warn(action: SnatWarnAction):
    """
    Снимает предупреждение с пользователя.
    
    Логика работы:
    1. Проверяет права админа в таблице admins
    2. Получает все предупреждения пользователя из таблицы warns
    3. Удаляет указанное предупреждение по номеру (1, 2 или 3)
    4. Сохраняет информацию о снятом предупреждении в таблицу warn_snat
    5. Возвращает успешный статус
    
    Параметры:
    - chat: ID чата (строка)
    - userid: ID пользователя (строка)
    - num: номер предупреждения для снятия (1, 2 или 3)
    - admin_id: ID админа, который снимает пред
    - admin_name: имя админа
    - admin_username: username админа
    """
    
    chat = action.chat
    userid = action.userid
    num = action.num
    admin_id = action.admin_id
    admin_name = action.admin_name
    admin_username = action.admin_username
    
    if admin_id == int(userid):
        raise HTTPException(status_code=400, detail="Нельзя снять предупреждение самому себе")
    
    # Проверка прав админа
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (admin_id,))
        admin_check = cursor.fetchall()
        
        if not admin_check:
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Получаем путь к базе данных чата
        chat_db_path = get_db_path(int(chat))
        
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Получаем все предупреждения пользователя, отсортированные по дате
        cursor.execute("SELECT * FROM warns WHERE user_id = ? ORDER BY date", (int(userid),))
        all_warns = cursor.fetchall()
        
        if not all_warns:
            raise HTTPException(status_code=404, detail="У пользователя нет предупреждений")
        
        if num > len(all_warns) or num < 1:
            raise HTTPException(status_code=400, detail=f"Неверный номер предупреждения. У пользователя {len(all_warns)} предупреждений")
        
        # Получаем предупреждение для удаления (num - 1, т.к. индексация с 0)
        warn_index = num - 1
        warn_to_delete = all_warns[warn_index]
        
        # Структура таблицы warns: user_id, reason, moder_id, date
        warn_reason = warn_to_delete[1] if warn_to_delete[1] else 'Без причины'
        warn_moder_id = warn_to_delete[2]
        warn_date = warn_to_delete[3]
        
        # Удаляем предупреждение
        cursor.execute(
            "DELETE FROM warns WHERE user_id = ? AND reason = ? AND moder_id = ? AND date = ?",
            (int(userid), warn_reason, warn_moder_id, warn_date)
        )
        
        # Формируем упоминание админа, который снимает пред
        admin_mention = f'<a href="tg://user?id={admin_id}">{admin_name}</a>'
        
        # Формируем информацию о модераторе, который выдал пред
        moder_give_info = f'ID: {warn_moder_id}'
        
        # Сохраняем в историю снятых предупреждений
        cursor.execute(
            'INSERT INTO warn_snat (user_id, warn_text, moder_give, moder_snat) VALUES (?, ?, ?, ?)',
            (int(userid), warn_reason, moder_give_info, admin_mention)
        )
        
        connection.commit()
        connection.close()
        
        # Получаем новое количество предупреждений
        cnt = len(all_warns) - 1
        
        return {
            "status": "ok",
            "message": f"Предупреждение #{num} успешно снято",
            "warns_left": cnt
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/dk-commands/{chat_id}")
def get_dk_commands(chat_id: int):
    """
    Получает список команд и их рангов доступа из таблицы dk в базе данных чата
    """
    try:
        # Получаем путь к базе данных конкретного чата
        # Убираем знак минус из ID чата для имени файла
        chat_id_str = str(abs(chat_id))
        chat_db_path = curent_path / 'databases' / f'{chat_id_str}.db'
        
        if not chat_db_path.exists():
            raise HTTPException(status_code=404, detail="База данных чата не найдена")
        
        connection = sqlite3.connect(chat_db_path)
        cursor = connection.cursor()
        
        # Проверяем существование таблицы dk
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dk'")
        if not cursor.fetchone():
            connection.close()
            return {"commands": []}
        
        # Получаем все команды и их ранги
        cursor.execute("SELECT comand, dk FROM dk ORDER BY dk ASC, comand ASC")
        dk_commands = cursor.fetchall()
        
        connection.close()
        
        # Словарь с названиями команд на русском
        command_names = {
            'ban': 'Блокировка пользователей',
            'mut': 'Ограничение пользователей',
            'warn': 'Предупреждение пользователей',
            'all': 'Созыв пользователей',
            'rang': 'Изменение ранга пользователей',
            'dk': 'Изменение доступа вызова команд',
            'change_pravils': 'Изменение правил чата',
            'close_chat': 'Изменение ограничений чата',
            'change_priv': 'Изменение приветствия чата',
            'obavlenie': 'Создание объявления',
            'tur': 'Создание турниров',
            'dell': 'Удаление сообщений',
            'period': 'Изменение периодов'
        }
        
        # Словарь с названиями рангов
        rank_names = {
            0: 'Доступно всем',
            1: 'Младший Модератор',
            2: 'Модератор',
            3: 'Старший Модератор',
            4: 'Заместитель',
            5: 'Менеджер',
            6: 'Владелец'
        }
        
        # Формируем результат
        commands = []
        for comand, dk in dk_commands:
            commands.append({
                'command': comand,
                'command_name': command_names.get(comand, comand),
                'required_rank': dk,
                'rank_name': rank_names.get(dk, f'Ранг {dk}')
            })
        
        return {"commands": commands}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

@app.get('/check_owner/{chat_id}/{user_id}')
def check_owner(chat_id: int, user_id: int):
    """
    Проверяет является ли пользователь владельцем чата
    """
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Проверяем есть ли пользователь в таблице creators (владельцы)
        cursor.execute('SELECT * FROM creators WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        creator_record = cursor.fetchone()
        
        connection.close()
        
        if creator_record:
            return {
                "status": "success",
                "is_owner": True,
                "message": "Пользователь является владельцем чата"
            }
        else:
            return {
                "status": "success", 
                "is_owner": False,
                "message": "Пользователь не является владельцем чата"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка при проверке владельца: {str(e)}"
        }

if  __name__ == '__main__':
    uvicorn.run('api:app', reload=True, port=3000, host="0.0.0.0", ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')
