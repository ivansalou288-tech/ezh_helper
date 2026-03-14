import sqlite3
from pathlib import Path

def check_databases():
    """Проверяет структуру баз данных"""
    
    # Пути к базам данных
    curent_path = Path(__file__).parent
    warn_list_path = curent_path / 'databases' / 'warn_list.db'
    databases_path = curent_path / 'databases'
    
    print("=== ПРОВЕРКА БАЗ ДАННЫХ ===\n")
    
    # Проверяем старую базу
    print("1. СТАРАЯ БАЗА (warn_list.db):")
    if warn_list_path.exists():
        try:
            conn = sqlite3.connect(warn_list_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"   Найдено таблиц: {len(tables)}")
            
            for table in tables:
                table_name = table[0]
                print(f"   Таблица: {table_name}")
                
                # Получаем структуру
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"   Поля: {[col[1] for col in columns]}")
                
                # Количество записей
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cursor.fetchone()[0]
                print(f"   Записей: {count}")
                
                # Пример данных
                if count > 0:
                    cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 2')
                    sample = cursor.fetchall()
                    print(f"   Пример: {sample[0] if sample else 'Нет данных'}")
                print()
            
            conn.close()
            
        except Exception as e:
            print(f"   ОШИБКА: {e}\n")
    else:
        print("   Файл не найден\n")
    
    # Проверяем новые базы
    print("2. НОВЫЕ БАЗЫ (чатов):")
    
    chat_ids = [1002143434937, 1002274082016, 1002439682589, 1003012971064]  # Все чаты
    
    for chat_id in chat_ids:
        db_path = databases_path / f'{chat_id}.db'  # Без минуса
        print(f"   Чат {chat_id}:")
        
        if db_path.exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                print(f"     Найдено таблиц: {len(tables)}")
                
                for table in tables:
                    table_name = table[0]
                    if table_name == 'warns':
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        print(f"     Таблица warns: {[col[1] for col in columns]}")
                        
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"     Записей в warns: {count}")
                        
                        # Показываем пример данных
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                            sample = cursor.fetchall()
                            print(f"     Пример: {sample[0] if sample else 'Нет данных'}")
                
                conn.close()
                
            except Exception as e:
                print(f"     ОШИБКА: {e}")
        else:
            print("     Файл не найден")
        print()

if __name__ == "__main__":
    check_databases()
