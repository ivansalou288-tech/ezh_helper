#!/usr/bin/env python3
"""
Тестовый скрипт для проверки структуры базы данных
"""

import sqlite3
from pathlib import Path

curent_path = Path(__file__).parent
warn_list_path = curent_path / 'databases' / 'warn_list.db'

def check_old_database():
    """Проверяет структуру старой базы данных"""
    
    print("=== ПРОВЕРКА СТАРОЙ БАЗЫ ДАННЫХ ===\n")
    
    if not warn_list_path.exists():
        print(f"ОШИБКА: База данных не найдена: {warn_list_path}")
        return
    
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

if __name__ == "__main__":
    check_old_database()
