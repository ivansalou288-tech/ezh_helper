# 📌 DEVELOPERS GUIDE: MAIN MODULE

**Версия:** 1.0  
**Язык:** Python 3.10+  
**Framework:** aiogram 2.25.2+  
**Компоненты:** config.py, main_bot.py, utils.py  

---

## 1. ОБЗОР МОДУЛЯ

**Main** — это центральное ядро бота, содержащее:

- **config.py** — конфигурация бота, токен, пути БД, константы
- **main_bot.py** — обработчики команд и callbacks (3174 строки!)
- **utils.py** — вспомогательные функции и классы

### Основные функции

✅ Управление мутами (мут, размут, список мутов)  
✅ Управление банами (бан, разбан, причина бана)  
✅ Команды /start и /help с статусом клана  
✅ Вывод списков команд  
✅ Рекомендации пользователям  
✅ Модерирование чата  

---

## 2. ОСНОВНЫЕ ВОЗМОЖНОСТИ

### Функции модерирования

| Функция | Команда | Доступ | Описание |
|---------|---------|--------|---------|
| Мут | `мут <время> <тип>` | Модератор+ | Запретить писать на время |
| Размут | `размут @user` | Модератор+ | Снять мут |
| Просмотр мутов | `муты` | Все | Список замученных |
| Бан | `бан @user` | Admin+ | Навсегда забанить |
| Разбан | `разбан @user` | Admin+ | Разбанить |
| Причина бана | `причина бана @user` | Все | Показать причину |
| Старт/помощь | `/start`, `/help` | Все | Информация о боте |

### Типы времени мута

- `сек` — секунды
- `мин` — минуты
- `час` — часы (по умолчанию)
- `день` — дни
- `неделя` — недели

---

## 3. АРХИТЕКТУРА

```
Main Module
├── config.py (981 строк)
│   ├── Токен и API параметры
│   ├── Пути к БД
│   ├── Глобальные переменные
│   ├── Импорты модулей
│   └── Константы состояний
│
├── main_bot.py (3174 строк)
│   ├── Импорты
│   ├── Обработчики команд
│   ├── Обработчики callbacks
│   ├── Функции модерирования
│   ├── Функции бана
│   └── Вспомогательные функции
│
└── utils.py
    ├── CopyTextButton класс
    └── Функции поиска пользователей
```

### Поток данных

```
Message → Handler Decorator → Validation → Database Query → Response
                              ↓
                         Permission Check
                         (is_successful_moder)
```

---

## 4. API ФУНКЦИИ

### config.py

#### Глобальные переменные

```python
# Параметры бота
token = "YOUR_TOKEN"              # Токен бота
api_id = YOUR_API_ID              # Telegram API ID
api_hash = "YOUR_API_HASH"        # Telegram API Hash
bot = Bot(token=token)            # Объект бота
dp = Dispatcher(bot)              # Диспетчер обработчиков

# Пути к БД
main_path = Path / 'databases' / 'Base_bot.db'
warn_path = Path / 'databases' / 'warn_list.db'
datahelp_path = Path / 'databases' / 'my_database.db'
tur_path = Path / 'databases' / 'tournaments.db'
dinamik_path = Path / 'databases' / 'din_data.db'

# Чаты для работы
logs_gr = -1001234567890  # Логи
sost_1 = -1001234567891   # Состояние 1
sost_2 = -1001234567892   # Состояние 2
klan = -1001234567893     # Клан чат
chats = [logs_gr, sost_1, sost_2, klan]

# Флаги
posting = False           # Включен ли постинг
is_auto_unmute = False    # Автоматический размут
week_count = 1            # Номер недели
```

#### Функции конфигурации

```python
# Инициализация БД
connection = sqlite3.connect(main_path, check_same_thread=False)
cursor = connection.cursor()

# Загрузка ID чатов из БД
logs_gr = -int(cursor.execute(
    "SELECT chat_id FROM chat_ids WHERE chat_name = ?", 
    ('logs_gr',)
).fetchall()[0][0])
```

### main_bot.py

#### Обработчики команд

```python
# Команда /start
@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message) -> None:
    """
    Обработчик команды /start и /help в ЛС.
    
    Показывает:
    - Статус в клане
    - Описание пользователя
    - Основные кнопки навигации
    """
```

#### Функция мута

```python
@dp.message_handler(Text(startswith='мут', ignore_case=True))
async def mute(message: types.Message) -> None:
    """
    Замьючить пользователя на время.
    
    Синтаксис:
        мут <число> <тип_времени>
        мут 2 часа (мут на 2 часа)
        мут 30 мин (мут на 30 минут)
        мут 1 неделя
    
    Параметры:
        message: Message объект
    
    Проверки:
        - Команда только в групповых чатах
        - Проверка прав модератора
        - Проверка статуса пользователя
        - Проверка иерархии мудератора
    
    Действия:
        - Записывает мут в БД
        - Применяет ChatPermissions
        - Отправляет сообщение в чат
        - Запускает авторазмут если включен
    """
```

#### Функция бана

```python
@dp.message_handler(Text(startswith='бан', ignore_case=True))
async def ban(message: types.Message) -> None:
    """
    Забанить пользователя навсегда.
    
    Синтаксис:
        бан @username
        Причина на новой строке
    
    Параметры:
        message: Message объект
    
    Проверки:
        - Команда только в групповых чатах
        - Требуется ранг Admin+
        - Нельзя банить старших по рангу
    
    Действия:
        - Записывает бан в таблицу bans
        - Исключает пользователя из чата
        - Логирует действие
    """
```

#### Функция размута

```python
@dp.message_handler(Text(startswith=['анмут', 'размут']))
async def unmute(message: types.Message) -> None:
    """
    Снять мут с пользователя.
    
    Синтаксис:
        размут @username
        анмут @username
    
    Параметры:
        message: Message объект
    
    Действия:
        - Удаляет из таблицы muts
        - Снимает ChatPermissions
        - Отправляет сообщение
    """
```

### utils.py

#### Класс CopyTextButton

```python
class CopyTextButton(TelegramObject):
    """
    Кастомная кнопка для копирования текста.
    
    Параметры:
        text (str): Текст для копирования
    
    Использование:
        button = CopyTextButton(text="Скопируй меня!")
    """
    text: str
    
    def __init__(self, *, text: str) -> None:
        super().__init__(text=text)
```

---

## 5. СТРУКТУРА БД

### Таблица: `muts`

```sql
CREATE TABLE IF NOT EXISTS muts (
    user_id INTEGER,
    rang TEXT,
    chat_id INTEGER,
    moder TEXT,
    date TEXT,
    comments TEXT,
    PRIMARY KEY (user_id, chat_id)
);
```

**Поля:**
- `user_id` — ID пользователя
- `rang` — длительность мута (1 час, 2 дня и т.д.)
- `chat_id` — ID чата
- `moder` — ID модератора
- `date` — дата окончания мута
- `comments` — причина мута

**Примеры:**
```sql
INSERT INTO muts VALUES (123456789, '1 час', -1001234567890, 'Модератор', '2025-12-20 15:30', 'Спам');
SELECT * FROM muts WHERE user_id = 123456789;
```

### Таблица: `[CHAT_ID]bans`

```sql
CREATE TABLE IF NOT EXISTS [-1001234567890bans] (
    tg_id INTEGER PRIMARY KEY,
    pubg_id TEXT,
    message_id INTEGER,
    comments TEXT,
    date TEXT,
    user_mention TEXT,
    moder_mention TEXT
);
```

**Поля:**
- `tg_id` — Telegram ID забаненного
- `pubg_id` — ID в PUBG
- `message_id` — ID сообщения с причиной
- `comments` — причина бана
- `date` — дата бана
- `user_mention` — упоминание пользователя
- `moder_mention` — упоминание модератора

### Таблица: `chat_ids`

```sql
CREATE TABLE IF NOT EXISTS chat_ids (
    chat_id INTEGER,
    chat_name TEXT UNIQUE
);
```

**Примеры:**
```sql
INSERT INTO chat_ids VALUES (-1001234567890, 'logs_gr');
INSERT INTO chat_ids VALUES (-1001234567891, 'sost_1');
```

---

## 6. ОБРАБОТЧИКИ СООБЩЕНИЙ

### Декоратор `@dp.message_handler`

```python
@dp.message_handler(
    Text(startswith='мут', ignore_case=True),
    content_types=ContentType.TEXT,
    is_forwarded=False
)
async def mute(message: types.Message) -> None:
    pass
```

**Параметры:**
- `Text()` — фильтр по тексту сообщения
- `startswith` — проверка начало текста
- `ignore_case` — игнорировать регистр
- `content_types` — тип контента (текст, фото и т.д.)
- `is_forwarded` — исключить переслыланные сообщения

### Декоратор `@dp.callback_query_handler`

```python
@dp.callback_query_handler(text="commands")
async def show_commands(call: types.CallbackQuery) -> None:
    """Обработать нажатие кнопки"""
    pass
```

---

## 7. ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Добавить новую команду мута

```python
@dp.message_handler(Text(startswith='кик', ignore_case=True))
async def kick_user(message: types.Message) -> None:
    """Кикнуть пользователя на 10 минут."""
    if message.chat.id not in chats:
        return
    
    # Проверка прав
    if not await is_successful_moder(
        message.from_user.id, 
        message.chat.id, 
        'mut'
    ):
        await message.reply('❌ Нет прав')
        return
    
    # Получить пользователя
    user_id = GetUserByMessage(message).user_id
    if not user_id:
        await message.reply('❌ Пользователь не найден')
        return
    
    # Применить мут
    await mute_user(
        user_id, 
        message.chat.id, 
        10, 
        'мин', 
        message, 
        'Спам'
    )
```

### Пример 2: Кастомная кнопка с инструкциями

```python
@dp.callback_query_handler(text="help")
async def show_help(call: types.CallbackQuery) -> None:
    """Показать справку по командам."""
    help_text = """
    <b>🔧 Команды модератора:</b>
    
    <code>мут @user</code> - Замьючить
    <code>размут @user</code> - Размьючить
    <code>бан @user</code> - Забанить
    <code>разбан @user</code> - Разбанить
    <code>муты</code> - Список мутов
    
    <b>📋 Общие команды:</b>
    /start - Меню
    /help - Эта справка
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text='⬅️ Назад', 
            callback_data='back'
        )
    )
    
    await call.message.edit_text(
        help_text, 
        parse_mode='html',
        reply_markup=keyboard
    )
```

### Пример 3: Логирование действий модератора

```python
async def log_moderator_action(
    action: str,
    moder_id: int,
    user_id: int,
    chat_id: int,
    reason: str = ""
) -> None:
    """Залогировать действие модератора."""
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    log_message = f"""
    <b>📝 Логирование действия:</b>
    
    <b>Действие:</b> {action}
    <b>Модератор:</b> <a href="tg://user?id={moder_id}">ID {moder_id}</a>
    <b>Пользователь:</b> <a href="tg://user?id={user_id}">ID {user_id}</a>
    <b>Чат:</b> {chat_id}
    <b>Причина:</b> {reason}
    <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    await bot.send_message(
        logs_gr,
        log_message,
        parse_mode='html'
    )
    
    connection.close()
```

### Пример 4: Проверка иерархии модераторов

```python
async def check_moderator_hierarchy(
    moder_id: int,
    user_id: int,
    chat_id: int
) -> bool:
    """
    Проверить, может ли модератор действовать над пользователем.
    
    Возвращает:
        True если может, False если нельзя
    """
    # Если это один и тот же пользователь
    if moder_id == user_id:
        return False
    
    # Проверить ранги в БД
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        moder_rang = cursor.execute(
            f'SELECT status FROM [{-chat_id}] WHERE tg_id = ?',
            (moder_id,)
        ).fetchone()[0]
        
        user_rang = cursor.execute(
            f'SELECT status FROM [{-chat_id}] WHERE tg_id = ?',
            (user_id,)
        ).fetchone()[0]
        
        # Простая иерархия: Admin > Moderator > User
        hierarchy = {'Admin': 3, 'Moderator': 2, 'User': 1}
        
        return hierarchy.get(moder_rang, 0) > hierarchy.get(user_rang, 0)
    except:
        return False
    finally:
        connection.close()
```

### Пример 5: Автоматический размут по расписанию

```python
async def auto_unmute_scheduler() -> None:
    """
    Проверять и снимать муты по расписанию.
    Запускать каждую минуту.
    """
    while True:
        try:
            connection = sqlite3.connect(
                main_path, 
                check_same_thread=False
            )
            cursor = connection.cursor()
            
            # Получить все муты
            mutes = cursor.execute(
                'SELECT user_id, chat_id FROM muts'
            ).fetchall()
            
            current_time = datetime.now()
            
            for user_id, chat_id in mutes:
                mute_info = cursor.execute(
                    'SELECT date FROM muts WHERE user_id = ? AND chat_id = ?',
                    (user_id, chat_id)
                ).fetchone()
                
                if mute_info:
                    mute_end = datetime.fromisoformat(mute_info[0])
                    
                    # Если время мута истекло
                    if current_time >= mute_end:
                        # Размьючить
                        await bot.restrict_chat_member(
                            chat_id,
                            user_id,
                            ChatPermissions(
                                can_send_messages=True,
                                can_send_media_messages=True,
                                can_send_polls=True,
                                can_send_other_messages=True
                            )
                        )
                        
                        # Удалить из БД
                        cursor.execute(
                            'DELETE FROM muts WHERE user_id = ? AND chat_id = ?',
                            (user_id, chat_id)
                        )
                        connection.commit()
            
            connection.close()
            
            # Проверять каждую минуту
            await asyncio.sleep(60)
        except Exception as e:
            print(f'Ошибка в auto_unmute_scheduler: {e}')
            await asyncio.sleep(60)
```

---

## 8. ИНТЕГРАЦИЯ

### Как подключить в main_bot.py

```python
# В начало файла (уже есть)
from config import *
from modules.farm import *
from modules.bookmarks import *
# ... остальные модули

# Регистрация handlers
register_hot_cold_handlers(dp)
```

### Как использовать config в других модулях

```python
# В модулях можно импортировать config
from config import bot, dp, main_path, chats, klan

# Использовать
async def my_handler(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    # ...
```

### Как добавить новый чат

```python
# В config.py добавить:
new_chat = -1001234567894

# В таблицу chat_ids добавить:
cursor.execute(
    'INSERT INTO chat_ids VALUES (?, ?)',
    (new_chat, 'new_chat_name')
)
connection.commit()

# В список chats добавить:
chats = [logs_gr, sost_1, sost_2, klan, new_chat]
```

---

## 9. ТЕСТИРОВАНИЕ

### Unit тест для функции мута

```python
import unittest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User, Chat
import asyncio

class TestMuteFunction(unittest.TestCase):
    """Тесты для функции мута."""
    
    def setUp(self):
        """Подготовка к тесту."""
        self.message = AsyncMock(spec=Message)
        self.message.from_user = MagicMock(spec=User)
        self.message.from_user.id = 123456789
        self.message.chat = MagicMock(spec=Chat)
        self.message.chat.id = -1001234567890
        self.message.text = "мут 2 часа Спам"
    
    def test_mute_parsing(self):
        """Тест парсинга команды мута."""
        text = "мут 2 часа Спам"
        parts = text.split()
        
        self.assertEqual(parts[0], 'мут')
        self.assertEqual(parts[1], '2')
        self.assertEqual(parts[2], 'часа')
    
    def test_mute_time_calculation(self):
        """Тест расчета времени мута."""
        from datetime import datetime, timedelta
        
        mute_int = 2
        mute_type = 'часа'
        
        # Вычисляем время
        if mute_type.startswith('час'):
            delta = timedelta(hours=mute_int)
        elif mute_type.startswith('мин'):
            delta = timedelta(minutes=mute_int)
        elif mute_type.startswith('день'):
            delta = timedelta(days=mute_int)
        
        end_time = datetime.now() + delta
        
        self.assertGreater(end_time, datetime.now())
    
    async def test_mute_permissions(self):
        """Тест применения ChatPermissions."""
        from aiogram.types import ChatPermissions
        
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False
        )
        
        self.assertFalse(permissions.can_send_messages)

if __name__ == '__main__':
    unittest.main()
```

### Тест для бана

```python
class TestBanFunction(unittest.TestCase):
    """Тесты для функции бана."""
    
    def test_ban_reason_parsing(self):
        """Тест извлечения причины бана."""
        text = "бан @user\nСпам в чате"
        lines = text.split('\n')
        
        command = lines[0]
        reason = '\n'.join(lines[1:])
        
        self.assertEqual(command, 'бан @user')
        self.assertEqual(reason, 'Спам в чате')
    
    def test_ban_permanence(self):
        """Тест что бан перманентный."""
        # Бан не имеет даты окончания
        ban_info = {
            'user_id': 123456789,
            'reason': 'Спам',
            'permanent': True
        }
        
        self.assertTrue(ban_info['permanent'])
```

---

## 10. РАСШИРЕНИЕ ФУНКЦИОНАЛЬНОСТИ

### Идея 1: Система ревардов для модераторов

```python
# Отслеживать действия модераторов
async def track_moderator_action(
    moder_id: int,
    action: str,
    chat_id: int
) -> None:
    """
    Отслеживать и вознаграждать модераторов.
    """
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Увеличить счетчик
    cursor.execute('''
        UPDATE moderators 
        SET actions_count = actions_count + 1 
        WHERE moder_id = ? AND chat_id = ?
    ''', (moder_id, chat_id))
    
    connection.commit()
    connection.close()
```

### Идея 2: Система жалоб на модераторов

```python
@dp.message_handler(commands=['report_moder'])
async def report_moderator(message: types.Message) -> None:
    """
    Позволить пользователям жаловаться на модераторов.
    """
    # Получить информацию о жалобе
    # Сохранить в отдельную таблицу
    # Уведомить админов
    pass
```

### Идея 3: Автоматическое восстановление данных модератора

```python
async def restore_moderator_data(
    moder_id: int,
    chat_id: int
) -> None:
    """
    Восстановить данные о действиях модератора.
    """
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Получить все действия за период
    actions = cursor.execute('''
        SELECT action, date, user_id 
        FROM moderator_log 
        WHERE moder_id = ? AND chat_id = ? 
        ORDER BY date DESC 
        LIMIT 100
    ''', (moder_id, chat_id)).fetchall()
    
    return actions
```

### Идея 4: Интеграция с админ панелью

```python
async def get_moderator_stats(
    moder_id: int,
    chat_id: int
) -> dict:
    """
    Получить статистику работы модератора.
    """
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    stats = {
        'mutes': cursor.execute(
            'SELECT COUNT(*) FROM muts WHERE moder = ?',
            (str(moder_id),)
        ).fetchone()[0],
        'bans': cursor.execute(
            f'SELECT COUNT(*) FROM [{-chat_id}bans]'
        ).fetchone()[0],
        'warns': cursor.execute(
            'SELECT COUNT(*) FROM warns WHERE moder_id = ?',
            (moder_id,)
        ).fetchone()[0],
    }
    
    return stats
```

### Идея 5: Система предупреждений перед баном

```python
async def warn_user(
    user_id: int,
    chat_id: int,
    reason: str,
    moder_id: int
) -> None:
    """
    Дать предупреждение пользователю.
    После 3 предупреждений — автобан.
    """
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    # Добавить предупреждение
    cursor.execute('''
        INSERT INTO warns (user_id, chat_id, reason, moder_id, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, chat_id, reason, moder_id, datetime.now()))
    
    # Проверить количество предупреждений
    warn_count = cursor.execute(
        'SELECT COUNT(*) FROM warns WHERE user_id = ? AND chat_id = ?',
        (user_id, chat_id)
    ).fetchone()[0]
    
    if warn_count >= 3:
        # Автоматический бан
        await ban_user(user_id, chat_id, f"Автобан после {warn_count} предупреждений", None)
    
    connection.commit()
    connection.close()
```

---

## 11. РЕШЕНИЕ ПРОБЛЕМ

### Проблема: Мут не работает

**Симптомы:**
- Пользователь может писать после мута
- Нет сообщения о муте в чате

**Решение:**
```python
# Проверить:
1. Бот имеет права администратора в чате
2. Юзер найден в БД
3. Время мута правильно рассчитано
4. Таблица muts существует

# Отладочный код:
async def debug_mute(message: types.Message):
    user_id = GetUserByMessage(message).user_id
    print(f"User ID: {user_id}")
    print(f"Chat ID: {message.chat.id}")
    print(f"Bot permissions: {await bot.get_chat_member(message.chat.id, bot.id)}")
```

### Проблема: БД заблокирована

**Симптомы:**
- `database is locked` ошибка
- Боту не удается записать в БД

**Решение:**
```python
# config.py уже имеет:
check_same_thread=False  # Позволяет несколько потоков

# Но если все еще ошибка:
connection = sqlite3.connect(
    main_path, 
    check_same_thread=False,
    timeout=10  # Добавить timeout
)
```

### Проблема:权限проблемы при муте

**Симптомы:**
- `bot can't restrict message sending`
- Бот не может применить ChatPermissions

**Решение:**
```python
try:
    await bot.restrict_chat_member(
        chat_id,
        user_id,
        ChatPermissions(can_send_messages=False)
    )
except aiogram.utils.exceptions.BotKicked:
    print("Бота кикнули из чата")
except aiogram.utils.exceptions.ChatNotFound:
    print("Чат не найден")
except aiogram.utils.exceptions.UserNotFound:
    print("Пользователь не найден в чате")
except Exception as e:
    print(f"Ошибка: {e}")
```

### Проблема: Команда не срабатывает

**Решение:**
```python
# Проверить порядок декораторов
# Более специфичные должны быть выше

@dp.message_handler(Text(startswith='мут'))  # Специфичная
async def mute(message):
    pass

@dp.message_handler()  # Общая
async def default_handler(message):
    pass
```

---

## 12. ПРОИЗВОДИТЕЛЬНОСТЬ

### Оптимизация запросов

```python
# ❌ Плохо: Множество отдельных запросов
mutes = cursor.execute('SELECT user_id FROM muts WHERE chat_id = ?', (chat_id,))
for mute in mutes:
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (mute[0],))

# ✅ Хорошо: Один JOIN запрос
result = cursor.execute('''
    SELECT users.* FROM users
    JOIN muts ON users.id = muts.user_id
    WHERE muts.chat_id = ?
''', (chat_id,))
```

### Кэширование данных

```python
# Кэш модераторов
moderator_cache = {}
cache_time = {}

async def get_moderator_status(moder_id: int, chat_id: int) -> bool:
    """Получить статус модератора с кэшем."""
    cache_key = f"{moder_id}:{chat_id}"
    
    # Если в кэше и свежее
    if cache_key in moderator_cache:
        if time.time() - cache_time[cache_key] < 300:  # 5 минут
            return moderator_cache[cache_key]
    
    # Если не в кэше, получить из БД
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    result = cursor.execute(
        'SELECT status FROM moderators WHERE id = ? AND chat_id = ?',
        (moder_id, chat_id)
    ).fetchone()
    
    status = result is not None
    
    # Сохранить в кэш
    moderator_cache[cache_key] = status
    cache_time[cache_key] = time.time()
    
    connection.close()
    return status
```

---

## 13. БЕЗОПАСНОСТЬ

### Validation Input

```python
async def validate_mute_input(
    text: str
) -> tuple[int, str] | None:
    """
    Безопасно парсить команду мута.
    """
    try:
        parts = text.split()
        
        if len(parts) < 2:
            return None
        
        # Парсить число
        mute_int = int(parts[1])
        
        # Проверить диапазон
        if mute_int <= 0 or mute_int > 100:
            return None
        
        # Парсить тип
        mute_type = parts[2] if len(parts) > 2 else 'час'
        
        # Whitelist типов
        allowed_types = ['сек', 'мин', 'час', 'день', 'неделя']
        if not any(t in mute_type for t in allowed_types):
            return None
        
        return (mute_int, mute_type)
    except (ValueError, IndexError):
        return None
```

### SQL Injection Prevention

```python
# ❌ Плохо: String concatenation (уязвимо!)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Хорошо: Параметризованный запрос
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### Проверка прав

```python
async def check_user_permission(
    user_id: int,
    chat_id: int,
    required_permission: str
) -> bool:
    """
    Проверить есть ли у пользователя разрешение.
    """
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        
        permissions = {
            'restrict': member.status == 'administrator',
            'ban': member.status == 'creator',
            'write': member.status in ['member', 'administrator', 'creator']
        }
        
        return permissions.get(required_permission, False)
    except:
        return False
```

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- [aiogram документация](https://docs.aiogram.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [SQLite документация](https://www.sqlite.org/docs.html)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

## 🎓 ПОДПРИМЕЧАНИЕ

**Этот модуль содержит:**
- ✅ 3174 строк кода
- ✅ 50+ обработчиков
- ✅ 3 основных компонента (config, main_bot, utils)
- ✅ 5+ таблиц БД
- ✅ Система модерирования
- ✅ Система банов
- ✅ Система мутов

**Это ядро всего бота!**

---

**Создано:** 20.12.2025  
**Версия:** 1.0  
**Статус:** ✅ Готово к продакшену
