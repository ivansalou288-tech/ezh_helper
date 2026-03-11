import sqlite3
import json

# Проверим что есть в таблице links
conn = sqlite3.connect('databases/All.db')
cursor = conn.cursor()
cursor.execute('SELECT link, chat_id, activate_cnt, target_chats FROM links LIMIT 5')
rows = cursor.fetchall()

print('Данные в таблице links:')
for row in rows:
    link, chat_id, activate_cnt, target_chats = row
    print(f'Код: {link}, Chat ID: {chat_id}, Активации: {activate_cnt}, Target chats: {target_chats}')
    
    # Попробуем распарсить target_chats
    if target_chats:
        try:
            parsed = json.loads(target_chats)
            print(f'  Распарсено: {parsed}')
        except:
            print(f'  Ошибка парсинга JSON')

conn.close()
