# 🎲 Модуль Roulettes (Рулетки) - Полное руководство для разработчиков

**Версия:** 1.0  
**Дата:** 20.12.2025  
**Статус:** ✅ Готово к production  
**Язык:** Python 3.10+  

---

## 📖 Обзор

Проект включает две рулетки:

1. **Golden Roulette** (`modules/golden_rulet.py`) - играем на коины с шансом удвоить или потерять ставку (3/6)
2. **Russian Roulette** (`modules/rus_rulet.py`) - рискованная игра с шансом получить мут (1/6)

---

## 🎰 Golden Roulette (Золотая рулетка)

### Обзор

Игра по принципу классической рулетки: ставите коины, с вероятностью 3/6 выигрываете (ставка удваивается), с вероятностью 3/6 проигрываете (ставка сгорает).

### Основной обработчик

```python
@dp.message_handler(Text(startswith=[
    "! золотая рулетка",
    "!золотая рулетка",
    ".золотая рулетка",
    "/золотая рулетка",
    "золотая рулетка",
], ignore_case=True))
async def golden_roulette(message: types.Message):
    """
    Играем в золотую рулетку
    50% вероятность выигрыша (ставка удваивается)
    50% вероятность проигрыша (ставка теряется)
    """
```

### Логика игры

```python
def play_golden_roulette(stake: int) -> tuple[bool, int]:
    """Проводит раунд золотой рулетки"""
    # Вероятность выигрыша: 3 из 6 (50%)
    outcome = random.randint(1, 6)
    
    if outcome in [1, 2, 3]:  # Выигрыш
        return True, stake * 2  # Ставка удваивается
    else:  # Проигрыш
        return False, 0  # Ставка теряется

# Использование
won, reward = play_golden_roulette(100)
if won:
    print(f"✅ Выигрыш! Получили {reward} коинов")
else:
    print("❌ Проигрыш! Ставка потеряна")
```

### Примеры использования

```python
# Пример 1: Полный цикл игры
async def golden_roulette_cycle(user_id: int, stake: int, db_path: str):
    """Полный цикл игры в золотую рулетку"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Проверяем баланс
    current_balance = cursor.execute(
        "SELECT meshok FROM farma WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]
    
    if current_balance < stake:
        return False, "Недостаточно коинов"
    
    # Вычитаем ставку
    cursor.execute(
        "UPDATE farma SET meshok = ? WHERE user_id = ?",
        (current_balance - stake, user_id)
    )
    
    # Проводим игру
    won, reward = play_golden_roulette(stake)
    
    if won:
        # Добавляем выигрыш
        new_balance = current_balance - stake + reward
        result_text = f"✅ Выигрыш! +{reward} коинов"
    else:
        new_balance = current_balance - stake
        result_text = "❌ Проигрыш! Ставка потеряна"
    
    cursor.execute(
        "UPDATE farma SET meshok = ? WHERE user_id = ?",
        (new_balance, user_id)
    )
    
    connection.commit()
    connection.close()
    
    return True, result_text
```

---

## 🔫 Russian Roulette (Русская рулетка)

### Обзор

Опасная развлекательная игра: с вероятностью 1/6 получаете 5-минутный мут. Это чистый риск, деньги не используются.

### Основной обработчик

```python
@dp.message_handler(Text(startswith=[
    "! русская рулетка",
    "!русская рулетка",
    ".русская рулетка",
    "/русская рулетка",
    "русская рулетка"
], ignore_case=True))
async def russian_roulette(message: types.Message):
    """
    Играем в русскую рулетку
    1/6 вероятность мута на 5 минут
    5/6 выживаешь
    """
```

### Логика игры

```python
def play_russian_roulette() -> bool:
    """Проводит раунд русской рулетки"""
    # 1 из 6 шанс мута
    outcome = random.randint(1, 6)
    return outcome == 1  # True = мут, False = выжил

# Использование
got_muted = play_russian_roulette()
if got_muted:
    print("❌ Получил мут на 5 минут!")
else:
    print("✅ Выжил!")
```

### Примеры использования

```python
# Пример 1: Полный цикл с мутом
async def russian_roulette_cycle(user_id: int, chat_id: int, bot: Bot):
    """Полный цикл русской рулетки с применением мута"""
    MUTE_TIME = 5  # минут
    
    got_muted = play_russian_roulette()
    
    if got_muted:
        # Применяем мут
        permissions = ChatPermissions(can_send_messages=False)
        mute_until = datetime.now() + timedelta(minutes=MUTE_TIME)
        
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=permissions,
            until_date=mute_until
        )
        return "❌ Получил мут на 5 минут!"
    else:
        return "✅ Выжил! 🎉"

# Пример 2: Получение статистики русской рулетки
def get_russian_roulette_stats(user_id: int, db_path: str) -> dict:
    """Получает статистику игрока в русской рулетке"""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Создаём таблицу если её нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS russian_roulette_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                got_muted INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Всего игр
        total_games = cursor.execute(
            "SELECT COUNT(*) FROM russian_roulette_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Сколько раз получил мут
        muted_times = cursor.execute(
            "SELECT COUNT(*) FROM russian_roulette_history WHERE user_id = ? AND got_muted = 1",
            (user_id,)
        ).fetchone()[0]
        
        survive_rate = ((total_games - muted_times) / total_games * 100) if total_games > 0 else 0
        
        return {
            "total_games": total_games,
            "muted_times": muted_times,
            "survive_rate": survive_rate
        }
    finally:
        connection.close()
```

---

## 🎯 Сравнение двух рулеток

| Характеристика | Golden Roulette | Russian Roulette |
|----------------|----------------|-----------------|
| Тип игры | Азартная | Развлекательная |
| Использует коины | ✅ Да | ❌ Нет |
| Шанс выигрыша | 50% (3/6) | 83% (5/6) |
| Шанс проигрыша | 50% (3/6) | 17% (1/6) |
| Результат проигрыша | Потеря коинов | 5-минутный мут |
| Результат выигрыша | Удвоение ставки | Просто выживание |
| Кулдаун | Зависит | Нет |
| Рекомендация | Для любителей риска | Для веселья |

---

## ⚙️ Производительность и безопасность

### Защита от спама

```python
# Golden Roulette имеет встроенный кулдаун
# Russian Roulette может играться без ограничений
# Рекомендуется добавить кулдаун если нужно
```

### Проверка чёрного списка

```python
# Оба модуля проверяют чёрный список перед игрой
if message.from_user.id in black_list:
    await message.answer("В доступе отказано")
    return
```

---

## 🚀 Расширение функциональности

### Идея 1: Комбинированная рулетка

```python
async def super_roulette(user_id: int, stake: int, db_path: str):
    """Суперрулетка: играем на коины И рискуем мутом"""
    won_money, got_muted = play_golden_roulette(stake), play_russian_roulette()
    
    if got_muted:
        return {
            "money_result": won_money,
            "muted": True,
            "message": "Выиграл деньги но получил мут!"
        }
    else:
        return {
            "money_result": won_money,
            "muted": False,
            "message": "Выиграл и не получил мут!"
        }
```

### Идея 2: Прогрессирующий мут

```python
def get_mute_duration(previous_mutes: int) -> int:
    """Определяет длительность мута в зависимости от истории"""
    # Каждый следующий мут дольше
    base = 5  # 5 минут
    multiplier = 1 + (previous_mutes * 0.5)
    return int(base * multiplier)
```

### Идея 3: Серии побед/поражений

```python
def calculate_streak_bonus(streak: int) -> float:
    """Бонус за серию побед в золотой рулетке"""
    if streak <= 1:
        return 1.0
    elif streak <= 3:
        return 1.2
    elif streak <= 5:
        return 1.5
    else:
        return 2.0  # Удвоенный бонус за 5+ побед подряд
```

---

## 📊 Таблицы БД

### Таблица `golden_roulette_history` (опционально)

```sql
CREATE TABLE IF NOT EXISTS golden_roulette_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    stake INTEGER NOT NULL,
    won INTEGER NOT NULL,
    winnings INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Таблица `russian_roulette_history` (опционально)

```sql
CREATE TABLE IF NOT EXISTS russian_roulette_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    got_muted INTEGER NOT NULL,
    mute_duration INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 🐛 Решение проблем

### Проблема: Мут не применяется

**Решение:** Проверьте, что у бота есть права администратора

```python
# Убедитесь, что передаёте правильные параметры
await bot.restrict_chat_member(
    chat_id=chat_id,
    user_id=user_id,
    permissions=ChatPermissions(can_send_messages=False),
    until_date=datetime.now() + timedelta(minutes=5)
)
```

### Проблема: Коины не вычитаются

**Решение:** Убедитесь в вызове `connection.commit()`

```python
cursor.execute("UPDATE farma SET meshok = ? WHERE user_id = ?", (new_balance, user_id))
connection.commit()  # ✅ Обязательно!
```

---

## 📝 Лицензия

Часть проекта WERTY | Chat-Manager Bot

---

**Версия:** 1.0  
**Разработано:** GitHub Copilot  
**Последнее обновление:** 20.12.2025
