import sqlite3
from pathlib import Path

# Пути к базам данных
curent_path = Path.cwd()
warn_list_path = curent_path / 'databases' / 'warn_list.db'

print("=== ПРОВЕРКА СТАРОЙ БАЗЫ ДАННЫХ ===")
print(f"Путь к базе: {warn_list_path}")
print(f"Файл существует: {warn_list_path.exists()}")

if warn_list_path.exists():
    try:
        connection = sqlite3.connect(warn_list_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Найдено таблиц: {len(tables)}")
        
        for table_info in tables:
            table_name = table_info[0]
            print(f"\n--- Таблица: {table_name} ---")
            
            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Структура:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Количество записей: {count}")
            
            # Показываем несколько примеров данных
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()
            
            if sample_data:
                print("Примеры данных:")
                for i, row in enumerate(sample_data, 1):
                    print(f"  {i}: {row}")
        
        connection.close()
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
