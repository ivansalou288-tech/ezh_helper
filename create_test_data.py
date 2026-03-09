import sqlite3
import os

def create_test_admin_data():
    """Создает тестовые данные для админ панели"""
    
    # Проверяем существование базы admin.db
    if not os.path.exists('databases/admin.db'):
        print('Создаем базу данных admin.db...')
        conn = sqlite3.connect('databases/admin.db')
        cursor = conn.cursor()
        
        # Создаем таблицу admins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER,
                chat_id INTEGER,
                chat_name TEXT,
                can_see_users INTEGER DEFAULT 0,
                can_do_admin INTEGER DEFAULT 0,
                can_recom INTEGER DEFAULT 0,
                can_links INTEGER DEFAULT 0,
                can_dk INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, chat_id)
            )
        ''')
        
        # Добавляем тестовые данные
        test_data = [
            (123456789, -1001234567890, "Тестовый чат 1", 1, 1, 1, 0, 0),  # Полные права кроме links и dk
            (123456789, -1001234567891, "Тестовый чат 2", 1, 0, 0, 1, 1),  # Только просмотр, links и dk
            (123456789, -1001234567892, "Тестовый чат 3", 1, 1, 1, 1, 1),  # Все права
            (987654321, -1001234567890, "Тестовый чат 1", 1, 0, 0, 0, 0),  # Только просмотр для другого пользователя
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO admins 
            (user_id, chat_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        
        conn.commit()
        conn.close()
        print('Тестовые данные созданы успешно!')
    else:
        print('База admin.db уже существует')
    
    # Проверяем данные
    conn = sqlite3.connect('databases/admin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM admins')
    count = cursor.fetchone()[0]
    print(f'Всего записей в таблице admins: {count}')
    
    cursor.execute('SELECT * FROM admins WHERE user_id = 123456789')
    user_chats = cursor.fetchall()
    print(f'Чаты пользователя 123456789: {len(user_chats)}')
    for chat in user_chats:
        print(f'  - {chat[2]} (ID: {chat[1]})')
    
    conn.close()

if __name__ == '__main__':
    create_test_admin_data()
