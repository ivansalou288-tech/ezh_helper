#!/usr/bin/env python3
"""
Скрипт для переноса предупреждений из старой системы в новую

Старая система: warn_list.db с таблицами (-chat_id)
Поля: tg_id, warns_count, first_warn, second_warn, therd_warn, first_moder, second_moder, therd_moder

Новая система: (-chat_id).db с таблицей warns
Поля: user_id, reason, moder_id, date
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Пути к базам данных
curent_path = Path(__file__).parent
warn_list_path = curent_path / 'databases' / 'warn_list.db'
databases_path = curent_path / 'databases'

# Словарь с именами чатов
chats_names = {
    'klan': 1002143434937, 
    'sost-1': 1002274082016, 
    'sost-2': 1002439682589
}

def migrate_warnings():
    """Переносит предупреждения из старой системы в новую"""
    
    print("=== НАЧАЛО МИГРАЦИИ ПРЕДУПРЕЖДЕНИЙ ===\n")
    
    # Проверяем существование старой базы данных
    if not warn_list_path.exists():
        print(f"ОШИБКА: Старая база данных не найдена: {warn_list_path}")
        return
    
    try:
        # Подключаемся к старой базе данных
        old_connection = sqlite3.connect(warn_list_path, check_same_thread=False)
        old_cursor = old_connection.cursor()
        
        # Получаем список всех таблиц (чатов) в старой базе
        old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = old_cursor.fetchall()
        
        print(f"Найдено таблиц в старой базе: {len(tables)}")
        
        total_migrated = 0
        total_errors = 0
        
        for table_info in tables:
            table_name = table_info[0]
            
            # Пропускаем служебные таблицы
            if not table_name.startswith('-'):
                continue
            
            # Извлекаем chat_id из имени таблицы
            try:
                chat_id = int(table_name[1:])  # Убираем первый символ '-'
                print(f"\n--- Обработка чата {table_name} (ID: {chat_id}) ---")
                
                # Получаем все предупреждения из старой таблицы
                old_cursor.execute(f"SELECT * FROM {table_name}")
                warnings = old_cursor.fetchall()
                
                print(f"Найдено пользователей с предупреждениями: {len(warnings)}")
                
                # Путь к новой базе данных чата
                new_db_path = databases_path / f'{table_name}.db'
                
                if not new_db_path.exists():
                    print(f"ПРЕДУПРЕЖДЕНИЕ: Новая база данных не найдена: {new_db_path}")
                    total_errors += 1
                    continue
                
                # Подключаемся к новой базе данных
                new_connection = sqlite3.connect(new_db_path, check_same_thread=False)
                new_cursor = new_connection.cursor()
                
                # Проверяем существование таблицы warns
                new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='warns';")
                if not new_cursor.fetchone():
                    print(f"ОШИБКА: Таблица 'warns' не найдена в {new_db_path}")
                    new_connection.close()
                    total_errors += 1
                    continue
                
                migrated_count = 0
                
                for warning in warnings:
                    tg_id = warning[0]
                    warns_count = warning[1]
                    first_warn = warning[2]
                    second_warn = warning[3]
                    therd_warn = warning[4]
                    first_moder = warning[5]
                    second_moder = warning[6]
                    therd_moder = warning[7]
                    
                    # Переносим каждое предупреждение
                    warn_data = [
                        (first_warn, first_moder, 1),
                        (second_warn, second_moder, 2),
                        (therd_warn, therd_moder, 3)
                    ]
                    
                    for warn_text, moder_id, warn_num in warn_data:
                        if warn_text and warn_text.strip():  # Пропускаем пустые предупреждения
                            try:
                                # Вставляем в новую таблицу
                                current_date = datetime.now().strftime('%d.%m.%Y')
                                new_cursor.execute(
                                    "INSERT INTO warns (user_id, reason, moder_id, date) VALUES (?, ?, ?, ?)",
                                    (tg_id, warn_text, int(moder_id) if moder_id and moder_id.isdigit() else 0, current_date)
                                )
                                migrated_count += 1
                                print(f"  ✓ Перенесено предупреждение #{warn_num} для пользователя {tg_id}")
                            except Exception as e:
                                print(f"  ✗ Ошибка при переносе предупреждения #{warn_num} для пользователя {tg_id}: {e}")
                                total_errors += 1
                
                # Сохраняем изменения
                new_connection.commit()
                new_connection.close()
                
                print(f"Перенос предупреждений для чата {chat_id} завершен: {migrated_count} записей")
                total_migrated += migrated_count
                
            except ValueError as e:
                print(f"ОШИБКА: Не удалось извлечь chat_id из имени таблицы {table_name}: {e}")
                total_errors += 1
            except Exception as e:
                print(f"ОШИБКА при обработке таблицы {table_name}: {e}")
                total_errors += 1
        
        old_connection.close()
        
        print(f"\n=== МИГРАЦИЯ ЗАВЕРШЕНА ===")
        print(f"Всего перенесено предупреждений: {total_migrated}")
        print(f"Всего ошибок: {total_errors}")
        
        if total_errors == 0:
            print("✓ Миграция прошла успешно!")
        else:
            print(f"⚠ Миграция завершена с {total_errors} ошибками")
            
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")

def check_migration():
    """Проверяет результаты миграции"""
    
    print("\n=== ПРОВЕРКА РЕЗУЛЬТАТОВ МИГРАЦИИ ===\n")
    
    for chat_name, chat_id in chats_names.items():
        print(f"--- Проверка чата {chat_name} (ID: {chat_id}) ---")
        
        # Старая база
        old_db_path = databases_path / 'warn_list.db'
        if old_db_path.exists():
            try:
                old_connection = sqlite3.connect(old_db_path, check_same_thread=False)
                old_cursor = old_connection.cursor()
                
                table_name = f"-{chat_id}"
                old_cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE warns_count > 0")
                old_count = old_cursor.fetchone()[0]
                
                old_cursor.execute(f"SELECT SUM(warns_count) FROM {table_name}")
                old_total = old_cursor.fetchone()[0] or 0
                
                old_connection.close()
                
                print(f"  Старая система: {old_count} пользователей, {old_total} предупреждений")
            except Exception as e:
                print(f"  Ошибка проверки старой базы: {e}")
        
        # Новая база
        new_db_path = databases_path / f'-{chat_id}.db'
        if new_db_path.exists():
            try:
                new_connection = sqlite3.connect(new_db_path, check_same_thread=False)
                new_cursor = new_connection.cursor()
                
                new_cursor.execute("SELECT COUNT(*) FROM warns")
                new_count = new_cursor.fetchone()[0]
                
                new_cursor.execute("SELECT COUNT(DISTINCT user_id) FROM warns")
                new_users = new_cursor.fetchone()[0]
                
                new_connection.close()
                
                print(f"  Новая система: {new_users} пользователей, {new_count} предупреждений")
            except Exception as e:
                print(f"  Ошибка проверки новой базы: {e}")
        
        print()

if __name__ == "__main__":
    print("Скрипт миграции предупреждений")
    print("------------------------------")
    
    # Запрашиваем подтверждение
    response = input("Выполнить миграцию? (y/n): ").lower().strip()
    
    if response in ['y', 'yes', 'да']:
        migrate_warnings()
        
        # Запрашиваем проверку
        response = input("\nВыполнить проверку результатов? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'да']:
            check_migration()
    else:
        print("Миграция отменена")
