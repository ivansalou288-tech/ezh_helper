import sqlite3

# Проверим что код есть в базе
conn = sqlite3.connect('databases/All.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM links WHERE link = ?', ('test123',))
rows = cursor.fetchall()

print(f"Найдено записей с кодом 'test123': {len(rows)}")
for row in rows:
    print(f"Полная запись: {row}")

conn.close()
