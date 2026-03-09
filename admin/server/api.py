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

from main.config3 import *
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

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
if  __name__ == '__main__':
    uvicorn.run('api:app', reload=True,port=3000, host="0.0.0.0", ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')
