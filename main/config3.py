import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main.secret import main_token as token, main_token as bot_token
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram import Bot, Dispatcher, types
import asyncio
#?from config import *
import sqlite3
from aiogram.exceptions import *

# from main.utils import CopyTextButton
from pathlib import Path
import requests
from googletrans import Translator

#? EN: Bot initialization
#* RU: Инициализация ботa


states = ['246. Нарушение правил охраны окружающей среды при производстве работ',
          '273. Создание, использование и распространение вредоносных компьютерных программ',
          '110. Доведение до самоубийства',
          '359. Наемничество',
          '267.1. Действия, угрожающие безопасной эксплуатации транспортных средств',
          '343. Нарушение правил несения службы по охране общественного порядка и обеспечению общественной безопасности',
          '300. Незаконное освобождение от уголовной ответственности',
          '131 УК РФ. Изнасилование определяется Уголовным кодексом как половое сношение с применением насилия или с угрозой его применения к потерпевшей или к другим лицам либо с использованием беспомощного состояния потерпевшей',
          '1488 УК. КВ. Поздравляю! Ты выйграл купон на антимут, действует сутки',
          '228 УК. КВ. Поздравляю! Тебе очень повезло, теперь у тебя бесплатный купон на пиздюля от пикачу',
          '225. Ненадлежащее исполнение обязанностей по охране оружия, боеприпасов, взрывчатых веществ и взрывных устройств',
          '158. Кража — тайное хищение чужого имущества. Наказание: штраф, обязательные работы или лишение свободы.',
          '159. Мошенничество — хищение имущества путём обмана или злоупотребления доверием. Часто связано с финансовыми махинациями и подлогом.',
          '167. Умышленное уничтожение или повреждение чужого имущества.',
          '161. Грабёж — открытое хищение чужого имущества без применения опасного насилия.',
          '222. Незаконное хранение, перевозка или сбыт оружия и боеприпасов.',
          '327. Подделка, изготовление или использование подложных документов.',
          '264. Нарушение правил дорожного движения, повлекшее причинение вреда здоровью.',
          '272. Неправомерный доступ к компьютерной информации.',
          '223. Незаконное изготовление оружия и взрывных устройств.',
          '128.1. Клевета — распространение заведомо ложных сведений.',
          '180. Незаконное использование товарного знака.',
          '176. Незаконное получение кредита.',
          '292. Служебный подлог — внесение заведомо ложных сведений в документы.',
          '138. Нарушение тайны телефонных переговоров и переписки.',
          '168. Уничтожение имущества по неосторожности.',
          '171. Незаконное предпринимательство.',
          '198. Уклонение от уплаты налогов физическим лицом.',
          '216. Нарушение правил безопасности при ведении строительных работ.',
          '137. Нарушение неприкосновенности частной жизни.',
          '165. Причинение имущественного ущерба без хищения.',
          '183. Незаконное получение и разглашение коммерческой тайны.',
          '306. Заведомо ложный донос.',
          '330. Самоуправство — самовольное осуществление своих мнимых прав.',
          '267. Приведение в негодность транспорта.',
          '327.1. Подделка акцизных марок.',
          '238.1. Оборот фальсифицированных лекарств.',
          '294. Воспрепятствование правосудию.',
          ''
          
        ]
curent_path = (Path(__file__)).parent.parent
all_path = curent_path / 'databases' / 'All.db'
admin_path = curent_path / 'databases' / 'admin.db'
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'


#? EN: Import working chat IDs from database
#* RU: Импорт ID рабочих чатов из базы данных
connection = sqlite3.connect(main_path, check_same_thread=False)
cursor = connection.cursor()
logs_gr = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('logs_gr',)).fetchall()[0][0])
sost_1 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_1',)).fetchall()[0][0])
sost_2 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_2',)).fetchall()[0][0])
klan = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchall()[0][0])



# print(chats)
#? EN: For posting functionality
#* RU: Для работы постинга
monday = "Доброе утром пидоры! \nПидор 1 наблюдает, Пидор 2 на подстраховке, Пидор 3 на подстраховке подсраховки, Пидор 4 на манагере, а Верти юрец"
tuesday="Доброе утро пидоры! \nПидор 1 наблюдает, Пидор 2 на подстраховке, Пидор 3 на подстраховке подсраховки, Пидор 4 на манагере, а Верти юрец"
wednesday="Доброе утро пидоры! \nПидор 1 наблюдает, Пидор 2 на подстраховке, Пидор 3 на подстраховке подсраховки, Пидор 4 на манагере, а Верти юрец"
thursday="Доброе утро пидоры! \nПидор 1 наблюдает, Пидор 2 на подстраховке, Пидор 3 на подстраховке подсраховки, Пидор 4 на манагере, а Верти юрец"
friday="Доброе утро пидоры! \nПидор 1 наблюдает, Пидор 2 на подстраховке, Пидор 3 на подстраховке подсраховки, Пидор 4 на манагере, а Верти юрец"
saturday="Доброе утро пидоры! \nПидор 1 наблюдает, Пидор 2 на подстраховке, Пидор 3 на подстраховке подсраховки, Пидор 4 на манагере, а Верти юрец"
sunday="Доброе утро пидоры! \nПидор 1 наблюдает, Пидор 2 на подстраховке, Пидор 3 на подстраховке подсраховки, Пидор 4 на манагере, а Верти юрец"
week_count = 1
posting = False

gal = '<tg-emoji emoji-id="5462919317832082236">✅</tg-emoji>'
dance_cat = '<tg-emoji emoji-id="5235465481992809720">🐈</tg-emoji>'
block = '<tg-emoji emoji-id="5240241223632954241">🚫</tg-emoji>'
voscl = '<tg-emoji emoji-id="5440660757194744323">❗</tg-emoji>'
soziv = '<tg-emoji emoji-id="5424818078833715060">📢</tg-emoji>'
dance_ezh = '<tg-emoji emoji-id="6262672546521423618">🦔</tg-emoji>'
mes_em = '<tg-emoji emoji-id="5443038326535759644">💬</tg-emoji>'
mut_em = '<tg-emoji emoji-id="5462990730253319917">🔇</tg-emoji>'
time_em = '<tg-emoji emoji-id="5440621591387980068">🕰️</tg-emoji>'
zloy_cat = '<tg-emoji emoji-id="5235850315357497516">👿</tg-emoji>'
unmut_em = '<tg-emoji emoji-id="5388632425314140043">🔊</tg-emoji>'
desk_em = '<tg-emoji emoji-id="5413879192267805083">🗓️</tg-emoji>'
write_em = '<tg-emoji emoji-id="5215209935188534658">📝</tg-emoji>'
circle_em = '<tg-emoji emoji-id="5411225014148014586">🔴</tg-emoji>'
znak_yelow = '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji>'
krest = '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji>'
money = '<tg-emoji emoji-id="5422444280473998663">🍊</tg-emoji>'
mesh_money = '<tg-emoji emoji-id="5224257782013769471">💰</tg-emoji>'
#? EN: Who can recommend and remove recommendations
#* RU: Кто может рекомендовать и снимать рекомендации
can_recommend_users = [8015726709, 1401086794, 1240656726, 5714854312, 1803851598, 5740021109]
can_snat_recommend_users = [8015726709, 1401086794, 1240656726]

#? EN: For proper activation of auto-unmute and quests
#* RU: Для правильной активации автоанмута и квестов
is_auto_unmute = False
is_quests = False

#? EN: For viewing removed warnings functionality
page = 0
mes_id = 0
itog = []
page_c = 0

def get_db_path(chat_id):
    db_path = curent_path / 'databases' / f'{-chat_id}.db'
    return db_path

def init_chat_db(chat_id):
    """Initialize database for a specific chat from {-chat_id}.sql file"""
    db_path = get_db_path(chat_id)
    sql_file_path = curent_path / '{-chat_id}.sql'
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Read and execute SQL from file
    if sql_file_path.exists():
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
    else:
        # Fallback to hardcoded structure if file doesn't exist
        create_fallback_tables(cursor)
    
    connection.commit()
    connection.close()

def init_all_db():
    """Initialize All.db database from all.sql file"""
    db_path = curent_path / 'databases' / 'All.db'
    sql_file_path = curent_path / 'all.sql'
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Read and execute SQL from file
    if sql_file_path.exists():
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
    else:
        # Fallback structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER,
                chat_id INTEGER,
                rang INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, chat_id)
            )
        ''')
    
    connection.commit()
    connection.close()

def init_admin_db():
    """Initialize admin.db database from admin.sql file"""
    db_path = curent_path / 'databases' / 'admin.db'
    sql_file_path = curent_path / 'admin.sql'
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Read and execute SQL from file
    if sql_file_path.exists():
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
    else:
        # Fallback structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER,
                chat_id INTEGER,
                chat_name TEXT,
                can_see_users INTEGER,
                can_do_admin INTEGER,
                can_recom INTEGER,
                can_links INTEGER,
                can_dk INTEGER
            )
        ''')
    
    connection.commit()
    connection.close()

def create_fallback_tables(cursor):
    """Fallback table creation if SQL files are not available"""
    # Create basic tables structure here as fallback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            nik_pubg TEXT NOT NULL,
            id_pubg INTEGER NOT NULL,
            nik TEXT,
            rang INTEGER NOT NULL DEFAULT 0,
            last_date TEXT,
            date_vhod TEXT DEFAULT 'Неизвестно',
            mess_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dk (
            comand TEXT PRIMARY KEY,
            dk INTEGER
        )
    ''')
    
    # Insert default commands
    default_commands = [
        ('ban', 3), ('mut', 2), ('warn', 2), ('all', 3),
        ('rang', 4), ('dk', 4), ('change_pravils', 4),
        ('close_chat', 4), ('change_priv', 4), ('obavlenie', 4),
        ('tur', 1), ('dell', 1), ('period', 4)
    ]
    
    texts = [
        ('priv', 'Добро пожаловать!'),
        ('rules', '')
    ]
    default_periods = [
        ('mut', "1 час", -1003012971064),
        ('all', "3 минуты", -1003012971064),
        ('kasik', "5 минут", -1003012971064)
    ]
    for command, dk_value in default_commands:
        cursor.execute('INSERT OR IGNORE INTO dk (comand, dk) VALUES (?, ?)', (command, dk_value))
    
    for text_name, txt in texts:
        cursor.execute('INSERT OR IGNORE INTO texts (text_name, text) VALUES (?, ?)', (text_name, txt))



#? EN: Class to extract user information from a message (reply, mention, or ID)
#* RU: Класс для извлечения информации о пользователе из сообщения (ответ, упоминание или ID)
class GetUserByMessage:
    def __init__(self, message):
        self.message = message
        self.chat_id = message.chat.id
        self.user_id = self.getUserId(self.message)
        # self.self_user_id = self.getSelfUserId(self.message)
        self.username = self.getUsernameByID(self.user_id)
        self.name = self.getNameByID(self.user_id, self.chat_id)
        self.pubg_id = self.getPubgidByID(self.user_id, self.chat_id)
        self.pubg_nik = self.getPubgNikByID(self.user_id, self.chat_id)
        self.nik = self.getNikByID(self.user_id, self.chat_id)
        self.rang = self.getRangByID(self.user_id, self.chat_id)
        self.last_date = self.getLastDateByID(self.user_id, self.chat_id)
        self.date_vhod = self.getDateVhodByID(self.user_id, self.chat_id)

    def getUserId(self, message):
        # Initialize database for this chat if it doesn't exist
        
        connection = sqlite3.connect(get_db_path(self.chat_id), check_same_thread=False)
        cursor = connection.cursor()

        try:
            user_id = int(self.message.text.split('tg://openmessage?user_id=')[1].split()[0])
            return user_id
        except IndexError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass
        try:
            user_id = int(self.message.text.split('@')[1].split()[0])
            return user_id
        except ValueError:
            pass
        except IndexError:
            pass
        try:
            connection = sqlite3.connect(all_path, check_same_thread=False)
            cursor = connection.cursor()
            username = (message.text.split('@')[1]).split()[0]
            user_id = int(
                cursor.execute(f"SELECT user_id FROM all_users WHERE username=?", (username,)).fetchall()[0][0])
            return user_id
        except IndexError:
            pass

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            return user_id
        else:
            return False

    def getUsernameByID(self, user_id):
        connection = sqlite3.connect(all_path, check_same_thread=False)
        cursor = connection.cursor()
        try:
            username = cursor.execute(f"SELECT username FROM all_users WHERE user_id=?", (self.user_id,)).fetchall()[0][0]
            return username
        except IndexError:
            return 'Отсутвует'

    def getNameByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
       
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            name = cursor.execute(f"SELECT name FROM users WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return name
        except IndexError:
            return 'Отсутвует'

    def getPubgidByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
       
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            pubg_id = cursor.execute(f"SELECT id_pubg FROM users WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return pubg_id
        except IndexError:
            return 'Отсутвует'

    def getPubgNikByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
        init_chat_db(chat_id)
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            pubg_nik = cursor.execute(f"SELECT nik_pubg FROM users WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return pubg_nik
        except IndexError:
            return 'Отсутвует'
    def getNikByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
        
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            nik = cursor.execute(f"SELECT nik FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return nik
        except IndexError:
            return 'Отсутвут'



    def getRangByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
       
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            rang = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return rang
        except IndexError:
            return 'Отсутвует'

    def getLastDateByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
        
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            last_date = cursor.execute(f"SELECT last_date FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return last_date
        except IndexError:
            return 'Отсутвует'

    def getDateVhodByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
    
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            date_vhod = cursor.execute(f"SELECT date_vhod FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return date_vhod
        except IndexError:
            return 'Отсутвует'


#? EN: Class to get user information by their Telegram ID
#* RU: Класс для получения информации о пользователе по его Telegram ID
class GetUserByID:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.username = self.getUsernameByID(self.user_id)
        self.name = self.getNameByID(self.user_id, self.chat_id)
        self.pubg_id = self.getPubgidByID(self.user_id, self.chat_id)
        self.pubg_nik = self.getPubgNikByID(self.user_id, self.chat_id)
        self.nik = self.getNikByID(self.user_id, self.chat_id)
        self.rang = self.getRangByID(self.user_id, self.chat_id)
        self.last_date = self.getLastDateByID(self.user_id, self.chat_id)
        self.date_vhod = self.getDateVhodByID(self.user_id, self.chat_id)
        self.mention = self.getUserMention(self.user_id, self.chat_id)

    def getUsernameByID(self, user_id):
        connection = sqlite3.connect(all_path, check_same_thread=False)
        cursor = connection.cursor()
        try:
            username = cursor.execute(f"SELECT username FROM all_users WHERE user_id=?", (self.user_id,)).fetchall()[0][0]
            return username
        except IndexError:
            return 'Пользователь'

    def getNameByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
        
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            name = cursor.execute(f"SELECT name FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return name
        except IndexError:
            return 'Пользователь'

    def getPubgidByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
     
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            pubg_id = int(cursor.execute(f"SELECT id_pubg FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0])
            return pubg_id
        except IndexError:
            return 'Отсутвует'

    def getPubgNikByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
       
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            pubg_nik = cursor.execute(f"SELECT nik_pubg FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return pubg_nik
        except IndexError:
            return 'Пользователь'

    def getRangByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
     
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            rang = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return rang
        except IndexError:
            return 'Обычный участник'

    def getLastDateByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
      
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            last_date = cursor.execute(f"SELECT last_date FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return last_date
        except IndexError:
            return 'Отсутвует'
    def getNikByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
        
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            nik = cursor.execute(f"SELECT nik FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return nik
        except IndexError:
            return 'Отсутвует'

    def getDateVhodByID(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
      
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            date_vhod = cursor.execute(f"SELECT date_vhod FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
            return date_vhod
        except IndexError:
            return 'Отсутвует'
    def getUserMention(self, user_id, chat_id):
        # Initialize database for this chat if it doesn't exist
 
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
        cursor = connection.cursor()
        try:
            name = cursor.execute(f"SELECT nik FROM users WHERE tg_id=?", (user_id,)).fetchall()[0][0]
        except IndexError:
            name = 'Пользователь'
        
        mention = f'<a href="tg://user?id={user_id}">{name}</a>'
        return mention

#? EN: Retrieves and formats user recommendations from database
#* RU: Получает и форматирует рекомендации пользователя из базы данных
async def recom_check_sdk(tg_id, name_user, chat_id):
    connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
    cursor = connection.cursor()
    moder_gives = []
    moder_rang = []
    comments = []
    rang = []
    date = []
    itog = []
    all = cursor.execute('SELECT * FROM recommendation WHERE user_id = ?', (tg_id,)).fetchall()
    print(all)
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    recommendation_count = 0
    for i in all:
        recommendation_count += 1



    for i in range(recommendation_count):
        moder_gives.append(all[i][2])

    for i in range(recommendation_count):
        comments.append(all[i][3])

    for i in range(recommendation_count):
        rang.append(all[i][4])

    for i in range(recommendation_count):
        date.append(all[i][5])

    for moder in moder_gives:
        try:
            id = int(moder)
        except ValueError:
            id = moder
        try:
            rang_m = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (id,)).fetchall()[0][0]
            # Ensure rang value is within bounds
            if rang_m < 0:
                rang_m = 0
            elif rang_m >= len(rangs_name):
                rang_m = len(rangs_name) - 1
            moder_rang.append(rangs_name[rang_m])
        except IndexError:
            moder_rang.append('Неизвестная должность')

    for i in range(recommendation_count):
        try:
            name_mod = cursor.execute(f"SELECT nik FROM users WHERE tg_id=?", (int(moder_gives[i]),)).fetchall()[0][0]
        except IndexError:
            name_mod = moder_gives[i]
        except ValueError:
            name_mod = moder_gives[i]
        textt = f'🟢 <b>{i+1}</b>. От <a href="tg://user?id={moder_gives[i]}">{name_mod}</a> | Должность: <b>{moder_rang[i]}</b>\n<b>&#8195Чем отличился:</b> {comments[i]}\n<b>&#8195Рекомендован на:</b> {rang[i]}\n<b>&#8195Дата рекомендации: {date[i]}</b>'
        itog.append(textt)
    text = '\n\n'.join(itog)
    if text == '':
        text = f'📝Рекомендации <a href="tg://user?id={tg_id}">{name_user}</a> отсутвуют'
    else:
        text = f'📝Рекомендации <a href="tg://user?id={tg_id}">{name_user}</a>:\n\n{text}'
    return text


#? EN: Retrieves and formats user warnings from database
#* RU: Получает и форматирует предупреждения пользователя из базы данных
async def warn_check_sdk(tg_id, chat_id, name_user):
    # Используем базу данных конкретного чата
    connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM warns WHERE user_id=?", (tg_id,))
    try:
        warns = cursor.fetchall()
        if not warns:
            # Нет предупреждений
            text = f'<b>❕Предупреждения</b> <a href="tg://user?id={tg_id}">{name_user}</a> отсутсвуют! Поздравляем!'
            return text
        
        warns_count = len(warns)
        
        # Формируем текст предупреждений
        warn_texts = []
        for i, warn in enumerate(warns, 1):
            reason = warn[1] if warn[1] else 'Без причины'
            moder_id = warn[2]
            date = warn[3] if warn[3] else 'Неизвестна'
            
            # Получаем имя модератора
            try:
                moder_connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
                moder_cursor = moder_connection.cursor()
                moder_cursor.execute("SELECT nik FROM users WHERE tg_id=?", (moder_id,))
                moder_result = moder_cursor.fetchall()
                moder_name = moder_result[0][0] if moder_result else f"ID: {moder_id}"
                moder_connection.close()
            except:
                moder_name = f"ID: {moder_id}"
            
            warn_text = f'🔺 {i}. От {moder_name}:\n&#8195&#8194Причина: {reason}\n&#8195&#8194Дата: {date}'
            warn_texts.append(warn_text)
        
        all_warns_text = '\n\n'.join(warn_texts)
        
        if warns_count == 1:
            text = f'❕Пользователь <a href="tg://user?id={tg_id}">{name_user}</a> имеет {warns_count} предупреждение\n\n{all_warns_text}'
        elif warns_count <= 4:
            text = f'❕Пользователь <a href="tg://user?id={tg_id}">{name_user}</a> имеет {warns_count} предупреждения\n\n{all_warns_text}'
        else:
            text = f'❕Пользователь <a href="tg://user?id={tg_id}">{name_user}</a> имеет {warns_count} предупреждений\n\n{all_warns_text}'
        
        return text
        
    except Exception as e:
        print(f"Error in warn_check_sdk: {e}")
        text = f'<b>❕Предупреждения <a href="tg://user?id={tg_id}">{name_user}</a> отсутвуют! Поздравляем!</b>'
        return text

#? EN: Checks if user is first time seen in warning database
#* RU: Проверяет, впервые ли пользователь попадает в базу предупреждений
def firstSeen(tg_id, message):
    chat_db_path = get_db_path(message.chat.id)
    connection = sqlite3.connect(chat_db_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT user_id FROM warns WHERE user_id=?", (tg_id,))
    rez = cursor.fetchall()
    if not rez:
        return True
    else:
        return False

#? EN: Retrieves and formats user profile information from database
#* RU: Получает и форматирует информацию о профиле пользователя из базы данных
async def about_user_sdk(user_id, chat_id):
    chat_db_path = get_db_path(chat_id)
    connection = sqlite3.connect(chat_db_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE tg_id=?", (user_id,))
    users = cursor.fetchall()

    if not users:
        return "Пользователь не найден в базе данных."

    user_about = {}
    for user in users:
        user_about = {
            'tg_id': user[0],
            'usename': user[1],
            'name': user[2],
            'age': user[3],
            'nik_pubg': user[4],
            'id_pubg': user[5],
            'nik': user[6],
            'rang': user[7],
            'last_date': user[8],
            'date_vhod': user[9],
        }

    # Выводим в нормальном формате описание

    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    print(rangs_name[4])
    sm = "🎄"
    stars = ""
    try:
        rang_value = int(user_about['rang'])
        # Ensure rang value is within bounds
        if rang_value < 0:
            rang_value = 0
        elif rang_value >= len(rangs_name):
            rang_value = len(rangs_name) - 1
        
        for i in range(rang_value):
            stars += sm
        if user_about['last_date'] == '' or user_about['last_date'] == None:
            last_date = 'Неизвестно'
    except (UnboundLocalError, ValueError, TypeError):
        return
    else:
        last_date = user_about['last_date']
    text = f"{stars} [{user_about['rang']}] Ранг: <b>{rangs_name[rang_value]}</b>\n<b>👤Имя: </b>{user_about['name']}\n<b>🎂Возраст:</b> {user_about['age']}\n<b>🏷️Клановый Ник:</b> {user_about['nik']}\n<b>👾Игровой Ник:</b> {user_about['nik_pubg']}\n<b>🎮Игровой айди:</b> <code>{user_about['id_pubg']}</code>"
    return text


#? EN: Retrieves chat rules from database
#* RU: Получает правила чата из базы данных
async def pravila_sdk(message):
    # Initialize database for this chat if it doesn't exist
   
    connection = sqlite3.connect(get_db_path(message.chat.id), check_same_thread=False)
    cursor = connection.cursor()
    try:
        rules = cursor.execute(f'SELECT text FROM texts WHERE text_name=?', ('rules',)).fetchall()[0][0]
        text = f"{desk_em} <b>Правила чата</b>\n\n{rules if rules and rules!=None and rules!='None' else 'Правила не установлены'}"
        return text
    except IndexError:
        return f"{desk_em} <b>Правила чата</b>\n\nПравила не установлены"
    finally:
        connection.close()

#? EN: Extracts user ID from message, defaults to sender if not found
#* RU: Извлекает ID пользователя из сообщения, по умолчанию возвращает отправителя
async def get_user_id_self(message):
    try:
        user_id = int(message.text.split('tg://openmessage?user_id=')[1].split()[0])
        return user_id
    except (IndexError, ValueError, TypeError) as e:
        print(e)
        pass
    
    try:
        user_id = int(message.text.split('@')[1].split()[0])
        return user_id
    except (ValueError, IndexError):
        pass

    try:
        username = (message.text.split('@')[1]).split()[0]
        chat_db_path = get_db_path(message.chat.id)
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        try:
            user_id = cursor.execute("SELECT tg_id FROM users WHERE username=?", (username,)).fetchall()[0][0]
            return user_id
        finally:
            connection.close()
    except (IndexError, sqlite3.Error):
        pass

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        return user_id
    else:
        user_id = message.from_user.id
        return user_id


#? EN: Removes specific warning from user and reorganizes warning list
#* RU: Снимает конкретное предупреждение с пользователя и реорганизует список предупреждений
async def snat_warn(user_id, number_warn, warn_count_new, message):
    chat_db_path = get_db_path(message.chat.id)
    connection = sqlite3.connect(chat_db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        # Получаем все предупреждения пользователя, отсортированные по дате
        cursor.execute("SELECT * FROM warns WHERE user_id = ? ORDER BY date", (user_id,))
        all_warns = cursor.fetchall()
        
        if not all_warns or number_warn > len(all_warns):
            return
            
        # Удаляем указанное предупреждение (1 = самое старое, 2 = второе, 3 = самое новое)
        warn_index = number_warn - 1
        if warn_index < len(all_warns):
            warn_to_delete = all_warns[warn_index]
            # Delete by user_id and reason to identify the specific warning
            cursor.execute("DELETE FROM warns WHERE user_id = ? AND reason = ? AND moder_id = ? AND date = ?", 
                        (user_id, warn_to_delete[1], warn_to_delete[2], warn_to_delete[3]))
            connection.commit()
            
        # Записываем в историю снятых предупреждений
        moder_name = message.from_user.full_name
        moder_mention = f'<a href="tg://user?id={message.from_user.id}">{moder_name}</a>'
        
        try:
            cursor.execute('INSERT INTO warn_snat (user_id, warn_text, moder_give, moder_snat) VALUES (?, ?, ?, ?)', 
                        (user_id, warn_to_delete[1] if warn_index < len(all_warns) else 'Предупреждение', f'ID: {warn_to_delete[2]}' if warn_index < len(all_warns) else 'Неизвестен', moder_mention))
            connection.commit()
        except:
            pass
            
    except Exception as e:
        print(f"Error in snat_warn: {e}")
    finally:
        connection.close()

#? EN: Checks if moderator has sufficient rank to execute command
#* RU: Проверяет, имеет ли модератор достаточный ранг для выполнения команды
async def is_successful_moder(moder_id, chat_id, command):
    global klan
    chat_db_path = get_db_path(chat_id)
    connection = sqlite3.connect(chat_db_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        rang_moder = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        return 'Need reg'
    except sqlite3.OperationalError:
        return 'chat error'
    
    command_dk = int(cursor.execute("SELECT dk FROM dk WHERE comand=?", (command,)).fetchall()[0][0])
    if rang_moder < command_dk:
        return False
    else:
        return True

#? EN: Checks if moderator has higher rank than target user
#* RU: Проверяет, имеет ли модератор более высокий ранг чем целевой пользователь
async def is_more_moder(user_id, moder_id, chat_id):
    chat_db_path = get_db_path(chat_id)
    connection = sqlite3.connect(chat_db_path, check_same_thread=False)
    cursor = connection.cursor()
    rang_moder = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    try:
        first_rang_user = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?",(user_id,)).fetchall()[0][0]
    except IndexError:
        if user_id == 8451829699:
            return False
        else:
            first_rang_user = 0

    if first_rang_user >= rang_moder:
        return False
    else:
        return True

#? EN: Gives warning to user with specified reason
#* RU: Выдает предупреждение пользователю с указанной причиной
async def give_warn(message, comments, user_id, is_first):
    chat_db_path = get_db_path(message.chat.id)
    connection = sqlite3.connect(chat_db_path, check_same_thread=False)
    cursor = connection.cursor()
    
    moder_name = message.from_user.full_name
    moder_mention = f'<a href="tg://user?id={message.from_user.id}">{moder_name}</a>'
    date = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    
    # В новой структуре просто добавляем запись в таблицу warns
    cursor.execute('INSERT INTO warns (user_id, reason, moder_id, date) VALUES (?, ?, ?, ?)', 
                (user_id, comments, message.from_user.id, date))
    
    connection.commit()

#? EN: Inserts banned user information into database
#* RU: Вставляет информацию о забаненном пользователе в базу данных
async def insert_ban_user(user_id, user_men, moder_men, comments, message_id, chat_id, connection=None):
    if connection is None:
        # Create new connection only if not provided
        chat_db_path = get_db_path(chat_id)
        connection = sqlite3.connect(chat_db_path, check_same_thread=False)
        cursor = connection.cursor()
        close_connection = True
    else:
        # Use provided connection (from ban_user transaction)
        cursor = connection.cursor()
        close_connection = False
    
    # Check if bans table exists, create it if not
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='bans' ''')
    if not cursor.fetchone():
        # Create bans table
        cursor.execute('''CREATE TABLE bans (
            tg_id INTEGER UNIQUE NOT NULL,
            id_pubg INTEGER NOT NULL UNIQUE,
            message_id INTEGER,
            prichina TEXT,
            date TEXT,
            user_men TEXT,
            moder_men TEXT
        )''')
        connection.commit()
    
    try:
        id_pubg = cursor.execute(f"SELECT id_pubg FROM users WHERE tg_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        id_pubg = 'неизвестен'
    date = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    try:
        cursor.execute('INSERT INTO bans (tg_id, id_pubg, message_id, prichina, date, user_men, moder_men) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                    (user_id, id_pubg, message_id, comments, date, user_men, moder_men))
    except sqlite3.IntegrityError:
        cursor.execute('UPDATE bans SET id_pubg = ?, message_id = ?, prichina = ?, date = ?, user_men = ?, moder_men = ? WHERE tg_id = ?', 
                    (id_pubg, message_id, comments, date, user_men, moder_men, user_id))
    connection.commit()
    try:
        cursor.execute(f'DELETE FROM users WHERE tg_id = ?', (user_id, ))
        connection.commit()
    except sqlite3.OperationalError:
        pass
    
    if close_connection:
        connection.close()

#? EN: Mutes user for specified time period with given reason
#* RU: Мутит пользователя на указанный период времени с указанной причиной
async def mute_user(user_id, chat_id, muteint, mutetype, message, comments, bot: Bot):
    connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
    cursor = connection.cursor()
    
    # Check if muts table exists, create it if not
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='muts' ''')
    if not cursor.fetchone():
        # Create muts table
        cursor.execute('''CREATE TABLE muts (
            user_id INTEGER,
            rang_moder INTEGER,
            moder_id INTEGER,
            moder_men TEXT,
            date TEXT,
            comments TEXT
        )''')
        connection.commit()
    
    print(mutetype, muteint)
    try:
        if mutetype == "ч" or mutetype == "часов" or mutetype == "час" or mutetype == "часа":
            dt = datetime.now() + timedelta(hours=int(muteint))
            timestamp = dt.timestamp()
        elif mutetype == "мин" or mutetype == "минут" or mutetype == "минуты" or mutetype == "минута":
            dt = datetime.now() + timedelta(minutes=int(muteint))
            timestamp = dt.timestamp()
        elif mutetype == "д" or mutetype == "дней" or mutetype == "день" or mutetype == "дня" or mutetype == "сутки":
            dt = datetime.now() + timedelta(days=int(muteint))
            timestamp = dt.timestamp()
        elif mutetype == comments.split()[0]:
            dt = datetime.now() + timedelta(hours=int(muteint))
            timestamp = dt.timestamp()
        else:
            connection.close()
            return False
    except IndexError:
        connection.close()
        return False
    date = dt.strftime('%H:%M:%S %d.%m.%Y')
    try:
        await bot.restrict_chat_member(chat_id, user_id,permissions=ChatPermissions(can_send_messages=False),until_date=timestamp)
        moder_id = message.from_user.id
        moder_name = message.from_user.full_name
        moder_men = f'<a href="tg://user?id={moder_id}">{moder_name}</a>'
        rang_moder = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
        try:

            rang_f_moder = cursor.execute(f'SELECT rang_moder FROM muts WHERE user_id=?', (user_id,)).fetchall()[0][0]
            if rang_f_moder > rang_moder:
                connection.close()
                rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель',
                              'Менеджер',
                              'Владелец')
                text = f'📝 Ранг модератора не достаточен для перевыдачи мута. Обратитесь к модератору рангом от {rang_f_moder}+ ({rangs_name[rang_f_moder]})'
                return text
            cursor.execute(f'UPDATE muts SET rang_moder = ?, moder_id = ?, moder_men = ?, date = ?, comments = ? WHERE user_id = ?',
                           (rang_moder, moder_id, moder_men, date, comments, user_id))
        except IndexError:
            cursor.execute(
                f'INSERT INTO muts (user_id, rang_moder, moder_id, moder_men, date, comments) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, rang_moder, moder_id, moder_men, date, comments))

        connection.commit()
        connection.close()
        return True
    except TelegramBadRequest:
        await message.reply(
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Телеграм-админом этого чата',
            parse_mode='html')
        connection.close()
        return False
    except Exception as e:
        print(f"Error in mute_user: {e}")
        connection.close()
        return False

#? EN: Unmutes user and removes mute record from database
#* RU: Размучивает пользователя и удаляет запись о муте из базы данных
async def unmute_user(user_id, chat_id, message, bot: Bot):
    connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
    cursor = connection.cursor()
    try:
        rang_f_moder = cursor.execute(f'SELECT rang_moder FROM muts WHERE user_id = ?', (user_id,)).fetchall()[0][0]
    except IndexError:
        connection.close()
        text = '🗓 Пользователь не лишён свободы слова'
        return text
    moder_id = message.from_user.id
    rang_moder = cursor.execute(f"SELECT rang FROM users WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    if rang_f_moder > rang_moder:
        connection.close()
        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель',
                      'Менеджер',
                      'Владелец')
        text = f'📝 Ранг модератора не достаточен для размута. Обратитесь к модератору рангом от {rang_f_moder}+ ({rangs_name[rang_f_moder]})'
        return text
    await bot.restrict_chat_member(chat_id, user_id,permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                                               can_send_photos=True, can_send_videos=True,
                                                               can_send_audios=True, can_send_documents=True,
                                                               can_send_other_messages=True,
                                                               can_send_video_notes=True, can_send_voice_notes=True,
                                                               can_pin_messages=True,
                                                               can_add_web_page_previews=True, can_send_polls=True))
    cursor.execute(f'DELETE FROM muts WHERE user_id = ?', (user_id, ))
    connection.commit()
    connection.close()
    return True

#? EN: Bans user from chat and records ban information in database
#* RU: Банит пользователя из чата и записывает информацию о бане в базу данных
async def ban_user(user_id, chat_id, user_men, moder_men, comments, message_id, message, bot: Bot):
    connection = None
    try:
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False, timeout=10.0)
        cursor = connection.cursor()
        
        # Start transaction
        cursor.execute("BEGIN IMMEDIATE")
        
        await bot.ban_chat_member(chat_id, user_id)
        
        cursor.execute('DELETE FROM warns WHERE user_id = ?', (user_id,))
        
        await insert_ban_user(user_id, user_men, moder_men, comments, message_id, chat_id, connection)
        
        # Commit transaction
        connection.commit()
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print(f"Database locked in ban_user: {e}")
            return 'База данных занята, попробуйте еще раз через несколько секунд'
        else:
            print(f"OperationalError in ban_user: {e}")
            return f'Ошибка базы данных при бане пользователя: {str(e)}'
    except TelegramBadRequest as e:
        print(f"TelegramBadRequest in ban_user: {e}")
        return f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Телеграм-админом этого чата'
    except Exception as e:
        print(f"Unexpected error in ban_user: {e}")
        return f'Произошла ошибка при бане пользователя: {str(e)}'
    finally:
        if connection:
            connection.close()

#? EN: Unbans user from chat and removes ban record from database
#* RU: Разбанивает пользователя в чате и удаляет запись о бане из базы данных
async def unban_user(chat_id, user_id, bot: Bot):
    connection = None
    try:
        connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False, timeout=10.0)
        cursor = connection.cursor()
        
        # Start transaction
        cursor.execute("BEGIN IMMEDIATE")
        
        cursor.execute("SELECT * FROM bans WHERE tg_id = ?", (user_id,))
        ban_record = cursor.fetchall()
        
        if not ban_record:
            return '🗓 Пользователь не забанен'
            
        await bot.unban_chat_member(chat_id, user_id)
        
        cursor.execute('DELETE FROM bans WHERE tg_id = ?', (user_id,))
        
        # Commit transaction
        connection.commit()
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print(f"Database locked in unban_user: {e}")
            return 'База данных занята, попробуйте еще раз через несколько секунд'
        else:
            print(f"OperationalError in unban_user: {e}")
            return f'Ошибка базы данных при разбане: {str(e)}'
    except TelegramBadRequest as e:
        print(f"TelegramBadRequest in unban_user: {e}")
        return f'Ошибка при разбане: {str(e)}'
    except Exception as e:
        print(f"Unexpected error in unban_user: {e}")
        return f'Произошла ошибка при разбане: {str(e)}'
    finally:
        if connection:
            connection.close()

#? EN: Returns banned user back to chat
#* RU: Возвращает забаненного пользователя обратно в чат
async def return_user(chat_id, user_id, bot: Bot):
    connection = sqlite3.connect(get_db_path(chat_id), check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute(f'SELECT * FROM bans WHERE tg_id = ?', (user_id,))
        ban_record = cursor.fetchall()
        
        if not ban_record:
            return '🗓 Пользователь не в списке забаненных'
        
        ban_data = ban_record[0]
        id_pubg = ban_data[1]
        user_men = ban_data[5]
        
        await bot.unban_chat_member(chat_id, user_id)
        
        cursor.execute(f'DELETE FROM bans WHERE tg_id = ?', (user_id,))
        connection.commit()
        
        return {'success': True, 'id_pubg': id_pubg, 'user_men': user_men}
        
    except TelegramBadRequest as e:
        print(f"TelegramBadRequest in return_user: {e}")
        return f'Ошибка при возврате: {str(e)}'
    except Exception as e:
        print(f"Error in return_user: {e}")
        return f'Произошла ошибка при возврате пользователя: {str(e)}'
    finally:
        connection.close()

#? EN: Kicks user from chat without permanent ban
#* RU: Кикает пользователя из чата без постоянного бана
async def kick_user(user_id, chat_id, bot: Bot):
    try:
        await bot.ban_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)
        return True
    except TelegramBadRequest:
        await bot.send_message(chat_id,
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Телеграм-админом этого чата',
            parse_mode='html')

