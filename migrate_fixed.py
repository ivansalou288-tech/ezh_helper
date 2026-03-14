import sqlite3
from pathlib import Path
from datetime import datetime

def migrate_warnings():
    """Переносит предупреждения из старой системы в новую"""
    
    # Пути к базам данных
    curent_path = Path(__file__).parent
    warn_list_path = curent_path / 'databases' / 'warn_list.db'
    databases_path = curent_path / 'databases'
    
    print("=== НАЧАЛО МИГРАЦИИ ПРЕДУПРЕЖДЕНИЙ ===\n")
    
    # Проверяем существование старой базы данных
    if not warn_list_path.exists():
        print(f"ОШИБКА: Старая база данных не найдена: {warn_list_path}")
        return
    
    try:
        # Подключаемся к старой базе данных
        old_conn = sqlite3.connect(warn_list_path)
        old_cursor = old_conn.cursor()
        
        # Получаем список всех таблиц
        old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = old_cursor.fetchall()
        
        print(f"Найдено таблиц в старой базе: {len(tables)}")
        
        total_migrated = 0
        total_errors = 0
        
        # Список chat_id для обработки
        chat_ids = [1002143434937, 1002274082016, 1002439682589, 1003012971064]
        
        # Получаем список всех таблиц в старой базе
        old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        available_tables = [table[0] for table in old_cursor.fetchall()]
        
        print(f"Доступные таблицы в старой базе: {available_tables}")
        
        for chat_id in chat_ids:
            table_name = str(chat_id)  # Имя таблицы в старой базе - просто число
            
            print(f"\n--- Обработка чата {chat_id} (таблица {table_name}) ---")
            
            # Проверяем существование таблицы
            if table_name not in available_tables:
                print(f"Таблица {table_name} не найдена в старой базе")
                continue
            
            # Получаем все данные из старой таблицы
            old_cursor.execute(f'SELECT * FROM "{table_name}"')
            warnings = old_cursor.fetchall()
            
            print(f"Найдено пользователей с предупреждениями: {len(warnings)}")
            
            if len(warnings) == 0:
                continue
            
            # Проверяем структуру данных
            print(f"Структура данных (первая запись): {warnings[0] if warnings else 'Нет данных'}")
            
            # Путь к новой базе данных
            new_db_path = databases_path / f'{chat_id}.db'  # Без минуса в начале
            
            if not new_db_path.exists():
                print(f"Новая база данных не найдена: {new_db_path}")
                total_errors += 1
                continue
            
            # Подключаемся к новой базе данных
            new_conn = sqlite3.connect(new_db_path)
            new_cursor = new_conn.cursor()
            
            # Проверяем существование таблицы warns
            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='warns';")
            warns_exists = new_cursor.fetchone()
            
            if not warns_exists:
                print(f"Таблица 'warns' не найдена в {new_db_path}")
                new_conn.close()
                total_errors += 1
                continue
            
            migrated_count = 0
            
            for warning in warnings:
                try:
                    # Определяем структуру данных
                    if len(warning) >= 8:
                        # Полная структура: tg_id, warns_count, first_warn, second_warn, therd_warn, first_moder, second_moder, therd_moder
                        tg_id = warning[0]
                        warns_count = warning[1]
                        first_warn = warning[2]
                        second_warn = warning[3]
                        therd_warn = warning[4]
                        first_moder = warning[5]
                        second_moder = warning[6]
                        therd_moder = warning[7]
                    else:
                        print(f"Неожиданная структура данных: {warning}")
                        continue
                    
                    # Переносим каждое предупреждение
                    warn_data = [
                        (first_warn, first_moder, 1),
                        (second_warn, second_moder, 2),
                        (therd_warn, therd_moder, 3)
                    ]
                    
                    for warn_text, moder_id, warn_num in warn_data:
                        if warn_text and str(warn_text).strip():  # Пропускаем пустые предупреждения
                            try:
                                # Вставляем в новую таблицу
                                current_date = datetime.now().strftime('%d.%m.%Y')
                                new_cursor.execute(
                                    "INSERT INTO warns (user_id, reason, moder_id, date) VALUES (?, ?, ?, ?)",
                                    (tg_id, str(warn_text), int(moder_id) if moder_id and str(moder_id).isdigit() else 0, current_date)
                                )
                                migrated_count += 1
                                print(f"  ✓ Перенесено предупреждение #{warn_num} для пользователя {tg_id}")
                            except Exception as e:
                                print(f"  ✗ Ошибка при переносе предупреждения #{warn_num} для пользователя {tg_id}: {e}")
                                total_errors += 1
                
                except Exception as e:
                    print(f"  ✗ Ошибка обработки записи {warning}: {e}")
                    total_errors += 1
            
            # Сохраняем изменения
            new_conn.commit()
            new_conn.close()
            
            print(f"Перенос предупреждений для чата {chat_id} завершен: {migrated_count} записей")
            total_migrated += migrated_count
        
        old_conn.close()
        
        print(f"\n=== МИГРАЦИЯ ЗАВЕРШЕНА ===")
        print(f"Всего перенесено предупреждений: {total_migrated}")
        print(f"Всего ошибок: {total_errors}")
        
        if total_errors == 0:
            print("✓ Миграция прошла успешно!")
        else:
            print(f"⚠ Миграция завершена с {total_errors} ошибками")
            
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_warnings()
