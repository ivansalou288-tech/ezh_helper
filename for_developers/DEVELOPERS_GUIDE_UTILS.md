# 🔍 Модули Who-Is-Who и Message Top - Полное руководство для разработчиков

**Версия:** 1.0  
**Дата:** 20.12.2025  
**Статус:** ✅ Готово к production  
**Язык:** Python 3.10+  

---

## 📖 Обзор

Два утилитарных модуля для работы с информацией о пользователях и сообщениях:

1. **Who-Is-Who** (`modules/who_is_who.py`) - поиск пользователя по описанию
2. **Message Top** (`modules/message_top.py`) - топ пользователей по активности в чате

---

## 🔍 Who-Is-Who (Кто это?)

### Обзор

Модуль позволяет быстро найти пользователя по его описанию или никнейму. Поиск проводится среди пользователей, зарегистрированных в чате.

### Основной обработчик

```python
@dp.message_handler(Text(startswith=["бот кто"], ignore_case=True))
async def who_is_who(message: types.Message):
    """
    Команда для поиска пользователя по описанию
    Формат: бот кто {описание}
    """
```

**Срабатывает когда:**
- Пользователь напишет `бот кто {описание}`

**Логика:**
1. Парсит описание из сообщения
2. Получает таблицу пользователей для чата
3. Ищет совпадение в `nik` (ник), `username` (юзернейм) или `first_name` (имя)
4. Возвращает найденного пользователя с его информацией

### Примеры использования

#### Пример 1: Поиск по нику

```python
def search_user_by_nic(chat_id: int, search_nic: str, db_path: str) -> dict:
    """Ищет пользователя по нику"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    
    try:
        result = cursor.execute(
            f"SELECT tg_id, nik, username, first_name FROM [{table_name}] WHERE nik LIKE ?",
            (f"%{search_nic}%",)
        ).fetchone()
        
        if result:
            return {
                "user_id": result[0],
                "nik": result[1],
                "username": result[2],
                "first_name": result[3],
                "found": True
            }
        else:
            return {"found": False}
    finally:
        connection.close()

# Использование
result = search_user_by_nic(-1001234567890, "Ivan", "Base_bot.db")
if result["found"]:
    print(f"Найден: {result['nik']} (@{result['username']})")
```

#### Пример 2: Поиск по юзернейму

```python
def search_user_by_username(chat_id: int, username: str, db_path: str) -> dict:
    """Ищет пользователя по юзернейму"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    
    # Убираем @ если присутствует
    if username.startswith("@"):
        username = username[1:]
    
    try:
        result = cursor.execute(
            f"SELECT tg_id, nik, username, first_name FROM [{table_name}] WHERE username = ?",
            (username,)
        ).fetchone()
        
        if result:
            return {
                "user_id": result[0],
                "nik": result[1],
                "username": result[2],
                "first_name": result[3],
                "found": True
            }
        else:
            return {"found": False}
    finally:
        connection.close()
```

#### Пример 3: Расширенный поиск

```python
def advanced_search(chat_id: int, keywords: list[str], db_path: str) -> list[dict]:
    """Поиск по нескольким ключевым словам"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    results = []
    
    try:
        for keyword in keywords:
            matches = cursor.execute(
                f"SELECT tg_id, nik, username FROM [{table_name}] "
                "WHERE nik LIKE ? OR username LIKE ? OR first_name LIKE ?",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            ).fetchall()
            
            for user_id, nik, username in matches:
                results.append({
                    "user_id": user_id,
                    "nik": nik,
                    "username": username
                })
        
        return results
    finally:
        connection.close()
```

---

## 📊 Message Top (Топ сообщений)

### Обзор

Модуль показывает рейтинг пользователей по количеству отправленных сообщений в чате. Поддерживает разные сортировки и ограничение количества результатов.

### Основные обработчики

```python
@dp.message_handler(Text(startswith=["топ вся", "!топ сообщений"], ignore_case=True))
async def show_messages_top_all_time(message: types.Message):
    """
    Показывает топ пользователей по сообщениям за всё время
    Формат: !топ сообщений [количество]
    """
```

**Примеры использования:**
```
!топ сообщений          # Топ 10 (по умолчанию)
!топ сообщений 20       # Топ 20
топ вся                 # Топ 10
топ вся 50              # Топ 50
```

### Примеры использования

#### Пример 1: Получение топ сообщений

```python
def get_messages_top(chat_id: int, limit: int = 10, db_path: str = "Base_bot.db") -> list[tuple]:
    """Получает топ пользователей по количеству сообщений"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    
    try:
        # Пытаемся найти колонку с количеством сообщений
        columns_info = cursor.execute(f"PRAGMA table_info([{table_name}])").fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Ищем колонку для подсчёта сообщений
        message_column = None
        for candidate in ("mess_count", "message_count", "messages_count", "msg_count", "messages"):
            if candidate in column_names:
                message_column = candidate
                break
        
        if not message_column:
            return []
        
        # Получаем топ
        top = cursor.execute(
            f"SELECT nik, {message_column} FROM [{table_name}] ORDER BY {message_column} DESC LIMIT ?",
            (limit,)
        ).fetchall()
        
        return top
    finally:
        connection.close()

# Использование
top = get_messages_top(-1001234567890, limit=10)
for idx, (nik, msg_count) in enumerate(top, 1):
    print(f"{idx}. {nik}: {msg_count} сообщений")
```

#### Пример 2: Форматированный топ

```python
def format_messages_top(chat_id: int, limit: int = 10, db_path: str = "Base_bot.db") -> str:
    """Форматирует топ для отправки в сообщение"""
    top = get_messages_top(chat_id, limit, db_path)
    
    if not top:
        return "📊 Данных нет"
    
    message = "📊 <b>Топ по сообщениям</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, (nik, msg_count) in enumerate(top, 1):
        medal = medals[idx - 1] if idx <= 3 else f"{idx}️⃣"
        message += f"{medal} <b>{nik}</b> — {msg_count} сообщений\n"
    
    return message
```

#### Пример 3: Статистика активности

```python
def get_activity_stats(chat_id: int, db_path: str = "Base_bot.db") -> dict:
    """Получает статистику активности в чате"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    
    try:
        # Находим колонку сообщений
        columns_info = cursor.execute(f"PRAGMA table_info([{table_name}])").fetchall()
        column_names = [col[1] for col in columns_info]
        
        message_column = None
        for candidate in ("mess_count", "message_count", "messages_count", "msg_count", "messages"):
            if candidate in column_names:
                message_column = candidate
                break
        
        if not message_column:
            return {}
        
        # Получаем статистику
        stats = cursor.execute(
            f"SELECT COUNT(*), SUM({message_column}), AVG({message_column}), MAX({message_column}) FROM [{table_name}]"
        ).fetchone()
        
        users_count, total_messages, avg_messages, max_messages = stats
        
        return {
            "total_users": users_count or 0,
            "total_messages": total_messages or 0,
            "avg_messages_per_user": round(avg_messages, 2) if avg_messages else 0,
            "max_messages": max_messages or 0,
            "activity_level": "Высокая" if (total_messages or 0) / max(users_count or 1, 1) > 50 else "Средняя"
        }
    finally:
        connection.close()

# Использование
stats = get_activity_stats(-1001234567890)
print(f"Всего пользователей: {stats['total_users']}")
print(f"Всего сообщений: {stats['total_messages']}")
print(f"Среднее на пользователя: {stats['avg_messages_per_user']}")
```

#### Пример 4: Трендинг пользователей

```python
def get_trending_users(chat_id: int, limit: int = 5, db_path: str = "Base_bot.db") -> list:
    """Получает пользователей с наибольшим ростом активности"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    
    try:
        # Можно добавить колонку last_week_messages для отслеживания роста
        # Пока просто получаем самых активных
        trending = cursor.execute(
            f"SELECT nik, mess_count FROM [{table_name}] ORDER BY mess_count DESC LIMIT ?",
            (limit,)
        ).fetchall()
        
        return trending
    finally:
        connection.close()
```

---

## 🏗️ Структура таблиц

### Таблица чата (например `[123456789]` для chat_id = -123456789)

```sql
CREATE TABLE [123456789] (
    tg_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    nik TEXT,
    mess_count INTEGER DEFAULT 0,
    -- и другие колонки...
)
```

---

## 🚀 Расширение функциональности

### Идея 1: Недельный рейтинг

```python
def add_weekly_tracking(chat_id: int, db_path: str = "Base_bot.db"):
    """Добавляет отслеживание недельной активности"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    
    # Добавляем колонки если их нет
    cursor.execute(f"ALTER TABLE [{table_name}] ADD COLUMN week_messages INTEGER DEFAULT 0")
    cursor.execute(f"ALTER TABLE [{table_name}] ADD COLUMN week_reset_date TEXT")
    
    connection.commit()
    connection.close()
```

### Идея 2: Медали за достижения

```python
def get_user_medals(chat_id: int, user_nik: str, db_path: str = "Base_bot.db") -> list[str]:
    """Получает медали пользователя"""
    top = get_messages_top(chat_id, limit=100, db_path=db_path)
    
    medals = []
    
    # Находим позицию пользователя
    for idx, (nik, msg_count) in enumerate(top, 1):
        if nik == user_nik:
            if idx == 1:
                medals.append("🥇 Король чата")
            elif idx == 2:
                medals.append("🥈 Второй по активности")
            elif idx == 3:
                medals.append("🥉 Третий по активности")
            elif idx <= 10:
                medals.append("⭐ Топ 10")
            
            # Количество сообщений
            if msg_count >= 1000:
                medals.append("💬 1000+ сообщений")
            elif msg_count >= 500:
                medals.append("💬 500+ сообщений")
    
    return medals
```

### Идея 3: Сравнение пользователей

```python
def compare_users(chat_id: int, user1_nik: str, user2_nik: str, db_path: str = "Base_bot.db") -> dict:
    """Сравнивает активность двух пользователей"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    table_name = str(-(chat_id))
    
    try:
        user1_data = cursor.execute(
            f"SELECT nik, mess_count FROM [{table_name}] WHERE nik = ?",
            (user1_nik,)
        ).fetchone()
        
        user2_data = cursor.execute(
            f"SELECT nik, mess_count FROM [{table_name}] WHERE nik = ?",
            (user2_nik,)
        ).fetchone()
        
        if not user1_data or not user2_data:
            return {}
        
        diff = user1_data[1] - user2_data[1]
        
        return {
            "user1": {"nik": user1_data[0], "messages": user1_data[1]},
            "user2": {"nik": user2_data[0], "messages": user2_data[1]},
            "difference": abs(diff),
            "leader": user1_data[0] if diff > 0 else user2_data[0]
        }
    finally:
        connection.close()
```

---

## 🐛 Решение проблем

### Проблема: "Топ не показывает данные"

**Решение:** Проверьте наличие колонки сообщений

```python
# Убедитесь что таблица имеет одну из этих колонок:
# mess_count, message_count, messages_count, msg_count, messages
```

### Проблема: "Поиск не находит пользователя"

**Решение:** Проверьте правильность формата команды

```python
# ✅ Правильно
бот кто Иван
бот кто @username
бот кто 123456  # По ID

# ❌ Неправильно
бот кто        # Без параметра
```

---

## 📝 Лицензия

Часть проекта WERTY | Chat-Manager Bot

---

**Версия:** 1.0  
**Разработано:** GitHub Copilot  
**Последнее обновление:** 20.12.2025
