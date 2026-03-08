# 🏆 Модуль Tournaments (Турниры) - Полное руководство для разработчиков

**Версия:** 1.0  
**Дата:** 20.12.2025  
**Статус:** ✅ Готово к production  
**Язык:** Python 3.10+  

---

## 📖 Обзор

Модуль Tournaments (`modules/turnaments.py`) реализует полнофункциональную систему управления турнирами с поддержкой личных и командных турниров, регистрацией участников, отслеживанием побед и подведением итогов.

### Основные возможности

✅ **Создание турниров** - организаторы создают новые турниры с параметрами  
✅ **Регистрация участников** - как личная, так и командная  
✅ **Управление турниром** - редактирование параметров во время регистрации  
✅ **Отслеживание побед** - система ведения счёта  
✅ **Автоматическое распределение команд** - случайное разделение на группы  
✅ **История турниров** - сохранение всех данных в БД  
✅ **Уникальные ID** - каждый турнир имеет свой идентификатор  

---

## 🏗️ Архитектура

### Структура турнира

```
Турнир
├── Основная информация
│   ├── ID (уникальный 8-символьный код)
│   ├── Название
│   ├── Организатор (ID + имя)
│   ├── Дата и время
│   ├── Максимум участников
│   └── Размер команды
│
├── Описание
│   ├── Правила
│   └── Комментарии
│
├── Статус
│   ├── Регистрация открыта/закрыта
│   ├── Турнир идёт
│   └── Завершён
│
├── Участники/Команды
│   ├── Список зарегистрированных
│   ├── Информация о командах
│   └── Счёт побед
│
└── История
    └── Сохранение результатов в БД
```

---

## 🔌 API функций турниров

### create_tournament()

Создаёт новый турнир.

```python
def create_tournament(
    moder_id: int,
    chat_id: int,
    name: str,
    date: str,          # "HH:MM:SS DD.MM.YYYY"
    max_participants: int,
    rules: str,
    comments: str,
    db_path: str = "tournaments.db"
) -> tuple[bool, str]:
    """
    Создаёт новый турнир
    Возвращает: (успех, ID_турнира_или_сообщение_об_ошибке)
    """
```

**Параметры:**
- `moder_id` (int): ID организатора
- `chat_id` (int): ID чата, где создаётся турнир
- `name` (str): Название турнира
- `date` (str): Дата в формате "HH:MM:SS DD.MM.YYYY"
- `max_participants` (int): Максимальное количество участников (1-60)
- `rules` (str): Правила турнира
- `comments` (str): Дополнительные комментарии
- `db_path` (str): Путь к БД

**Возвращает:**
- `(True, tournament_id)` - успешно создан
- `(False, error_message)` - ошибка создания

---

## 💻 Примеры использования

### Пример 1: Создание турнира

```python
def create_tournament_example():
    """Пример создания турнира"""
    success, result = create_tournament(
        moder_id=123456,
        chat_id=-1001234567890,
        name="Чемпионат по PvP 2025",
        date="18:00:00 25.12.2025",
        max_participants=16,
        rules="No items, Only weapons, Final на платформе",
        comments="Победитель получит 1000 рублей",
        db_path="tournaments.db"
    )
    
    if success:
        print(f"✅ Турнир создан! ID: {result}")
    else:
        print(f"❌ Ошибка: {result}")
```

### Пример 2: Регистрация участника

```python
def register_participant(tournament_id: str, user_id: int, user_name: str, db_path: str) -> bool:
    """Регистрирует участника в турнир"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Проверяем есть ли место
        cursor.execute(
            "SELECT registered_count, max_participants FROM tournaments WHERE id = ?",
            (tournament_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return False
        
        registered_count, max_participants = result
        
        if registered_count >= max_participants:
            return False  # Нет места
        
        # Добавляем участника
        cursor.execute(
            "INSERT INTO tournament_participants (tournament_id, user_id, user_name) VALUES (?, ?, ?)",
            (tournament_id, user_id, user_name)
        )
        
        # Увеличиваем счётчик регистрированных
        cursor.execute(
            "UPDATE tournaments SET registered_count = registered_count + 1 WHERE id = ?",
            (tournament_id,)
        )
        
        connection.commit()
        return True
    finally:
        connection.close()

# Использование
if register_participant("A1B2C3D4", 123456, "Ivan", "tournaments.db"):
    print("✅ Регистрация успешна")
else:
    print("❌ Не удалось зарегистрироваться")
```

### Пример 3: Регистрация команды

```python
def register_team(tournament_id: str, captain_id: int, team_members: list[int], db_path: str) -> bool:
    """Регистрирует команду в турнир"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Генерируем ID команды
        import secrets
        team_id = f"TEAM_{secrets.token_hex(4)}"
        
        # Добавляем команду
        cursor.execute(
            "INSERT INTO tournament_teams (tournament_id, team_id, captain_id) VALUES (?, ?, ?)",
            (tournament_id, team_id, captain_id)
        )
        
        # Добавляем всех членов команды
        for member_id in team_members:
            cursor.execute(
                "INSERT INTO tournament_team_members (team_id, user_id) VALUES (?, ?)",
                (team_id, member_id)
            )
        
        connection.commit()
        return True
    finally:
        connection.close()

# Использование
team_members = [123456, 234567, 345678, 456789]
if register_team("A1B2C3D4", 123456, team_members, "tournaments.db"):
    print("✅ Команда зарегистрирована")
```

### Пример 4: Отслеживание побед

```python
def record_victory(tournament_id: str, team_id: str, db_path: str) -> bool:
    """Записывает победу для команды"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "UPDATE tournament_teams SET wins = wins + 1 WHERE tournament_id = ? AND team_id = ?",
            (tournament_id, team_id)
        )
        
        connection.commit()
        return True
    finally:
        connection.close()

# Использование
if record_victory("A1B2C3D4", "TEAM_ABC123", "tournaments.db"):
    print("✅ Победа записана")
```

### Пример 5: Получение таблицы побед

```python
def get_tournament_leaderboard(tournament_id: str, db_path: str) -> list:
    """Получает таблицу лидеров турнира"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        leaderboard = cursor.execute(
            "SELECT team_id, captain_id, wins FROM tournament_teams WHERE tournament_id = ? ORDER BY wins DESC",
            (tournament_id,)
        ).fetchall()
        
        return leaderboard
    finally:
        connection.close()

# Использование
leaderboard = get_tournament_leaderboard("A1B2C3D4", "tournaments.db")
for idx, (team_id, captain, wins) in enumerate(leaderboard, 1):
    print(f"{idx}. Команда {team_id} (капитан {captain}): {wins} побед")
```

---

## 📊 Структура базы данных

### Таблица `tournaments`

```sql
CREATE TABLE IF NOT EXISTS tournaments (
    id TEXT PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    organizer_id INTEGER NOT NULL,
    organizer_name TEXT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    max_participants INTEGER NOT NULL,
    registered_count INTEGER DEFAULT 0,
    rules TEXT,
    comments TEXT,
    status TEXT DEFAULT 'registration',  -- registration, active, finished
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Таблица `tournament_participants`

```sql
CREATE TABLE IF NOT EXISTS tournament_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    user_name TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
)
```

### Таблица `tournament_teams`

```sql
CREATE TABLE IF NOT EXISTS tournament_teams (
    team_id TEXT PRIMARY KEY,
    tournament_id TEXT NOT NULL,
    captain_id INTEGER NOT NULL,
    wins INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
)
```

### Таблица `tournament_team_members`

```sql
CREATE TABLE IF NOT EXISTS tournament_team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(team_id) REFERENCES tournament_teams(team_id)
)
```

---

## 🚀 Расширение функциональности

### Идея 1: Система плей-офф

```python
def generate_playoff_bracket(tournament_id: str, db_path: str) -> list[tuple]:
    """Генерирует кронштейн плей-офф из участников"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Получаем всех участников в порядке побед
    participants = cursor.execute(
        "SELECT team_id FROM tournament_teams WHERE tournament_id = ? ORDER BY wins DESC",
        (tournament_id,)
    ).fetchall()
    
    connection.close()
    
    # Создаём матчи: 1 vs 2, 3 vs 4, и т.д.
    bracket = []
    for i in range(0, len(participants), 2):
        if i + 1 < len(participants):
            bracket.append((participants[i][0], participants[i+1][0]))
    
    return bracket
```

### Идея 2: Система групп

```python
def divide_into_groups(tournament_id: str, group_size: int = 4, db_path: str = "tournaments.db") -> dict:
    """Разделяет участников на группы"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    participants = cursor.execute(
        "SELECT user_id FROM tournament_participants WHERE tournament_id = ?",
        (tournament_id,)
    ).fetchall()
    
    connection.close()
    
    groups = {}
    for i, (user_id,) in enumerate(participants):
        group_num = i // group_size
        if group_num not in groups:
            groups[group_num] = []
        groups[group_num].append(user_id)
    
    return groups
```

### Идея 3: Система рейтингов

```python
def calculate_tournament_rating(user_id: int, db_path: str) -> float:
    """Расчитывает рейтинг игрока на основе турниров"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Получаем все турниры где участвовал игрок
    tournaments = cursor.execute(
        "SELECT t.id, t.max_participants, tt.wins FROM tournaments t "
        "JOIN tournament_teams tt ON t.id = tt.tournament_id "
        "WHERE tt.captain_id = ?",
        (user_id,)
    ).fetchall()
    
    connection.close()
    
    rating = 0
    for tournament_id, max_participants, wins in tournaments:
        # Рейтинг зависит от размера турнира и побед
        tournament_rating = (wins / max_participants) * 100
        rating += tournament_rating
    
    return rating
```

---

## 🐛 Решение проблем

### Проблема: "Турнир не создаётся"

**Решение:** Проверьте формат даты

```python
# ✅ Правильно
date = "18:00:00 25.12.2025"
datetime.strptime(date, "%H:%M:%S %d.%m.%Y")

# ❌ Неправильно
date = "25.12.2025 18:00:00"  # Неверный порядок
```

### Проблема: "ID турнира слишком длинный"

**Решение:** Используйте 8-символьный код

```python
from password_generator import PasswordGenerator

pwo = PasswordGenerator()
tournament_id = pwo.shuffle_password('ASDFGHJKL12345678', 8)  # Ровно 8 символов
```

### Проблема: "Команды не распределяются правильно"

**Решение:** Убедитесь что используете правильный размер группы

```python
# Получите размер команды из турнира
tournament_info = cursor.execute(
    "SELECT team_size FROM tournaments WHERE id = ?",
    (tournament_id,)
).fetchone()

team_size = tournament_info[0] if tournament_info else 1
```

---

## 📝 Лицензия

Часть проекта WERTY | Chat-Manager Bot

---

**Версия:** 1.0  
**Разработано:** GitHub Copilot  
**Последнее обновление:** 20.12.2025
