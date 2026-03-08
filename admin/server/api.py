from math import log
import sqlite3
import os
import ssl
import sys
from fastapi import FastAPI, HTTPException, Request, Depends
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

app = FastAPI()

# Добавление CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Модели данных
class ChatInfo(BaseModel):
    chat_id: int
    chat_title: str
    chat_username: Optional[str] = None
    member_count: int
    last_activity: Optional[str] = None

# Инициализация базы данных для админ-панели
def init_admin_db():
    # Используем абсолютный путь для базы данных
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'databases', 'admin.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_chats (
            chat_id INTEGER PRIMARY KEY,
            chat_title TEXT NOT NULL,
            chat_username TEXT,
            member_count INTEGER DEFAULT 0,
            last_activity TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Проверка прав админа
async def verify_admin(request: Request):
    user_data = None
    try:
        # Получаем данные из Telegram WebApp init data
        init_data = request.headers.get('X-Telegram-Init-Data', '')
        if init_data:
            # Простая проверка (в реальном приложении нужна валидация подписи)
            for param in init_data.split('&'):
                if param.startswith('user='):
                    user_data = json.loads(param[5:].replace('%22', '"').replace('%20', ' '))
                    break
    except:
        pass
    
    # Временно разрешаем доступ для тестирования
    # В реальном приложении нужно раскомментировать проверку
    # if not user_data or user_data.get('id') not in [817325514]:  # ID админа
    #     raise HTTPException(status_code=403, detail="Access denied")
    
    return user_data or {'id': 817325514, 'first_name': 'Admin'}  # Временный заглушечный пользователь

@app.get("/api/chats")
async def get_admin_chats(request: Request, current_user: dict = Depends(verify_admin)):
    """Получение списка чатов доступных админу"""
    try:
        # Используем абсолютный путь для базы данных
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'databases', 'admin.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chat_id, chat_title, chat_username, member_count, last_activity
            FROM admin_chats 
            WHERE is_active = 1
            ORDER BY last_activity DESC NULLS LAST
        ''')
        
        chats = []
        for row in cursor.fetchall():
            chat_data = {
                'chat_id': row[0],
                'chat_title': row[1],
                'chat_username': row[2],
                'member_count': row[3],
                'last_activity': row[4],
                'chat_photo_url': None
            }
            
            # Получаем фото чата через Telegram Bot API
            try:
                import requests
                bot_token = '8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q'
                
                # Получаем информацию о чате
                chat_info_url = f"https://api.telegram.org/bot{bot_token}/getChat"
                chat_data_request = {'chat_id': row[0]}
                
                response = requests.post(chat_info_url, json=chat_data_request, timeout=5)
                if response.status_code == 200:
                    chat_info = response.json().get('result', {})
                    
                    # Получаем фото чата если есть
                    if chat_info.get('photo'):
                        # Получаем фото через getFile
                        get_file_url = f"https://api.telegram.org/bot{bot_token}/getFile"
                        file_data = {'file_id': chat_info['photo']['small_file_id']}
                        
                        file_response = requests.post(get_file_url, json=file_data, timeout=5)
                        if file_response.status_code == 200:
                            file_info = file_response.json().get('result', {})
                            file_path = file_info.get('file_path')
                            if file_path:
                                chat_data['chat_photo_url'] = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                                
            except Exception as e:
                print(f"Error getting chat photo for {row[0]}: {e}")
                # Если не удалось получить фото, оставляем None
            
            chats.append(chat_data)
        
        conn.close()
        return {'chats': chats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Раздача статики
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    init_admin_db()
    uvicorn.run(app, host="0.0.0.0", port=3000, ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')

