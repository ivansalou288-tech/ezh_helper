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
    conn = sqlite3.connect('databases/admin.db')
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
    
    if not user_data or user_data.get('id') not in [817325514]:  # ID админа
        raise HTTPException(status_code=403, detail="Access denied")
    
    return user_data

@app.get("/api/chats")
async def get_admin_chats(request: Request, current_user: dict = Depends(verify_admin)):
    """Получение списка чатов доступных админу"""
    try:
        conn = sqlite3.connect('databases/admin.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chat_id, chat_title, chat_username, member_count, last_activity
            FROM admin_chats 
            WHERE is_active = 1
            ORDER BY last_activity DESC NULLS LAST
        ''')
        
        chats = []
        for row in cursor.fetchall():
            chats.append({
                'chat_id': row[0],
                'chat_title': row[1],
                'chat_username': row[2],
                'member_count': row[3],
                'last_activity': row[4]
            })
        
        conn.close()
        return {'chats': chats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chats/{chat_id}/add")
async def add_chat_to_admin(chat_id: int, request: Request, current_user: dict = Depends(verify_admin)):
    """Добавление чата в список доступных админу"""
    try:
        # Получаем информацию о чате из основной БД
        chat_db_path = f'databases/{-chat_id}.db'
        if not os.path.exists(chat_db_path):
            raise HTTPException(status_code=404, detail="Chat database not found")
        
        conn = sqlite3.connect(chat_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        member_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Добавляем в админскую таблицу
        admin_conn = sqlite3.connect('databases/admin.db')
        cursor = admin_conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO admin_chats 
            (chat_id, chat_title, member_count, last_activity)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, f"Chat {chat_id}", member_count, datetime.now().isoformat()))
        
        admin_conn.commit()
        admin_conn.close()
        
        return {'status': 'success'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Раздача статики
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    init_admin_db()
    uvicorn.run(app, host="0.0.0.0", port=3000, ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')

