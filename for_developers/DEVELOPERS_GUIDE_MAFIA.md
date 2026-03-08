# 🎭 Модуль Mafia (Мафия) - Полное руководство для разработчиков

**Версия:** 1.0  
**Дата:** 20.12.2025  
**Статус:** ✅ Готово к production  
**Язык:** Python 3.10+  

---

## 📖 Обзор

Модуль Mafia (`modules/mafia.py`) реализует полнофункциональную ролевую игру "Мафия" с поддержкой 6+ различных ролей, ночных и дневных фаз, голосования и динамического развития игры.

### Основные возможности

✅ **Множественные роли** - Мирный, Дон, Мафия, Комиссар, Доктор, Маньяк  
✅ **Фазы игры** - Ночь/День с разными действиями  
✅ **Голосование** - Дневное голосование за исключение игрока  
✅ **Ночные действия** - Убийства, проверки, защита  
✅ **Сложная логика** - Учёт ролей, победных условий, взаимодействий  
✅ **История игр** - Сохранение результатов в БД  

---

## 🎭 Роли в игре

### Роли горожан

| Роль | Описание | Действие |
|------|---------|---------|
| 👥 Мирный | Обычный житель без способностей | Голосование днём |
| 🕵️ Комиссар | Следователь | Проверить роль или убить ночью |
| 🏥 Доктор | Защитник | Спасить игрока от убийства ночью |

### Роли мафии

| Роль | Описание | Действие |
|------|---------|---------|
| 🕴 Дон | Глава мафии | Координирует убийства и знает других |
| 💀 Мафия | Член мафии | Участвует в убийствах |

### Нейтральные роли

| Роль | Описание | Действие |
|------|---------|---------|
| 🔪 Маньяк | Убийца-одиночка | Убивает ночью для себя |

---

## 🏗️ Архитектура

### Система распределения ролей

```python
QUANTITY_OF_ROLES = {
    4: '2 1 0 0 1 0',  # 4 игрока: 2 мирных, 1 дон, 0 мафии, 0 комиссар, 1 доктор, 0 маньяк
    5: '2 1 0 1 1 0',
    6: '3 1 0 1 1 0',
    7: '4 1 0 1 1 0',
    8: '4 1 1 1 1 0',
    9: '4 1 1 1 1 1',
    10: '4 1 2 1 1 1'
}

def parse_roles(count: int) -> dict:
    """Преобразует строку ролей в словарь"""
    if count not in QUANTITY_OF_ROLES:
        return {}
    
    roles_str = QUANTITY_OF_ROLES[count]
    mirny, don, mafia, police, doctor, maniak = map(int, roles_str.split())
    
    return {
        'mirny': mirny,
        'don': don,
        'mafia': mafia,
        'police': police,
        'doctor': doctor,
        'maniak': maniak
    }
```

### Поток игры

```
Игроки регистрируются
         ↓
Роли распределяются случайно
         ↓
НОЧЬ 1: Действия мафии, доктора, комиссара
         ↓
ДЕНЬ 1: Все голосуют за исключение
         ↓
Проверка условия победы
         ↓
НОЧЬ 2: Ночные действия продолжаются
         ↓
ДЕНЬ 2: Голосование
         ↓
... (Игра продолжается)
         ↓
Побеждают горожане ИЛИ мафия ИЛИ маньяк
```

---

## 💻 Примеры использования

### Пример 1: Начало игры

```python
async def start_mafia_game(chat_id: int, players: list[int], bot: Bot) -> bool:
    """Начинает новую игру мафии"""
    player_count = len(players)
    
    if player_count < 4:
        return False  # Минимум 4 игрока
    
    # Получаем распределение ролей
    roles_dist = parse_roles(player_count)
    
    # Создаём список всех ролей
    all_roles = (
        ['mirny'] * roles_dist['mirny'] +
        ['don'] * roles_dist['don'] +
        ['mafia'] * roles_dist['mafia'] +
        ['police'] * roles_dist['police'] +
        ['doctor'] * roles_dist['doctor'] +
        ['maniak'] * roles_dist['maniak']
    )
    
    # Перемешиваем роли
    random.shuffle(all_roles)
    
    # Распределяем каждому игроку
    player_roles = {player_id: role for player_id, role in zip(players, all_roles)}
    
    # Отправляем приватные сообщения с ролями
    for player_id, role in player_roles.items():
        role_info = ROLES_ABOUT.get(role, "Неизвестная роль")
        await bot.send_message(player_id, f"🎭 Ваша роль: {role_info}")
    
    return True
```

### Пример 2: Ночное голосование мафии

```python
async def mafia_night_vote(game_id: str, db_path: str) -> int:
    """Проводит голосование мафии за жертву"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Получаем всех живых членов мафии
    mafia_members = cursor.execute(
        "SELECT user_id FROM mafia_game_players WHERE game_id = ? AND role IN ('don', 'mafia') AND alive = 1",
        (game_id,)
    ).fetchall()
    
    # Получаем всех живых горожан (кроме мафии)
    possible_victims = cursor.execute(
        "SELECT user_id FROM mafia_game_players WHERE game_id = ? AND role NOT IN ('don', 'mafia') AND alive = 1",
        (game_id,)
    ).fetchall()
    
    # Каждый член мафии голосует
    votes = {}
    for member_id, in mafia_members:
        # Выбираем случайную жертву
        victim_id = random.choice(possible_victims)[0]
        votes[victim_id] = votes.get(victim_id, 0) + 1
    
    # Определяем жертву с наибольшим количеством голосов
    if votes:
        victim_id = max(votes, key=votes.get)
        return victim_id
    
    connection.close()
    return None
```

### Пример 3: Дневное голосование

```python
async def day_voting(game_id: str, votes: dict[int, int], db_path: str) -> int:
    """Обрабатывает дневное голосование"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Находим игрока с максимальным количеством голосов
    if not votes:
        return None
    
    voted_out = max(votes, key=votes.get)
    vote_count = votes[voted_out]
    
    # Удаляем игрока из живых
    cursor.execute(
        "UPDATE mafia_game_players SET alive = 0 WHERE game_id = ? AND user_id = ?",
        (game_id, voted_out)
    )
    
    # Получаем информацию об исключённом игроке
    player_info = cursor.execute(
        "SELECT user_id, nik, role FROM mafia_game_players WHERE game_id = ? AND user_id = ?",
        (game_id, voted_out)
    ).fetchone()
    
    connection.commit()
    connection.close()
    
    return player_info
```

### Пример 4: Проверка условия победы

```python
def check_win_condition(game_id: str, db_path: str) -> tuple[bool, str]:
    """Проверяет, выиграла ли какая-то сторона"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Подсчитываем живых игроков по ролям
    alive_counts = cursor.execute('''
        SELECT role, COUNT(*) FROM mafia_game_players 
        WHERE game_id = ? AND alive = 1
        GROUP BY role
    ''', (game_id,)).fetchall()
    
    alive_by_role = {role: count for role, count in alive_counts}
    
    mafia_alive = alive_by_role.get('don', 0) + alive_by_role.get('mafia', 0)
    townspeople_alive = sum(count for role, count in alive_by_role.items() 
                           if role not in ['don', 'mafia'])
    maniak_alive = alive_by_role.get('maniak', 0)
    
    # Проверяем условия победы
    if mafia_alive == 0:
        connection.close()
        return True, "Горожане выиграли! Мафия уничтожена!"
    
    if mafia_alive >= townspeople_alive:
        connection.close()
        return True, "Мафия выиграла!"
    
    if maniak_alive > 0 and townspeople_alive + mafia_alive == 1:
        connection.close()
        return True, "Маньяк выиграл!"
    
    connection.close()
    return False, None
```

---

## 📊 Структура базы данных

### Таблица `mafia_game_players`

```sql
CREATE TABLE IF NOT EXISTS mafia_game_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    nik TEXT,
    role TEXT NOT NULL,
    alive INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Таблица `mafia_game_actions`

```sql
CREATE TABLE IF NOT EXISTS mafia_game_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    night_number INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_id INTEGER,
    result TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 🚀 Расширение функциональности

### Идея 1: Новые роли

```python
EXTENDED_ROLES = {
    # ... старые роли ...
    "love": "💕 Влюблённые - пара игроков, защищают друг друга",
    "witch": "🧙 Ведьма - может спасти или проклясть",
    "informant": "🕵️ Информатор - знает одного члена мафии"
}
```

### Идея 2: Система статистики

```python
def get_player_mafia_stats(user_id: int, db_path: str) -> dict:
    """Получает статистику игрока в мафии"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    stats = cursor.execute('''
        SELECT role, COUNT(*) as games, SUM(CASE WHEN alive = 1 THEN 1 ELSE 0 END) as wins
        FROM mafia_game_players
        WHERE user_id = ?
        GROUP BY role
    ''', (user_id,)).fetchall()
    
    connection.close()
    
    return {role: {"games": games, "wins": wins} for role, games, wins in stats}
```

### Идея 3: Рейтинг лучших игроков

```python
def get_mafia_leaderboard(chat_id: int, limit: int = 10, db_path: str = "mafia.db") -> list:
    """Получает рейтинг лучших игроков мафии"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    leaders = cursor.execute('''
        SELECT user_id, COUNT(*) as games_played, 
               SUM(CASE WHEN alive = 1 THEN 1 ELSE 0 END) as wins
        FROM mafia_game_players
        WHERE chat_id = ?
        GROUP BY user_id
        ORDER BY wins DESC
        LIMIT ?
    ''', (chat_id, limit)).fetchall()
    
    connection.close()
    return leaders
```

---

## 🐛 Решение проблем

### Проблема: "Роли распределяются неправильно"

**Решение:** Убедитесь что вы перемешиваете список ролей

```python
random.shuffle(all_roles)  # ✅ Обязательно!
```

### Проблема: "Игра не заканчивается"

**Решение:** Проверяйте условие победы после каждого дня

```python
won, message = check_win_condition(game_id, db_path)
if won:
    await notify_game_end(chat_id, message)
    delete_game(game_id)
```

---

## 📝 Лицензия

Часть проекта WERTY | Chat-Manager Bot

---

**Версия:** 1.0  
**Разработано:** GitHub Copilot  
**Последнее обновление:** 20.12.2025
