import sqlite3
import json

# Тестируем логику работы с кодом
def test_code_logic(code):
    conn = sqlite3.connect('databases/All.db')
    cursor = conn.cursor()
    
    # Ищем код в таблице
    cursor.execute('SELECT chat_id, activate_cnt, target_chats FROM links WHERE link = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return {"status": "error", "message": "Неверный код приглашения"}
    
    chat_id, activate_cnt, target_chats_json = result
    
    if activate_cnt <= 0:
        return {"status": "error", "message": "Код больше не действителен"}
    
    # Парсим список целевых чатов
    target_chats = []
    try:
        target_chats = json.loads(target_chats_json) if target_chats_json else []
    except:
        target_chats = []
    
    # Если target_chats пустой, используем основной chat_id
    if not target_chats:
        target_chats = [chat_id]
    
    return {
        "status": "success",
        "data": {
            "chat_id": chat_id,
            "activate_cnt": activate_cnt,
            "target_chats": target_chats,
            "code": code
        }
    }

# Тестируем
result = test_code_logic('test123')
print("Результат теста:")
print(json.dumps(result, indent=2, ensure_ascii=False))
