import sqlite3
import os

def check_database():
    """Проверяет структуру и данные базы admin.db"""
    
    if not os.path.exists('databases/admin.db'):
        print('База admin.db не найдена')
        return
    
    conn = sqlite3.connect('databases/admin.db')
    cursor = conn.cursor()
    
    # Проверяем структуру таблицы admins
    cursor.execute('PRAGMA table_info(admins)')
    columns = cursor.fetchall()
    print('Структура таблицы admins:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    print()
    
    # Проверяем наличие данных
    cursor.execute('SELECT COUNT(*) FROM admins')
    count = cursor.fetchone()[0]
    print(f'Всего записей в таблице admins: {count}')
    
    if count > 0:
        print('\nПример записей:')
        cursor.execute('SELECT * FROM admins LIMIT 5')
        rows = cursor.fetchall()
        for row in rows:
            print(f'  User: {row[0]}, Chat: {row[1]}, Name: {row[2]}')
            print(f'    Права: see_users={row[3]}, do_admin={row[4]}, recom={row[5]}, links={row[6]}, dk={row[7]}')
    
    print()
    
    # Проверяем уникальные пользователи и чаты
    cursor.execute('SELECT DISTINCT user_id FROM admins')
    users = cursor.fetchall()
    print(f'Уникальных пользователей: {len(users)}')
    
    cursor.execute('SELECT DISTINCT chat_id FROM admins')
    chats = cursor.fetchall()
    print(f'Уникальных чатов: {len(chats)}')
    
    conn.close()

if __name__ == '__main__':
    check_database()
