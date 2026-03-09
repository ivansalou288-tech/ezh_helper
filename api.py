from math import log
import sqlite3
import os
import ssl
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
import asyncio
from datetime import datetime
import password_generator
from typing import Any, Optional
import time
import json

import sys
import os

# Добавляем корневую директорию проекта в путь
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from main.config3 import *
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
curent_path = (Path(__file__)).parent
all_path = curent_path / 'databases' / 'All.db'
admin_path = curent_path / 'databases' / 'admin.db'
app = FastAPI()

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
            
            if photo:
                # Ищем фото в разных размерах
                avatar_file_id = None
                
                # Проверяем все возможные размеры фото
                for size_key in ["big", "small", "thumb"]:
                    if size_key in photo:
                        avatar_file_id = photo[size_key].get("file_id")
                        print(f"DEBUG: Found {size_key} photo with file_id: {avatar_file_id}")
                        break
                
                if avatar_file_id:
                    # Получаем URL файла
                    file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={avatar_file_id}"
                    file_response = requests.get(file_url)
                    file_data = file_response.json()
                    
                    print(f"DEBUG: File response: {file_data}")
                    
                    if file_data.get("ok"):
                        file_path = file_data["result"]["file_path"]
                        avatar_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                        
                        print(f"DEBUG: Final avatar URL: {avatar_url}")
                        
                        return {
                            "status": "success",
                            "avatar_url": avatar_url
                        }
        
        # Если фото нет или произошла ошибка, возвращаем пустой результат
        print("DEBUG: No photo found, returning None")
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

if  __name__ == '__main__':
    uvicorn.run('api:app', reload=True,port=3000, host="0.0.0.0", ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')
