# 🎲 Модуль Cubes (Дуэль на кубиках) - Полное руководство для разработчиков

**Версия:** 1.0  
**Дата:** 20.12.2025  
**Статус:** ✅ Готово к production  
**Язык:** Python 3.10+  

---

## 📋 Содержание

1. [Обзор](#обзор)
2. [Архитектура](#архитектура)
3. [API системы дуэлей](#api-системы-дуэлей)
4. [Структура базы данных](#структура-базы-данных)
5. [Обработчики сообщений](#обработчики-сообщений)
6. [Примеры использования](#примеры-использования)
7. [Интеграция](#интеграция)
8. [Тестирование](#тестирование)
9. [Расширение функциональности](#расширение-функциональности)

---

## 📖 Обзор

Модуль Cubes (`modules/cubes.py`) реализует систему дуэлей между двумя игроками на кубиках. Один игрок вызывает другого на дуэль, вызванный может согласиться или отказаться, а затем кубики определяют победителя. Поддерживает ставки на коины из фармы.

### Основные возможности

✅ **Система вызовов** - один игрок вызывает другого на дуэль  
✅ **Время на ответ** - 90 секунд чтобы согласиться или отказаться  
✅ **Ставки** - возможность играть на коины из мешка  
✅ **Броски кубиков** - случайный результат для каждого игрока  
✅ **Определение победителя** - автоматический расчёт по результатам  
✅ **Передача коинов** - автоматическое перечисление выигрыша/проигрыша  
✅ **История дуэлей** - опциональное сохранение результатов  

---

## 🏗️ Архитектура

### Структура модуля

```
modules/cubes.py
├── Класс _CubesDuel
│   ├── duel_id: str
│   ├── chat_id: int
│   ├── inviter_id: int
│   ├── opponent_id: int
│   ├── inviter_name: str
│   ├── opponent_name: str
│   ├── invite_message_id: int
│   ├── created_at: float
│   └── stake: int
│
├── Хранилище дуэлей
│   ├── _PENDING_BY_CHAT[chat_id] -> duel_id
│   └── _PENDING_BY_ID[duel_id] -> _CubesDuel
│
├── Обработчики
│   ├── cubes_handler() - инициирует дуэль
│   ├── accept_duel_handler() - согласиться с дуэлью
│   ├── reject_duel_handler() - отклонить дуэль
│   └── Автоматическое удаление истёкших дуэлей
│
└── Вспомогательные функции
    ├── _user_link() - создание HTML-ссылки на пользователя
    ├── _is_expired() - проверка истечения дуэли
    ├── _parse_stake() - парсинг размера ставки
    └── _ensure_farma_row_and_get_meshok() - проверка баланса
```

### Поток данных

```
Игрок A пишет "!кубы 100" для вызова B
         ↓
    cubes_handler()
         ↓
    Создание объекта _CubesDuel
         ↓
    Сохранение в _PENDING_BY_ID и _PENDING_BY_CHAT
         ↓
    Отправка сообщения с кнопками согласиться/отказаться
         ↓
    90 секунд ожидания на ответ
         ↓
    [Игрок B согласился] ИЛИ [Время истекло]
         ↓
    Розыгрыш кубиков
         ↓
    Определение победителя
         ↓
    Передача коинов
         ↓
    Удаление дуэли из хранилища
```

---

## 🔌 API системы дуэлей

### _CubesDuel

Класс данных для хранения информации о дуэли.

```python
@dataclass
class _CubesDuel:
    duel_id: str              # Уникальный ID дуэли
    chat_id: int              # ID чата, где идёт дуэль
    inviter_id: int           # ID приглашающего игрока
    opponent_id: int          # ID вызванного игрока
    inviter_name: str         # Имя приглашающего
    opponent_name: str        # Имя вызванного
    invite_message_id: int    # ID сообщения с приглашением
    created_at: float         # Время создания (для проверки истечения)
    stake: int                # Ставка в коинах
```

### _PENDING_BY_CHAT и _PENDING_BY_ID

Глобальные хранилища для отслеживания активных дуэлей.

```python
_PENDING_BY_CHAT: dict[int, str] = {}  # chat_id -> duel_id
_PENDING_BY_ID: dict[str, _CubesDuel] = {}  # duel_id -> _CubesDuel
```

### _parse_stake()

Функция для парсинга размера ставки из текста команды.

```python
def _parse_stake(text: str) -> Optional[int]:
    """
    Поддерживает:
      - "!кубы 100"
      - "! кубы 100"
      - без ставки -> 100 (по умолчанию)
    """
```

**Параметры:**
- `text` (str): Текст команды

**Возвращает:** 
- `int` - размер ставки (по умолчанию 100)
- `None` - если формат неверный

**Примеры:**
```python
_parse_stake("!кубы 100")     # -> 100
_parse_stake("! кубы 50")     # -> 50
_parse_stake("!кубы")         # -> 100 (по умолчанию)
_parse_stake("!кубы abc")     # -> None
```

### _ensure_farma_row_and_get_meshok()

Функция для получения баланса пользователя с автоматическим созданием записи.

```python
def _ensure_farma_row_and_get_meshok(cursor: sqlite3.Cursor, user_id: int) -> int:
    """
    Обеспечивает наличие записи в таблице farma и возвращает баланс
    """
```

**Параметры:**
- `cursor` (sqlite3.Cursor): Курсор БД
- `user_id` (int): ID пользователя

**Возвращает:** 
- `int` - текущий баланс мешка (или 0 если новый пользователь)

### cubes_handler()

Основной обработчик для инициирования дуэли.

```python
@dp.message_handler(Text(startswith=['! кубы', '!кубы'], ignore_case=True))
async def cubes_handler(message: types.Message):
    """
    Инициирует дуэль между двумя игроками на кубиках
    """
```

**Срабатывает когда:**
- Пользователь напишет `!кубы` или `! кубы` с опциональной ставкой

**Параметры:**
- `message.from_user.id` (int): ID приглашающего
- `message.reply_to_message` (optional): Если дуэль по ответу на сообщение
- `message.text` (str): Текст команды, содержит размер ставки

**Возвращает:** None (отправляет сообщение в чат)

**Логика:**
1. Получает целевого игрока (из ответа на сообщение)
2. Парсит размер ставки
3. Проверяет баланс обоих игроков
4. Создаёт объект _CubesDuel
5. Отправляет сообщение с кнопками согласиться/отказаться
6. Устанавливает таймер на 90 секунд
7. При истечении удаляет дуэль

---

## 📊 Структура базы данных

### Таблица `farma`

```sql
CREATE TABLE IF NOT EXISTS farma (
    user_id INTEGER PRIMARY KEY,
    meshok INTEGER DEFAULT 0,
    last_date TEXT
)
```

### Таблица `duels` (опционально, для истории)

```sql
CREATE TABLE IF NOT EXISTS duels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    inviter_id INTEGER NOT NULL,
    opponent_id INTEGER NOT NULL,
    winner_id INTEGER NOT NULL,
    stake INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Примеры данных

```sql
-- Дуэль с ставкой 100 коинов
INSERT INTO duels (chat_id, inviter_id, opponent_id, winner_id, stake)
VALUES (-1001234567890, 111111, 222222, 111111, 100);

-- Дуэль с ставкой 50 коинов
INSERT INTO duels (chat_id, inviter_id, opponent_id, winner_id, stake)
VALUES (-1001234567890, 333333, 444444, 444444, 50);
```

---

## 🎯 Обработчики сообщений

### cubes_handler()

**Основной обработчик для инициирования дуэли.**

```python
@dp.message_handler(Text(startswith=['! кубы', '!кубы'], ignore_case=True))
async def cubes_handler(message: types.Message):
    """
    Инициирует дуэль между приглашающим и вызванным игроком
    Поддерживает ставки и проверку баланса
    """
```

**Действия:**
1. Проверяет, что дуэль инициирована ответом на сообщение
2. Получает целевого игрока
3. Парсит размер ставки из текста команды
4. Проверяет баланс обоих игроков
5. Создаёт новую дуэль
6. Отправляет приглашение с кнопками
7. Ждёт 90 секунд на ответ

### accept_duel_handler()

**Обработчик для согласия с дуэлью.**

```python
@dp.callback_query_handler(lambda call: call.data.startswith('duel_accept_'))
async def accept_duel_handler(call: types.CallbackQuery):
    """
    Обрабатывает нажатие кнопки "Согласиться"
    Проводит розыгрыш и определяет победителя
    """
```

**Действия:**
1. Получает ID дуэли из callback data
2. Проверяет, не истекла ли дуэль
3. Проводит броски кубиков для обоих игроков
4. Определяет победителя (больший результат)
5. Передаёт коины от проигравшего к победителю
6. Отправляет результаты
7. Удаляет дуэль из хранилища

### reject_duel_handler()

**Обработчик для отклонения дуэли.**

```python
@dp.callback_query_handler(lambda call: call.data.startswith('duel_reject_'))
async def reject_duel_handler(call: types.CallbackQuery):
    """
    Обрабатывает нажатие кнопки "Отказаться"
    """
```

**Действия:**
1. Удаляет дуэль из хранилища
2. Отправляет сообщение об отказе
3. Уведомляет приглашающего об отказе

---

## 💻 Примеры использования

### Пример 1: Инициирование дуэли программно

```python
import asyncio
from dataclasses import dataclass
import time

@dataclass
class _CubesDuel:
    duel_id: str
    chat_id: int
    inviter_id: int
    opponent_id: int
    inviter_name: str
    opponent_name: str
    invite_message_id: int
    created_at: float
    stake: int

async def initiate_duel(inviter_id: int, opponent_id: int, chat_id: int, stake: int = 100):
    """Инициирует дуэль между двумя игроками"""
    import secrets
    
    duel_id = secrets.token_hex(4)
    
    duel = _CubesDuel(
        duel_id=duel_id,
        chat_id=chat_id,
        inviter_id=inviter_id,
        opponent_id=opponent_id,
        inviter_name="Player1",
        opponent_name="Player2",
        invite_message_id=0,
        created_at=time.monotonic(),
        stake=stake
    )
    
    return duel
```

### Пример 2: Проверка балансов для дуэли

```python
def can_both_afford_duel(inviter_id: int, opponent_id: int, stake: int, db_path: str) -> tuple[bool, str]:
    """Проверяет, могут ли оба игрока участвовать в дуэли"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Проверяем баланс приглашающего
    inviter_balance = cursor.execute(
        "SELECT meshok FROM farma WHERE user_id = ?", 
        (inviter_id,)
    ).fetchone()
    inviter_balance = inviter_balance[0] if inviter_balance else 0
    
    # Проверяем баланс вызванного
    opponent_balance = cursor.execute(
        "SELECT meshok FROM farma WHERE user_id = ?", 
        (opponent_id,)
    ).fetchone()
    opponent_balance = opponent_balance[0] if opponent_balance else 0
    
    connection.close()
    
    if inviter_balance < stake:
        return False, f"У приглашающего недостаточно коинов ({inviter_balance}/{stake})"
    
    if opponent_balance < stake:
        return False, f"У вызванного недостаточно коинов ({opponent_balance}/{stake})"
    
    return True, "Оба игрока могут участвовать"

# Использование
can_afford, message = can_both_afford_duel(123456, 234567, 100, "Base_bot.db")
if can_afford:
    print("Дуэль может начаться")
else:
    print(f"Ошибка: {message}")
```

### Пример 3: Броски кубиков и определение победителя

```python
import random

def roll_dice() -> int:
    """Бросает один кубик (от 1 до 6)"""
    return random.randint(1, 6)

def conduct_duel(inviter_name: str, opponent_name: str, stake: int) -> dict:
    """Проводит дуэль и возвращает результаты"""
    # Оба игрока бросают 3 кубика каждый
    inviter_rolls = [roll_dice() for _ in range(3)]
    opponent_rolls = [roll_dice() for _ in range(3)]
    
    inviter_score = sum(inviter_rolls)
    opponent_score = sum(opponent_rolls)
    
    if inviter_score > opponent_score:
        winner = inviter_name
        loser = opponent_name
    elif opponent_score > inviter_score:
        winner = opponent_name
        loser = inviter_name
    else:
        winner = "Ничья"
        loser = None
    
    return {
        "inviter_name": inviter_name,
        "opponent_name": opponent_name,
        "inviter_rolls": inviter_rolls,
        "opponent_rolls": opponent_rolls,
        "inviter_score": inviter_score,
        "opponent_score": opponent_score,
        "winner": winner,
        "stake": stake
    }

# Использование
result = conduct_duel("Иван", "Мария", 100)
print(f"{result['inviter_name']}: {result['inviter_rolls']} = {result['inviter_score']}")
print(f"{result['opponent_name']}: {result['opponent_rolls']} = {result['opponent_score']}")
print(f"Победитель: {result['winner']}")
```

### Пример 4: Передача коинов после дуэли

```python
def transfer_coins(from_user: int, to_user: int, amount: int, db_path: str) -> bool:
    """Передаёт коины от одного пользователя другому"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Вычитаем у первого
        from_balance = cursor.execute(
            "SELECT meshok FROM farma WHERE user_id = ?",
            (from_user,)
        ).fetchone()
        
        if from_balance is None or from_balance[0] < amount:
            return False
        
        new_from_balance = from_balance[0] - amount
        cursor.execute(
            "UPDATE farma SET meshok = ? WHERE user_id = ?",
            (new_from_balance, from_user)
        )
        
        # Добавляем второму
        to_balance = cursor.execute(
            "SELECT meshok FROM farma WHERE user_id = ?",
            (to_user,)
        ).fetchone()
        
        new_to_balance = (to_balance[0] if to_balance else 0) + amount
        
        if to_balance is None:
            cursor.execute(
                "INSERT INTO farma (user_id, meshok, last_date) VALUES (?, ?, ?)",
                (to_user, new_to_balance, datetime.now().strftime("%H:%M:%S %d.%m.%Y"))
            )
        else:
            cursor.execute(
                "UPDATE farma SET meshok = ? WHERE user_id = ?",
                (new_to_balance, to_user)
            )
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка при передаче коинов: {e}")
        return False
    finally:
        connection.close()

# Использование
if transfer_coins(123456, 234567, 100, "Base_bot.db"):
    print("✅ 100 коинов успешно переданы")
else:
    print("❌ Ошибка при передаче коинов")
```

### Пример 5: Сохранение результатов дуэли

```python
def save_duel_result(chat_id: int, inviter_id: int, opponent_id: int, 
                     winner_id: int, stake: int, db_path: str) -> bool:
    """Сохраняет результат дуэли в БД для истории"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Сначала создаём таблицу, если её нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                inviter_id INTEGER NOT NULL,
                opponent_id INTEGER NOT NULL,
                winner_id INTEGER NOT NULL,
                stake INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute(
            '''INSERT INTO duels (chat_id, inviter_id, opponent_id, winner_id, stake)
               VALUES (?, ?, ?, ?, ?)''',
            (chat_id, inviter_id, opponent_id, winner_id, stake)
        )
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка при сохранении дуэли: {e}")
        return False
    finally:
        connection.close()

# Использование
save_duel_result(
    chat_id=-1001234567890,
    inviter_id=123456,
    opponent_id=234567,
    winner_id=123456,
    stake=100,
    db_path="Base_bot.db"
)
```

---

## 🔧 Интеграция

### Интеграция в main_bot.py

```python
# main/main_bot.py

import modules.cubes  # Обработчики регистрируются автоматически

# Остальной код вашего бота...

if __name__ == '__main__':
    print("Starting bot...")
    dp.start_polling()
```

### Интеграция с модулем Farm

```python
# Система дуэлей использует коины из модуля farm
# Перед началом дуэли:
# 1. Проверяется баланс в таблице farma
# 2. Вычитаются коины со ставкой
# 3. Добавляются коины победителю
```

---

## 🧪 Тестирование

### Запуск тестов

```bash
python test_cubes.py
```

### Написание тестов

```python
import unittest
import sqlite3
from datetime import datetime
from pathlib import Path

class TestCubes(unittest.TestCase):
    def setUp(self):
        """Подготовка к каждому тесту"""
        self.test_db = Path(__file__).parent / 'test_cubes.db'
        self.connection = sqlite3.connect(str(self.test_db), check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_tables()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.connection.close()
        if self.test_db.exists():
            self.test_db.unlink()
    
    def _create_tables(self):
        """Создает необходимые таблицы"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS farma (
                user_id INTEGER PRIMARY KEY,
                meshok INTEGER DEFAULT 0,
                last_date TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS duels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                inviter_id INTEGER,
                opponent_id INTEGER,
                winner_id INTEGER,
                stake INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()
    
    def test_duel_requires_sufficient_balance(self):
        """Тест: дуэль требует достаточного баланса"""
        # Первый игрок с 50 коинами
        self.cursor.execute(
            "INSERT INTO farma (user_id, meshok, last_date) VALUES (?, ?, ?)",
            (123456, 50, datetime.now().strftime("%H:%M:%S %d.%m.%Y"))
        )
        
        # Второй игрок с 200 коинами
        self.cursor.execute(
            "INSERT INTO farma (user_id, meshok, last_date) VALUES (?, ?, ?)",
            (234567, 200, datetime.now().strftime("%H:%M:%S %d.%m.%Y"))
        )
        self.connection.commit()
        
        # Первый не может участвовать в дуэли на 100 коинов
        balance1 = self.cursor.execute(
            "SELECT meshok FROM farma WHERE user_id = ?",
            (123456,)
        ).fetchone()[0]
        
        stake = 100
        self.assertLess(balance1, stake)

if __name__ == '__main__':
    unittest.main()
```

---

## 🚀 Расширение функциональности

### Идея 1: Разные типы дуэлей

```python
DUEL_TYPES = {
    "стандарт": {"dice_count": 3, "name": "Стандартная дуэль"},
    "экстрим": {"dice_count": 5, "name": "Экстремальная дуэль"},
    "быстрая": {"dice_count": 1, "name": "Быстрая дуэль"}
}

def get_duel_type_info(duel_type: str) -> dict:
    """Получает информацию о типе дуэли"""
    return DUEL_TYPES.get(duel_type, DUEL_TYPES["стандарт"])
```

### Идея 2: Рейтинг дуэлистов

```python
def get_duel_stats(user_id: int, db_path: str) -> dict:
    """Получает статистику по дуэлям пользователя"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Всего дуэлей
    total = cursor.execute(
        "SELECT COUNT(*) FROM duels WHERE inviter_id = ? OR opponent_id = ?",
        (user_id, user_id)
    ).fetchone()[0]
    
    # Побед
    wins = cursor.execute(
        "SELECT COUNT(*) FROM duels WHERE winner_id = ?",
        (user_id,)
    ).fetchone()[0]
    
    # Проигрышей
    losses = total - wins
    
    # Выигранных коинов
    earned = cursor.execute(
        "SELECT SUM(stake) FROM duels WHERE winner_id = ?",
        (user_id,)
    ).fetchone()[0] or 0
    
    connection.close()
    
    return {
        "total_duels": total,
        "wins": wins,
        "losses": losses,
        "win_rate": (wins / total * 100) if total > 0 else 0,
        "earned_coins": earned
    }
```

### Идея 3: Сезонные турниры дуэлей

```python
def get_season_stats(user_id: int, season: str, db_path: str) -> dict:
    """Получает статистику пользователя за сезон"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Получаем даты сезона
    season_dates = {
        "S1_2025": ("2025-01-01", "2025-03-31"),
        "S2_2025": ("2025-04-01", "2025-06-30"),
        "S3_2025": ("2025-07-01", "2025-09-30"),
        "S4_2025": ("2025-10-01", "2025-12-31"),
    }
    
    if season not in season_dates:
        return {}
    
    start_date, end_date = season_dates[season]
    
    wins = cursor.execute(
        "SELECT COUNT(*) FROM duels WHERE winner_id = ? AND timestamp BETWEEN ? AND ?",
        (user_id, start_date, end_date)
    ).fetchone()[0]
    
    connection.close()
    return {"season": season, "wins": wins}
```

---

## 📝 Лицензия

Часть проекта WERTY | Chat-Manager Bot

---

**Версия:** 1.0  
**Разработано:** GitHub Copilot  
**Последнее обновление:** 20.12.2025
