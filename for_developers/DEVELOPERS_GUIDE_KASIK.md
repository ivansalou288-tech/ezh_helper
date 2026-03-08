# 🎰 Модуль Kasik (Казино) - Полное руководство для разработчиков

**Версия:** 1.0  
**Дата:** 20.12.2025  
**Статус:** ✅ Готово к production  
**Язык:** Python 3.10+  

---

## 📖 Обзор

Модуль Kasik (`modules/kasik.py`) реализует полнофункциональное казино с игровыми автоматами (слотами). Пользователи ставят коины из фармы и пытаются выиграть. Система включает кулдаун 15 минут, проверку баланса и анимированные результаты.

### Основные возможности

✅ **Выбор ставки** - интерактивное меню с разными размерами ставок  
✅ **Кулдаун 15 минут** - защита от спама  
✅ **Проверка баланса** - автоматическая проверка наличия коинов  
✅ **Слот-машины** - 3 барабана с символами  
✅ **Анимированные результаты** - визуальное отображение вращения  
✅ **Мультипликаторы** - разные выигрыши за разные комбинации  
✅ **История ставок** - сохранение результатов в БД  

---

## 🎯 Основной обработчик

### kasik()

Основная функция для открытия интерфейса казино.

```python
@dp.message_handler(Text(startswith=['! казик', '!казик'], ignore_case=True))
async def kasik(message: types.Message):
    """
    Открывает интерфейс казино с выбором ставки
    """
```

**Срабатывает когда:**
- Пользователь напишет `!казик` или `! казик`

**Логика:**
1. Проверяет, что это групповой чат
2. Проверяет кулдаун (15 минут с последней ставки)
3. Получает баланс мешка пользователя
4. Открывает меню выбора ставки
5. Пользователь выбирает размер ставки (в диапазоне от 10 до его баланса)
6. После выбора ставки вращаются слоты
7. Определяется результат и передаются коины

---

## 📊 Структура базы данных

### Таблица `stavki` (в kasik.db)

```sql
CREATE TABLE IF NOT EXISTS stavki (
    user_id INTEGER PRIMARY KEY,
    last_date TEXT
)
```

### Таблица `kasik_history` (опционально)

```sql
CREATE TABLE IF NOT EXISTS kasik_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    stake INTEGER NOT NULL,
    result TEXT NOT NULL,
    winnings INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 💻 Примеры использования

### Пример 1: Проверка кулдауна казино

```python
def can_play_kasik(user_id: int, db_path: str) -> tuple[bool, str]:
    """Проверяет, может ли пользователь играть в казино"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        last_date_str = cursor.execute(
            "SELECT last_date FROM stavki WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        last_date = datetime.strptime(last_date_str, "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - last_date
        
        if delta >= timedelta(minutes=15):
            return True, "Можете играть"
        else:
            remaining = timedelta(minutes=15) - delta
            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60
            return False, f"Подождите {minutes}:{seconds:02d}"
    except (IndexError, TypeError):
        return True, "Первая ставка"
    finally:
        connection.close()
```

### Пример 2: Обработка результата слотов

```python
SLOT_SYMBOLS = {
    "🍊": 10,
    "🍋": 20,
    "🍒": 30,
    "⭐": 50,
    "💎": 100
}

def generate_slot_result() -> tuple[str, str, str, int]:
    """Генерирует результат слотов"""
    symbols = list(SLOT_SYMBOLS.keys())
    
    slot1 = random.choice(symbols)
    slot2 = random.choice(symbols)
    slot3 = random.choice(symbols)
    
    # Расчёт выигрыша
    if slot1 == slot2 == slot3:
        # Все три символа совпадают - большой выигрыш
        multiplier = 10
    elif slot1 == slot2 or slot2 == slot3:
        # Два символа совпадают
        multiplier = 3
    else:
        # Нет совпадений
        multiplier = 0
    
    return slot1, slot2, slot3, multiplier

# Использование
slot1, slot2, slot3, multiplier = generate_slot_result()
print(f"Результат: {slot1} {slot2} {slot3}")
print(f"Множитель: {multiplier}x")

stake = 100
winnings = stake * multiplier
print(f"Выигрыш: {winnings} коинов")
```

### Пример 3: Сохранение результата ставки

```python
def save_kasik_result(user_id: int, chat_id: int, stake: int, 
                      result: str, winnings: int, db_path: str) -> bool:
    """Сохраняет результат ставки в историю"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kasik_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                stake INTEGER NOT NULL,
                result TEXT NOT NULL,
                winnings INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute(
            '''INSERT INTO kasik_history (user_id, chat_id, stake, result, winnings)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, chat_id, stake, result, winnings)
        )
        
        # Обновляем дату последней ставки
        cursor.execute(
            "INSERT OR REPLACE INTO stavki (user_id, last_date) VALUES (?, ?)",
            (user_id, datetime.now().strftime("%H:%M:%S %d.%m.%Y"))
        )
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False
    finally:
        connection.close()
```

### Пример 4: Получение статистики казино

```python
def get_kasik_stats(user_id: int, db_path: str) -> dict:
    """Получает статистику игрока в казино"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Всего ставок
        total_bets = cursor.execute(
            "SELECT COUNT(*) FROM kasik_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Всего поставлено
        total_staked = cursor.execute(
            "SELECT SUM(stake) FROM kasik_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0] or 0
        
        # Всего выиграно
        total_winnings = cursor.execute(
            "SELECT SUM(winnings) FROM kasik_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0] or 0
        
        # Баланс
        balance = total_winnings - total_staked
        
        return {
            "total_bets": total_bets,
            "total_staked": total_staked,
            "total_winnings": total_winnings,
            "balance": balance,
            "roi": (balance / total_staked * 100) if total_staked > 0 else 0
        }
    finally:
        connection.close()

# Использование
stats = get_kasik_stats(123456, "kasik.db")
print(f"Всего ставок: {stats['total_bets']}")
print(f"Выигрыш/проигрыш: {stats['balance']}")
print(f"ROI: {stats['roi']:.2f}%")
```

---

## 🚀 Расширение функциональности

### Идея 1: Прогрессивный джекпот

```python
class ProgressiveJackpot:
    def __init__(self, initial: int = 1000):
        self.base_amount = initial
        self.current = initial
    
    def add_to_jackpot(self, amount: int):
        """Добавляет сумму в джекпот"""
        self.current += amount
    
    def win_jackpot(self) -> int:
        """Выигрывает джекпот и сбрасывает"""
        won = self.current
        self.current = self.base_amount
        return won
    
    def get_jackpot(self) -> int:
        """Получает текущий размер джекпота"""
        return self.current

# Использование
jackpot = ProgressiveJackpot()
jackpot.add_to_jackpot(100)  # Каждая ставка добавляет в джекпот
if lucky:
    won_amount = jackpot.win_jackpot()
```

### Идея 2: Бонус-раунды и мультипликаторы

```python
def calculate_bonus_multiplier(bet_count: int) -> float:
    """Возвращает бонусный множитель за количество ставок подряд"""
    if bet_count < 5:
        return 1.0
    elif bet_count < 10:
        return 1.1  # +10%
    elif bet_count < 20:
        return 1.2  # +20%
    else:
        return 1.3  # +30%

# Использование
multiplier = calculate_bonus_multiplier(15)
final_winnings = int(base_winnings * multiplier)
```

### Идея 3: Система уровней и привилегий

```python
KASIK_LEVELS = {
    1: {"min_bets": 0, "min_coins": 0, "name": "Новичок"},
    2: {"min_bets": 10, "min_coins": 100, "name": "Любитель"},
    3: {"min_bets": 50, "min_coins": 500, "name": "Профессионал"},
    4: {"min_bets": 100, "min_coins": 1000, "name": "Легенда"},
}

def get_kasik_level(user_id: int, db_path: str) -> tuple[int, dict]:
    """Определяет уровень игрока в казино"""
    stats = get_kasik_stats(user_id, db_path)
    
    for level_id in sorted(KASIK_LEVELS.keys(), reverse=True):
        level_info = KASIK_LEVELS[level_id]
        if stats['total_bets'] >= level_info['min_bets']:
            return level_id, level_info
    
    return 1, KASIK_LEVELS[1]
```

---

## 📝 Лицензия

Часть проекта WERTY | Chat-Manager Bot

---

**Версия:** 1.0  
**Разработано:** GitHub Copilot  
**Последнее обновление:** 20.12.2025
