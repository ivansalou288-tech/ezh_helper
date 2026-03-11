import sqlite3

# Создаем тестовую запись администратора
conn = sqlite3.connect('databases/admin.db')
cursor = conn.cursor()

# Создаем таблицу если не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER,
    chat_id INTEGER,
    chat_name TEXT,
    can_see_users INTEGER,
    can_do_admin INTEGER,
    can_recom INTEGER,
    can_links INTEGER,
    can_dk INTEGER
)''')

# Добавляем тестового администратора
test_user_id = 123456789
test_chat_id = 1002143434937

cursor.execute('''
    INSERT OR REPLACE INTO admins 
    (user_id, chat_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (test_user_id, test_chat_id, 'Test Chat', 1, 1, 0, 1, 0))

conn.commit()

# Проверяем что добавилось
cursor.execute('SELECT * FROM admins WHERE user_id = ? AND chat_id = ?', (test_user_id, test_chat_id))
result = cursor.fetchone()

print(f"Тестовый администратор создан:")
print(f"User ID: {result[0]}")
print(f"Chat ID: {result[1]}")
print(f"Права: see_users={result[3]}, do_admin={result[4]}, can_recom={result[5]}, can_links={result[6]}, can_dk={result[7]}")

conn.close()
print("\nТеперь пользователь 123456789 имеет права в чате 1002143434937")
