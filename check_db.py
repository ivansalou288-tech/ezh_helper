import sqlite3
from pathlib import Path

curent_path = Path('.')
chat_db_path = curent_path / 'databases' / '1003012971064.db'

if chat_db_path.exists():
    connection = sqlite3.connect(chat_db_path)
    cursor = connection.cursor()
    
    # Проверяем существование таблицы dk
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dk'")
    table_exists = cursor.fetchone()
    print(f'Table dk exists: {table_exists is not None}')
    
    if table_exists:
        cursor.execute('SELECT * FROM dk LIMIT 5')
        dk_data = cursor.fetchall()
        print(f'DK data: {dk_data}')
    else:
        print('Table dk does not exist')
        
    # Показываем все таблицы в базе
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f'All tables: {[t[0] for t in tables]}')
    
    connection.close()
else:
    print('Database file does not exist')
