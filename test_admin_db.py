import sqlite3
import os

# Проверяем существование базы admin.db
if os.path.exists('databases/admin.db'):
    print('База admin.db существует')
    conn = sqlite3.connect('databases/admin.db')
    cursor = conn.cursor()
    
    # Проверяем структуру таблицы admins
    cursor.execute('PRAGMA table_info(admins)')
    columns = cursor.fetchall()
    print('Структура таблицы admins:')
    for col in columns:
        print(f'  {col[1]} - {col[2]}')
    
    # Проверяем наличие данных
    cursor.execute('SELECT COUNT(*) FROM admins')
    count = cursor.fetchone()[0]
    print(f'Записей в таблице admins: {count}')
    
    # Показываем несколько записей для примера
    if count > 0:
        cursor.execute('SELECT * FROM admins LIMIT 3')
        rows = cursor.fetchall()
        print('Пример записей:')
        for row in rows:
            print(f'  User: {row[0]}, Chat: {row[1]}, Name: {row[2]}')
    
    conn.close()
else:
    print('База admin.db не найдена')
