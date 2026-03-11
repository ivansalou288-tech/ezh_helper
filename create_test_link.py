import sqlite3
import json

# Создаем таблицу и добавляем тестовую ссылку
conn = sqlite3.connect('databases/All.db')
cursor = conn.cursor()

# Создаем таблицу
cursor.execute('''CREATE TABLE IF NOT EXISTS links (
    chat_id INTEGER,
    link TEXT,
    activate_cnt INTEGER,
    target_chats TEXT
)''')

# Добавляем тестовую ссылку
test_code = "test123"
chat_id = 1002143434937  # Основной чат
target_chats = [1002143434937, -1001234567890]  # Основной + дополнительный чат
target_chats_json = json.dumps(target_chats)

cursor.execute('INSERT INTO links (chat_id, link, activate_cnt, target_chats) VALUES (?, ?, ?, ?)', 
               (chat_id, test_code, 10, target_chats_json))

conn.commit()

# Проверяем что добавилось
cursor.execute('SELECT link, chat_id, activate_cnt, target_chats FROM links')
rows = cursor.fetchall()

print('Созданные данные в таблице links:')
for row in rows:
    link, chat_id, activate_cnt, target_chats = row
    print(f'Код: {link}, Chat ID: {chat_id}, Активации: {activate_cnt}, Target chats: {target_chats}')
    
    # Распарсим target_chats
    if target_chats:
        try:
            parsed = json.loads(target_chats)
            print(f'  Распарсено: {parsed}')
        except:
            print(f'  Ошибка парсинга JSON')

conn.close()
print('\nТестовая ссылка создана! Код: test123')
