from math import log
import sqlite3
import os
import ssl
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

def get_db_path(chat_id):
    """Получает путь к базе данных чата"""
    chat_id_str = str(-chat_id)
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

        # Пытаемся получить статус участника в чате; если его больше нет в чате,
        # Telegram может вернуть ошибку "member not found" — тогда используем ранг
        chat_status = '� Состоит в чате'  # по умолчанию считаем, что состоит
        
        if bot:
            try:
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
                    
            except Exception as e:
                # При любой ошибке используем ранг из базы данных
                # Это исправляет проблему, когда у многих статус "не состоит"
                if rang and rang >= 5:
                    chat_status = '👨🏻‍🔧 Телеграм-админ этого чата'
                elif rang and rang >= 3:
                    chat_status = '💚 Состоит в чате'
                else:
                    chat_status = '💚 Состоит в чате'
        else:
            # Бот недоступен, используем ранг для определения статуса
            if rang and rang >= 5:
                chat_status = '👨🏻‍🔧 Телеграм-админ этого чата'
            elif rang and rang >= 3:
                chat_status = '💚 Состоит в чате'
            else:
                chat_status = '💚 Состоит в чате'

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
        cursor.execute('SELECT * FROM admins WHERE user_id = ? AND chat_id = ?', (action.user_id, action.chat_id))
        existing = cursor.fetchone()
        
        if existing:
            # Обновляем существующую запись
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

    

if  __name__ == '__main__':
    uvicorn.run('api:app', reload=True, port=3000, host="0.0.0.0", ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')
