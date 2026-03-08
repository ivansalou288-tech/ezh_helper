# 🎮 Модуль Hot-Cold (Холодно-Горячо) - Полное руководство для разработчиков

**Версия:** 1.0  
**Дата:** 20.12.2025  
**Статус:** ✅ Готово к production  
**Язык:** Python 3.10+  

---

## 📖 Обзор

Модуль Hot-Cold (`modules/hot_cold.py`) реализует классическую игру "Угадай число". Бот загадывает число от 1 до 100, а игрок пытается его угадать. После каждой попытки бот подсказывает "холодно" или "горячо".

### Основные возможности

✅ **Загадывание числа** - случайное число от 1 до 100  
✅ **Подсказки** - Холодно/Тепло/Горячо в зависимости от близости  
✅ **Отслеживание игр** - каждый чат имеет свою игру  
✅ **Отмена игры** - команда для остановки текущей игры  
✅ **Безлимитные попытки** - нет ограничений на количество гаданий  

---

## 🎯 Основные обработчики

### start_hot_cold()

Стартует игру в холодно-горячо.

```python
@dp.register_message_handler(start_hot_cold, commands=['хг'], commands_prefix='!/.')
async def start_hot_cold(message: types.Message):
    """
    Начинает игру холодно-горячо
    Загадывает число от 1 до 100
    """
```

**Срабатывает когда:**
- Пользователь напишет `/хг`, `!хг` или `.хг`

**Логика:**
1. Генерирует случайное число от 1 до 100
2. Сохраняет его в словаре `chat_targets` с ключом `chat_id`
3. Отправляет сообщение что игра началась
4. Активирует обработчик гаданий для этого чата

### guess_number()

Обрабатывает попытки угадать число.

```python
@dp.register_message_handler(guess_number, lambda message: message.chat.id in chat_targets)
async def guess_number(message: types.Message):
    """
    Обрабатывает попытку угадать число
    Проверяет результат и отправляет подсказку
    """
```

**Логика:**
1. Парсит число из сообщения пользователя
2. Вычисляет разницу между загаданным и предположением
3. Отправляет подсказку:
   - 🔥 **Горячо** - если разница <= 5
   - ☀️ **Тепло** - если разница <= 15
   - 🧊 **Холодно** - если разница > 15
4. Если угадано - завершает игру и удаляет из `chat_targets`

### cancel_hot_cold()

Отменяет текущую игру.

```python
@dp.register_message_handler(cancel_hot_cold, commands=['стоп-хг'], commands_prefix='!/.')
async def cancel_hot_cold(message: types.Message):
    """
    Отменяет игру холодно-горячо для текущего чата
    """
```

---

## 🏗️ Архитектура

### Структура хранения состояния

```python
# Словарь для хранения загаданного числа для каждого чата
chat_targets: dict[int, int] = {}
# Ключ: chat_id
# Значение: загаданное число
```

### Поток данных

```
Пользователь пишет /хг
         ↓
    start_hot_cold()
         ↓
    Генерируется число (1-100)
         ↓
    Сохраняется в chat_targets[chat_id]
         ↓
    Пользователь пишет число
         ↓
    guess_number()
         ↓
    Вычисляется разница
         ↓
    Отправляется подсказка
         ↓
    Если угадано - удаляется из chat_targets
```

---

## 💻 Примеры использования

### Пример 1: Полный цикл игры

```python
def play_hot_cold_game(target: int, guess: int) -> tuple[bool, str]:
    """Проводит одну попытку в игре"""
    difference = abs(target - guess)
    
    if guess == target:
        return True, "🎉 Поздравляю! Вы угадали число!"
    elif difference <= 5:
        return False, "🔥 Горячо!"
    elif difference <= 15:
        return False, "☀️ Тепло"
    else:
        return False, "🧊 Холодно"

# Использование
target_number = 42
user_guess = 50
is_correct, feedback = play_hot_cold_game(target_number, user_guess)
print(feedback)  # 🔥 Горячо!
```

### Пример 2: Расширенная версия с подсказками

```python
def give_hint(target: int, previous_guesses: list[int]) -> str:
    """Дает подсказку на основе предыдущих попыток"""
    if not previous_guesses:
        return "🔮 Это число между 1 и 100"
    
    low_guesses = [g for g in previous_guesses if g < target]
    high_guesses = [g for g in previous_guesses if g > target]
    
    if low_guesses and high_guesses:
        min_high = min(high_guesses)
        max_low = max(low_guesses)
        return f"💡 Число между {max_low} и {min_high}"
    elif low_guesses:
        return f"💡 Число больше {max(low_guesses)}"
    else:
        return f"💡 Число меньше {min(high_guesses)}"
```

### Пример 3: Сохранение игр и статистики

```python
class GameSession:
    def __init__(self, chat_id: int, target: int):
        self.chat_id = chat_id
        self.target = target
        self.guesses = []
        self.start_time = datetime.now()
    
    def make_guess(self, guess: int) -> tuple[bool, str]:
        """Делает попытку угадать"""
        self.guesses.append(guess)
        
        difference = abs(self.target - guess)
        
        if guess == self.target:
            return True, f"🎉 Угадал за {len(self.guesses)} попыток!"
        elif difference <= 5:
            return False, "🔥 Горячо!"
        elif difference <= 15:
            return False, "☀️ Тепло"
        else:
            return False, "🧊 Холодно"
    
    def get_stats(self) -> dict:
        """Получает статистику игры"""
        duration = datetime.now() - self.start_time
        return {
            "attempts": len(self.guesses),
            "duration": duration,
            "target": self.target,
            "guesses": self.guesses
        }

# Использование
game = GameSession(chat_id=123, target=42)
is_correct, feedback = game.make_guess(50)
print(feedback)  # 🔥 Горячо!
```

### Пример 4: Рейтинг лучших угадывальщиков

```python
def save_game_result(chat_id: int, user_id: int, target: int, 
                     guesses: list, db_path: str) -> bool:
    """Сохраняет результат игры"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_cold_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                target INTEGER NOT NULL,
                attempts INTEGER NOT NULL,
                success INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute(
            '''INSERT INTO hot_cold_games (chat_id, user_id, target, attempts, success)
               VALUES (?, ?, ?, ?, 1)''',
            (chat_id, user_id, target, len(guesses))
        )
        
        connection.commit()
        return True
    finally:
        connection.close()

def get_top_hot_cold_players(chat_id: int, limit: int = 10, db_path: str = "Base_bot.db") -> list:
    """Получает топ игроков по среднему количеству попыток"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        results = cursor.execute('''
            SELECT user_id, AVG(attempts) as avg_attempts, COUNT(*) as games_played
            FROM hot_cold_games
            WHERE chat_id = ?
            GROUP BY user_id
            ORDER BY avg_attempts ASC
            LIMIT ?
        ''', (chat_id, limit)).fetchall()
        
        return results
    finally:
        connection.close()
```

---

## 📊 Таблица БД (опционально)

### Таблица `hot_cold_games`

```sql
CREATE TABLE IF NOT EXISTS hot_cold_games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    target INTEGER NOT NULL,
    attempts INTEGER NOT NULL,
    success INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 🚀 Расширение функциональности

### Идея 1: Разные диапазоны чисел

```python
DIFFICULTY_LEVELS = {
    "easy": (1, 10),
    "normal": (1, 100),
    "hard": (1, 1000),
    "extreme": (1, 10000)
}

async def start_hot_cold_difficulty(message: types.Message, difficulty: str):
    """Начинает игру с выбранной сложностью"""
    min_val, max_val = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["normal"])
    target = random.randint(min_val, max_val)
    chat_targets[message.chat.id] = target
    
    await message.reply(
        f"🎮 Игра началась! Угадайте число от {min_val} до {max_val}"
    )
```

### Идея 2: Ограничение на количество попыток

```python
class LimitedHotCold:
    def __init__(self, target: int, max_attempts: int = 10):
        self.target = target
        self.max_attempts = max_attempts
        self.attempts_left = max_attempts
    
    def make_guess(self, guess: int) -> tuple[bool, str, int]:
        """Делает попытку, возвращает (успех, сообщение, осталось_попыток)"""
        self.attempts_left -= 1
        
        if guess == self.target:
            return True, "🎉 Угадал!", self.attempts_left
        
        if self.attempts_left == 0:
            return False, f"❌ Попытки закончились! Число было {self.target}", 0
        
        difference = abs(self.target - guess)
        if difference <= 5:
            feedback = "🔥 Горячо!"
        elif difference <= 15:
            feedback = "☀️ Тепло"
        else:
            feedback = "🧊 Холодно"
        
        return False, f"{feedback} ({self.attempts_left} попыток осталось)", self.attempts_left
```

### Идея 3: Рейтинги и достижения

```python
def get_hot_cold_achievements(user_id: int, db_path: str) -> list[str]:
    """Получает достижения в игре"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    stats = cursor.execute('''
        SELECT 
            COUNT(*) as games,
            AVG(attempts) as avg_attempts,
            MIN(attempts) as best_game
        FROM hot_cold_games
        WHERE user_id = ?
    ''', (user_id,)).fetchone()
    
    connection.close()
    
    achievements = []
    
    if stats[0] >= 1:
        achievements.append("🎮 Первая игра")
    if stats[0] >= 10:
        achievements.append("🎯 10 игр сыграно")
    if stats[0] >= 50:
        achievements.append("🏆 50 игр сыграно")
    if stats[2] and stats[2] == 1:
        achievements.append("⚡ Угадал с первой попытки!")
    if stats[1] and stats[1] < 5:
        achievements.append("🎪 Средний результат < 5 попыток")
    
    return achievements
```

---

## 🐛 Решение проблем

### Проблема: "Число не сохраняется в памяти"

**Решение:** Используйте словарь `chat_targets` для каждого чата отдельно

```python
chat_targets[message.chat.id] = target_number  # ✅ Правильно
```

### Проблема: "Игра продолжается после угадывания"

**Решение:** Удаляйте чат из `chat_targets` после завершения игры

```python
if guess == target_number:
    del chat_targets[chat_id]  # ✅ Удаляем игру
    await message.reply("🎉 Угадал!")
```

---

## 📝 Лицензия

Часть проекта WERTY | Chat-Manager Bot

---

**Версия:** 1.0  
**Разработано:** GitHub Copilot  
**Последнее обновление:** 20.12.2025
