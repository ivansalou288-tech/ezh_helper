import sqlite3
from pathlib import Path
from datetime import datetime

def migrate_warnings_simple():
    """Упрощенный перенос предупреждений из старой системы в новую"""
    
    # Пути к базам данных
    curent_path = Path(__file__).parent
    warn_list_path = curent_path / 'databases' / 'warn_list.db'
    databases_path = curent_path / 'databases'
    
    print("=== УПРОЩЕННАЯ МИГРАЦИЯ ПРЕДУПРЕЖДЕНИЙ ===\n")
    
    if not warn_list_path.exists():
        print(f"ОШИБКА: Старая база данных не найдена: {warn_list_path}")
        return
    
    try:
        old_conn = sqlite3.connect(warn_list_path)
        old_cursor = old_conn.cursor()
        
        # Получаем список всех таблиц
        old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        available_tables = [table[0] for table in old_cursor.fetchall()]
        
        print(f"Доступные таблицы в старой базе: {available_tables}")
        
        total_migrated = 0
        total_errors = 0
        
        # Список chat_id для обработки
        chat_ids = [1002143434937, 1002274082016, 1002439682589, 1003012971064]
        
        for chat_id in chat_ids:
            table_name = str(chat_id)
            
            print(f"\n--- Обработка чата {chat_id} (таблица {table_name}) ---")
            
            if table_name not in available_tables:
                print(f"Таблица {table_name} не найдена в старой базе")
                continue
            
            # Получаем все данные из старой таблицы
            old_cursor.execute(f'SELECT * FROM "{table_name}"')
            warnings = old_cursor.fetchall()
            
            print(f"Найдено пользователей с предупреждениями: {len(warnings)}")
            
            if len(warnings) == 0:
                continue
            
            print(f"Пример данных: {warnings[0] if warnings else 'Нет данных'}")
            
            # Путь к новой базе данных
            new_db_path = databases_path / f'{chat_id}.db'
            
            if not new_db_path.exists():
                print(f"Новая база данных не найдена: {new_db_path}")
                total_errors += 1
                continue
            
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
                    # Структура: tg_id, warns_count, first_warn, second_warn, therd_warn, first_moder, second_moder, therd_moder
                    tg_id = warning[0]
                    warns_count = warning[1]
                    first_warn = warning[2]
                    second_warn = warning[3]
                    therd_warn = warning[4]
                    first_moder = warning[5]
                    second_moder = warning[6]
                    therd_moder = warning[7]
                    
                    print(f"\n👤 Обработка пользователя {tg_id}:")
                    print(f"  first_moder: {repr(first_moder)}")
                    print(f"  second_moder: {repr(second_moder)}")
                    print(f"  therd_moder: {repr(therd_moder)}")
                    
                    # Функция для простого извлечения ID
                    def get_moder_id(moder_data):
                        if not moder_data:
                            return 0
                        
                        moder_str = str(moder_data).strip()
                        
                        # Если это число
                        if moder_str.isdigit():
                            return int(moder_str)
                        
                        # Если это гиперссылка, пытаемся извлечь ID
                        if 'tg://user?id=' in moder_str:
                            import re
                            match = re.search(r'tg://user\?id=(\d+)', moder_str)
                            if match:
                                return int(match.group(1))
                        
                        # Если не смогли извлечь ID, но есть данные
                        print(f"    ⚠️ Не удалось извлечь ID из: {moder_str}")
                        return 0
                    
                    # Переносим каждое предупреждение
                    warn_data = [
                        (first_warn, get_moder_id(first_moder), 1),
                        (second_warn, get_moder_id(second_moder), 2),
                        (therd_warn, get_moder_id(therd_moder), 3)
                    ]
                    
                    for warn_text, moder_id, warn_num in warn_data:
                        if warn_text and str(warn_text).strip():
                            try:
                                current_date = datetime.now().strftime('%d.%m.%Y')
                                
                                new_cursor.execute(
                                    "INSERT INTO warns (user_id, reason, moder_id, date) VALUES (?, ?, ?, ?)",
                                    (tg_id, str(warn_text), moder_id, current_date)
                                )
                                migrated_count += 1
                                print(f"  ✅ Перенесено предупреждение #{warn_num}, moder_id: {moder_id}")
                            except Exception as e:
                                print(f"  ❌ Ошибка при переносе: {e}")
                                total_errors += 1
                
                except Exception as e:
                    print(f"  ❌ Ошибка обработки записи {warning}: {e}")
                    total_errors += 1
            
            new_conn.commit()
            new_conn.close()
            
            print(f"Перенос предупреждений для чата {chat_id} завершен: {migrated_count} записей")
            total_migrated += migrated_count
        
        old_conn.close()
        
        print(f"\n=== МИГРАЦИЯ ЗАВЕРШЕНА ===")
        print(f"Всего перенесено предупреждений: {total_migrated}")
        print(f"Всего ошибок: {total_errors}")
        
        if total_errors == 0:
            print("✅ Миграция прошла успешно!")
        else:
            print(f"⚠️ Миграция завершена с {total_errors} ошибками")
            
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_warnings_simple()
