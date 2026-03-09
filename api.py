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
curent_path = (Path(__file__)).parent
all_path = curent_path / 'databases' / 'All.db'
admin_path = curent_path / 'databases' / 'admin.db'
app = FastAPI()

def get_db_path(chat_id):
    """Получает путь к базе данных чата"""
    chat_id_str = str(chat_id)

    return curent_path / 'databases' / f'{-chat_id_str}.db'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/user-admin-chats/{user_id}')
def get_user_admin_chats(user_id: int):
    """
    Получает список чатов, где пользователь имеет админские права
    """
    try:
        connection = sqlite3.connect(admin_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Получаем все записи для пользователя из таблицы admins
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        
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
        print(f"Error getting user admin chats: {e}")
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
        
        print(f"DEBUG: Getting avatar for chat_id: {chat_id}")
        
        # Получаем информацию о чате через Bot API
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {"chat_id": chat_id}
        
        response = requests.get(url, params=params)
        data = response.json()
        
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response data: {data}")
        
        if data.get("ok"):
            chat_info = data.get("result", {})
            photo = chat_info.get("photo")
            
            print(f"DEBUG: Photo data: {photo}")
            print(f"DEBUG: Photo keys: {list(photo.keys()) if photo else 'None'}")
            
            if photo:
                # Ищем фото в разных размерах
                avatar_file_id = None
                
                # Проверяем все возможные размеры фото
                if "big_file_id" in photo:
                    avatar_file_id = photo["big_file_id"]
                    print(f"DEBUG: Found big_file_id: {avatar_file_id}")
                elif "small_file_id" in photo:
                    avatar_file_id = photo["small_file_id"]
                    print(f"DEBUG: Found small_file_id: {avatar_file_id}")
                elif "file_id" in photo:
                    avatar_file_id = photo["file_id"]
                    print(f"DEBUG: Found file_id: {avatar_file_id}")
                
                if avatar_file_id:
                    # Получаем URL файла
                    file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={avatar_file_id}"
                    print(f"DEBUG: Requesting file from: {file_url}")
                    
                    file_response = requests.get(file_url)
                    file_data = file_response.json()
                    
                    print(f"DEBUG: File response status: {file_response.status_code}")
                    print(f"DEBUG: File response data: {file_data}")
                    
                    if file_data.get("ok"):
                        file_path = file_data["result"]["file_path"]
                        avatar_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                        
                        print(f"DEBUG: Final avatar URL: {avatar_url}")
                        
                        return {
                            "status": "success",
                            "avatar_url": avatar_url
                        }
                    else:
                        print(f"DEBUG: getFile failed: {file_data}")
                else:
                    print("DEBUG: No file_id found in photo data")
            
        # Если фото нет или произошла ошибка, возвращаем пустой результат
        print("DEBUG: No photo found or getFile failed, returning None")
        return {
            "status": "success",
            "avatar_url": None
        }
        
    except Exception as e:
        print(f"ERROR: Exception in get_chat_avatar: {e}")
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
        print(f"Error getting chat admin panel: {e}")
        return {
            "status": "error",
            "message": f"Ошибка при загрузке админ панели: {str(e)}"
        }

@app.get('/chat-users/{chat_id}')
def get_chat_users(chat_id: int):
    """
    Получает список пользователей чата
    """
    try:
        print(f"Запрос пользователей для чата: {chat_id}")
        
        # Получаем путь к базе данных чата
        chat_db_path = get_db_path(chat_id)
        print(f"Путь к БД: {chat_db_path}")
        
        if not os.path.exists(chat_db_path):
            print(f"База данных не найдена: {chat_db_path}")
            return {
                "status": "error",
                "message": "База данных чата не найдена"
            }
        
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Сначала проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        print(f"Доступные колонки: {column_names}")
        
        # Упрощенный запрос - получаем только то, что точно есть
        cursor.execute('''
            SELECT tg_id, nik, rang, date_vhod, last_date 
            FROM users 
            ORDER BY rang DESC, nik
        ''')
        users = cursor.fetchall()
        print(f"Найдено пользователей: {len(users)}")
        
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
        
        print(f"Возвращаем {len(users_list)} пользователей")
        return {
            "status": "success",
            "users": users_list,
            "count": len(users_list)
        }
        
    except Exception as e:
        print(f"Ошибка в get_chat_users: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Ошибка при получении пользователей: {str(e)}"
        }

if  __name__ == '__main__':
    uvicorn.run('api:app', reload=True,port=3000, host="0.0.0.0", ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')
