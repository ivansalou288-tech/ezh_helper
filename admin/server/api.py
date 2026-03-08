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

class ChatAdminCreate(BaseModel):
    user_id: int
    permissions: list[str]

class ChatAdminUpdate(BaseModel):
    permissions: list[str]
    is_active: Optional[bool] = None

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
    
    # Таблица администраторов чатов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            is_active BOOLEAN DEFAULT 1,
            UNIQUE(chat_id, user_id)
        )
    ''')
    
    # Таблица прав администраторов чатов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_admin_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_admin_id INTEGER NOT NULL,
            permission_name TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_admin_id) REFERENCES chat_admins (id) ON DELETE CASCADE,
            UNIQUE(chat_admin_id, permission_name)
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
    
    if not user_data:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Временно разрешаем доступ для тестирования (супер-админ)
    # В реальном приложении здесь должна быть проверка на глобального админа
    if user_data['id'] != 817325514:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        'id': user_data['id'],
        'first_name': user_data.get('first_name', 'Admin'),
        'is_super_admin': True
    }

# Проверка прав админа конкретного чата
async def verify_chat_admin(chat_id: int, request: Request):
    user_data = None
    try:
        # Получаем данные из Telegram WebApp init data
        init_data = request.headers.get('X-Telegram-Init-Data', '')
        if init_data:
            for param in init_data.split('&'):
                if param.startswith('user='):
                    user_data = json.loads(param[5:].replace('%22', '"').replace('%20', ' '))
                    break
    except:
        pass
    
    if not user_data:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Проверяем, является ли пользователь администратором чата
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'databases', 'admin.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ca.id, ca.role, ca.is_active 
        FROM chat_admins ca 
        WHERE ca.chat_id = ? AND ca.user_id = ?
    ''', (chat_id, user_data['id']))
    
    admin_data = cursor.fetchone()
    
    if not admin_data or not admin_data[2]:
        conn.close()
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем права администратора чата
    cursor.execute('''
        SELECT permission_name FROM chat_admin_permissions 
        WHERE chat_admin_id = ? AND enabled = 1
    ''', (admin_data[0],))
    
    permissions = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return {
        'id': user_data['id'],
        'first_name': user_data.get('first_name', 'Admin'),
        'chat_admin_id': admin_data[0],
        'role': admin_data[1],
        'permissions': permissions
    }

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

# Проверка прав доступа
def check_permission(user_permissions: list[str], required_permission: str) -> bool:
    return required_permission in user_permissions

@app.get("/api/chats/{chat_id}/admins")
async def get_chat_admins(chat_id: int, request: Request, current_user: dict = Depends(verify_admin)):
    """Получение списка администраторов чата"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'databases', 'admin.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ca.id, ca.user_id, ca.role, ca.is_active, ca.created_at,
                   GROUP_CONCAT(cap.permission_name, ',') as permissions
            FROM chat_admins ca
            LEFT JOIN chat_admin_permissions cap ON ca.id = cap.chat_admin_id AND cap.enabled = 1
            WHERE ca.chat_id = ?
            GROUP BY ca.id
            ORDER BY ca.created_at DESC
        ''', (chat_id,))
        
        admins = []
        for row in cursor.fetchall():
            admin_data = {
                'id': row[0],
                'user_id': row[1],
                'role': row[2],
                'is_active': bool(row[3]),
                'created_at': row[4],
                'permissions': row[5].split(',') if row[5] else []
            }
            admins.append(admin_data)
        
        conn.close()
        return {'admins': admins}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chats/{chat_id}/admins")
async def create_chat_admin(chat_id: int, admin_data: ChatAdminCreate, request: Request, current_user: dict = Depends(verify_admin)):
    """Создание нового администратора чата"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'databases', 'admin.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, не существует ли уже такой администратор в чате
        cursor.execute('SELECT id FROM chat_admins WHERE chat_id = ? AND user_id = ?', (chat_id, admin_data.user_id))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Admin already exists in this chat")
        
        # Создаем администратора чата
        cursor.execute('''
            INSERT INTO chat_admins (chat_id, user_id, role, created_by) VALUES (?, ?, ?, ?)
        ''', (chat_id, admin_data.user_id, 'admin', current_user['id']))
        
        chat_admin_id = cursor.lastrowid
        
        # Добавляем права
        for permission in admin_data.permissions:
            cursor.execute('''
                INSERT OR IGNORE INTO chat_admin_permissions (chat_admin_id, permission_name, enabled) VALUES (?, ?, ?)
            ''', (chat_admin_id, permission, 1))
        
        conn.commit()
        conn.close()
        
        return {'message': 'Chat admin created successfully', 'admin_id': chat_admin_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/chats/{chat_id}/admins/{admin_id}")
async def update_chat_admin(chat_id: int, admin_id: int, admin_data: ChatAdminUpdate, request: Request, current_user: dict = Depends(verify_admin)):
    """Обновление администратора чата"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'databases', 'admin.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существование администратора в чате
        cursor.execute('SELECT id FROM chat_admins WHERE id = ? AND chat_id = ?', (admin_id, chat_id))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Chat admin not found")
        
        # Обновляем статус активности если указан
        if admin_data.is_active is not None:
            cursor.execute('UPDATE chat_admins SET is_active = ? WHERE id = ?', (admin_data.is_active, admin_id))
        
        # Обновляем права
        cursor.execute('DELETE FROM chat_admin_permissions WHERE chat_admin_id = ?', (admin_id,))
        for permission in admin_data.permissions:
            cursor.execute('''
                INSERT INTO chat_admin_permissions (chat_admin_id, permission_name, enabled) VALUES (?, ?, ?)
            ''', (admin_id, permission, 1))
        
        conn.commit()
        conn.close()
        
        return {'message': 'Chat admin updated successfully'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chats/{chat_id}/admins/{admin_id}")
async def delete_chat_admin(chat_id: int, admin_id: int, request: Request, current_user: dict = Depends(verify_admin)):
    """Удаление администратора чата"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'databases', 'admin.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, не пытается ли пользователь удалить себя
        cursor.execute('SELECT user_id FROM chat_admins WHERE id = ? AND chat_id = ?', (admin_id, chat_id))
        admin_user = cursor.fetchone()
        if admin_user and admin_user[0] == current_user['id']:
            conn.close()
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        # Удаляем администратора чата (каскадно удалятся и права)
        cursor.execute('DELETE FROM chat_admins WHERE id = ? AND chat_id = ?', (admin_id, chat_id))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Chat admin not found")
        
        conn.commit()
        conn.close()
        
        return {'message': 'Chat admin deleted successfully'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat-admin/permissions")
async def get_available_permissions(request: Request, current_user: dict = Depends(verify_admin)):
    """Получение списка доступных прав для администраторов чатов"""
    permissions = [
        {'name': 'send_messages', 'display_name': 'Отправка сообщений от имени бота'},
        {'name': 'moderate_messages', 'display_name': 'Модерация сообщений'},
        {'name': 'manage_settings', 'display_name': 'Управление настройками чата'},
        {'name': 'view_statistics', 'display_name': 'Просмотр статистики'},
        {'name': 'manage_admins', 'display_name': 'Управление администраторами'},
        {'name': 'ban_users', 'display_name': 'Блокировка пользователей'}
    ]
    
    return {'permissions': permissions}

# Раздача статики
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    init_admin_db()
    uvicorn.run(app, host="0.0.0.0", port=3000, ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')

