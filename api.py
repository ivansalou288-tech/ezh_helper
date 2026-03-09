# from math import log
# import sqlite3
# import os
# import ssl
# import sys
# from fastapi import FastAPI, HTTPException, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# import uvicorn
# from pydantic import BaseModel
# import asyncio
# from datetime import datetime
# import password_generator
# from typing import Any, Optional
# import time
# import json
# # Добавляем корневую директорию проекта в путь
# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# sys.path.insert(0, ROOT_DIR)

# from main.config3 import *
# import main.secret
# TOKEN = main.secret.main_token

# bot = Bot(token=TOKEN)
# admin_bot = Bot(token=main.secret.admin_token)
# prinatie_bot = Bot(token=main.secret.prinatie_token)
# class RecomRemoveAction(BaseModel):
#     rec_id: str
#     user_id: Optional[int] = None
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None

# class UserAction(BaseModel):
#     chat: str
#     userid: str
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None

# class SnatWarnAction(BaseModel):
#     chat: str
#     userid: str
#     num: int
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None

# class BanAction(BaseModel):
#     chat: str
#     userid: str
#     reason: str
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None

# class RecomAddAction(BaseModel):
#     user_id: int
#     reason: str
#     position: str
#     username: Optional[str] = None
#     pubg_nik: Optional[str] = None
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None

# class CreateLinkAction(BaseModel):
#     sost: int
#     activate_count: int
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None

# class DeleteLinkAction(BaseModel):
#     link: str
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None

# class SendLinkToBotAction(BaseModel):
#     link: str
#     admin_id: Optional[int] = None
#     admin_name: Optional[str] = None
#     admin_username: Optional[str] = None
#     sost: int
#     activate_count: int

# class FormData(BaseModel):
#     telegram_id: Optional[int] = None
#     user: Optional[str] = None
#     name: str
#     age: int
#     nick: str
#     gameId: str
#     invite_code: Optional[str] = None
#     sost: Optional[int] = None

# chats_names = {'klan': 1002143434937, 'sost-1': 1002274082016, 'sost-2': 1002439682589}

# #? EN: User IDs allowed to access admin panel
# #* RU: ID пользователей, которым разрешен доступ к админ-панели
# can_admin_panel = [8015726709, 1401086794, 1240656726]


# async def gaid(chat_id):
#     from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton
#     from aiogram.types.input_file import FSInputFile
    
#     id_copy = CopyTextButton(text=str(51445023900))
#     id_btn = InlineKeyboardButton(text="📋Скопировать айди Лидера", copy_text=id_copy)
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[id_btn]])
    
#     await prinatie_bot.send_message(
#         chat_id,
#         text='Как вступить в клан?\n\n<b>1.</b> Ищешь игрока wePiKAcHy по айди «<code>51445023900</code>» и нажимаешь на его аватарку',
#         parse_mode='html', 
#         reply_markup=keyboard
#     )
    
#     # Отправка группы фото
#     from aiogram.types import InputMediaPhoto, InputMediaDocument, InputMediaVideo, InputMediaAudio
#     await prinatie_bot.send_media_group(
#         chat_id, 
#         media=[
#             InputMediaPhoto(media=FSInputFile(f'{curent_path}/photos/first_step.jpg')),
#             InputMediaPhoto(media=FSInputFile(f'{curent_path}/photos/second_step.jpg'))
#         ]
#     )
    
#     await prinatie_bot.send_message(
#         chat_id,
#         text='<b>2.</b> В его профиле нажимаешь на аватарку клана «Werty» и в всплышем окне нажимаешь на запрос',
#         parse_mode='html'
#     )
    
#     await prinatie_bot.send_media_group(
#         chat_id,
#         media=[
#             InputMediaPhoto(media=FSInputFile(f'{curent_path}/photos/therd_step.jpg')),
#             InputMediaPhoto(media=FSInputFile(f'{curent_path}/photos/last_step.jpg'))
#         ]
#     )



# def check_admin_rights(admin_id: Optional[int]) -> bool:
#     """Проверяет права доступа администратора"""
#     if admin_id is None:
#         return False
#     return admin_id in can_admin_panel


# def build_admin_link(admin_id: Optional[int], admin_username: Optional[str] = None) -> Optional[str]:
#     if admin_username:
#         u = admin_username.lstrip('@')
#         if u:
#             return f"https://t.me/{u}"
#     if admin_id is not None:
#         return f"tg://user?id={admin_id}"
#     return None


# def ensure_not_self_action(admin_id: Optional[int], target_user_id: Optional[int], action_name: str) -> None:
#     if admin_id is None or target_user_id is None:
#         return
#     if int(admin_id) == int(target_user_id):
#         raise HTTPException(status_code=400, detail=f"Cannot {action_name} yourself")

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain('/etc/letsencrypt/live/ezh-dev.ru/cert.pem', keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem')

# command_name = {
#             'ban': 'Блокировка пользователей',
#             'mut': 'Ограничение пользователей',
#             'warn': 'Предупреждение пользователей',
#             'all': 'Созыв пользователей',
#             'rang': 'Изменение ранга пользователей',
#             'dk': 'Изменение доступа вызова команд',
#             'change_pravils': 'Изменение правил чата',
#             'close_chat': 'Изменение ограничений чата',
#             'change_priv': 'Изменение приветствия чата',
#             'obavlenie': 'Создание объявления',
#             'tur': 'Создание турниров',
#             'dell': 'Удаление сообщений',
#             'period': 'Изменение периодов'
#         }

# app = FastAPI()

# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # # Обслуживание статических файлов
# # app.mount("/static", StaticFiles(directory="new_chat_mem_dir"), name="static")

# # @app.get("/", response_class=HTMLResponse)
# # async def read_root():
# #     # Отдаем HTML файл
# #     try:
# #         with open("new_chat_mem_dir/index.html", "r", encoding="utf-8") as f:
# #             content = f.read()
# #         return HTMLResponse(content=content)
# #     except FileNotFoundError:
# #         return HTMLResponse("<h1>Файл не найден</h1>", status_code=404)

# class CodeCheckRequest(BaseModel):
#     code: str

# @app.post("/check_invite_code")
# async def check_invite_code(request: Request):
#     """
#     Проверяет код приглашения в базе данных
#     """
#     try:
#         # Получаем тело запроса
#         body = await request.body()
#         raw_data = body.decode('utf-8')
#         print(f"Проверка кода: {raw_data}")
        
#         # Парсим JSON
#         import json
#         data = json.loads(raw_data)
#         code = data.get('code', '').strip()
        
#         if not code:
#             return {
#                 "status": "error",
#                 "message": "Код не указан"
#             }
        
#         # Проверяем код в базе данных
#         connection = sqlite3.connect(datahelp_path, check_same_thread=False)
#         cursor = connection.cursor()
        
#         cursor.execute('SELECT link_text, activate_count, sost FROM links_for_sosts WHERE link_text = ?', (code,))
#         result = cursor.fetchone()
#         connection.close()
        
#         if result:
#             link_text, activate_count, sost = result
#             if activate_count > 0:
#                 # activate_count_new = activate_count - 1
#                 # if activate_count_new == 0:
#                 #     cursor.execute('DELETE FROM links_for_sosts WHERE link_text = ?', (message.text,))
#                 #     connection.commit()
#                 #     connection.close()
#                 # else:
#                 #     cursor.execute('UPDATE links_for_sosts SET activate_count = ? WHERE link_text = ?', (activate_count_new, message.text))
#                 #     connection.commit()
#                 #     connection.close()
#                 return {
#                     "status": "success",
#                     "message": "Код действителен",
#                     "data": {
#                         "link": link_text,
#                         "activate_count": activate_count,
#                         "sost": sost
#                     }
#                 }
#             else:
#                 return {
#                     "status": "error",
#                     "message": "Код исчерпал лимит активаций"
#                 }
#         else:
#             return {
#                 "status": "error",
#                 "message": "Код не найден"
#             }
            
#     except Exception as e:
#         print(f"Ошибка при проверке кода: {e}")
#         return {
#             "status": "error",
#             "message": f"Ошибка проверки: {str(e)}"
#         }

# @app.get("/get_rules")
# async def get_rules():
#     try:
#         connection = sqlite3.connect(main_path, check_same_thread=False)
#         cursor = connection.cursor()
#         # Получаем правила из базы данных
#         cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('pravils',))
#         result = cursor.fetchall()
        
#         if result:
#             rules_text = result[0][0]
#             return {
#                 "status": "success",
#                 "data": {
#                     "rules": rules_text
#                 }
#             }
#         else:
#             return {
#                 "status": "error",
#                 "message": "Правила не найдены"
#             }
#     except Exception as e:
#         print(f"Ошибка при получении правил: {e}")
#         return {
#             "status": "error",
#             "message": "Ошибка сервера"
#         }

# @app.post("/upload_photo")
# async def upload_photo(request: Request):
#     """
#     Принимает фото скриншота отправленного запроса в клан
#     """
#     try:
#         # Получаем форму с файлом
#         form = await request.form()
#         photo = form.get("photo")
#         telegram_id = form.get("telegram_id")
#         username = form.get("username")
        
#         print(f"Получены данные: photo={photo}, telegram_id={telegram_id}, username={username}")
        
#         if not photo:
#             return {
#                 "status": "error",
#                 "message": "Фото не найдено"
#             }
        
#         # Сохраняем фото
#         # photo_filename = f"screen_{telegram_id}_{int(time.time())}.jpg"
        
#         # # Используем абсолютный путь
#         # import os
#         # screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
#         # os.makedirs(screenshots_dir, exist_ok=True)
#         # photo_path = os.path.join(screenshots_dir, photo_filename)
        
#         # print(f"Путь для сохранения: {photo_path}")
        
#         # # Сохраняем файл
#         # with open(photo_path, "wb") as buffer:
#         #     content = await photo.read()
#         #     buffer.write(content)
        
#         # print(f"Получен скриншот от пользователя {telegram_id} (@{username}): {photo_filename}")
#         # print(f"Размер файла: {os.path.getsize(photo_path)} байт")
        
#         # Здесь можно добавить логику для отправки фото в Telegram или сохранения в БД
#         await asyncio.sleep(3)
#         return {
#             "status": "success",
#             "message": "Скриншот успешно загружен",
#             "data": {
#                 "filename": 'name',
#                 "telegram_id": telegram_id,
#                 "username": username
#             }
#         }
        
#     except Exception as e:
#         print(f"Ошибка при загрузке фото: {e}")
#         import traceback
#         traceback.print_exc()
#         return {
#             "status": "error",
#             "message": f"Ошибка загрузки: {str(e)}"
#         }

# @app.post("/generate_invite_links")
# async def generate_invite_links(request: Request):
#     """
#     Генерирует ссылки-приглашения в чаты для пользователя
#     """
#     try:
#         # Получаем тело запроса
#         body = await request.body()
#         raw_data = body.decode('utf-8')
#         data = json.loads(raw_data)
        
#         telegram_id = data.get('telegram_id')
#         username = data.get('username')
        
#         if not telegram_id:
#             return {
#                 "status": "error",
#                 "message": "Telegram ID не указан"
#             }
        
#         # Проверяем есть ли пользователь в таблице is_to_klan
#         connection = sqlite3.connect(dinamik_path, check_same_thread=False)
#         cursor = connection.cursor()
        
#         cursor.execute('SELECT sostav FROM is_to_klan WHERE user_id = ?', (telegram_id,))
#         result = cursor.fetchone()
#         connection.close()
        
#         if not result:
#             return {
#                 "status": "error", 
#                 "message": "Сначала подайте заявку в клан"
#             }
        
#         sostav = result[0]
        
#         # Генерируем ссылки в зависимости от состава
#         if sostav == 1:
#             clan_link = await prinatie_bot.export_chat_invite_link(klan)
#             sost_link = await prinatie_bot.export_chat_invite_link(sost_1)
#             chat_name = "Состав 1"
#             return {
#             "status": "success",
#             "data": {
#                 "clan": {
#                     "name": "Клан Werty",
#                     "avatar": "/photos/klan_ava.jpg",
#                     "link": clan_link
#                 },
#                 "sostav": {
#                     "name": chat_name,
#                     "avatar": "/photos/sost-1.jpg",
#                     "link": sost_link
#                 }
#             }
#         }
#         elif sostav == 2:
#             clan_link = await prinatie_bot.export_chat_invite_link(klan)
#             sost_link = await prinatie_bot.export_chat_invite_link(sost_2)
#             chat_name = "Состав 2"
#             return {
#             "status": "success",
#             "data": {
#                 "clan": {
#                     "name": "Клан Werty",
#                     "avatar": "/photos/klan_ava.jpg",
#                     "link": clan_link
#                 },
#                 "sostav": {
#                     "name": chat_name,
#                     "avatar": "/photos/sost-2.jpg",
#                     "link": sost_link
#                 }
#             }
#         }
        
#         else:
#             return {
#                 "status": "error",
#                 "message": "Неизвестный состав"
#             }
        
        
#     except Exception as e:
#         print(f"Ошибка при генерации ссылок: {e}")
#         import traceback
#         traceback.print_exc()
#         return {
#             "status": "error",
#             "message": f"Ошибка генерации: {str(e)}"
#         }

# @app.post("/submit_form")
# async def submit_form(request: Request):
#     """
#     Принимает заявку в клан и выводит её в консоль
#     """
#     try:
#         # Получаем тело запроса
#         body = await request.body()
#         raw_data = body.decode('utf-8')
#         print(f"Полученные сырые данные: {raw_data}")
        
#         # Парсим JSON
#         import json
#         data = json.loads(raw_data)
#         print(f"Распарсенные данные: {data}")
        
#         # Создаем объект FormData вручную
#         form_data = FormData(**data)
        
#         print("=" * 50)
#         print("НОВАЯ ЗАЯВКА В КЛАН:")
#         print(f"Telegram ID: {form_data.telegram_id}")
#         print(f"Username: @{form_data.user}" if form_data.user else "Username: отсутствует")
#         print(f"Имя: {form_data.name}")
#         print(f"Возраст: {form_data.age}")
#         print(f"Игровой ник: {form_data.nick}")
#         print(f"Игровой ID: {form_data.gameId}")
#         print(f"Код приглашения: {form_data.invite_code}")
#         print(f"Состав: {form_data.sost}")
#         print(f"Время подачи: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}")
#         print("=" * 50)
        
#         # Уменьшаем количество активаций кода
#         if form_data.invite_code:
#             try:
#                 connection = sqlite3.connect(datahelp_path, check_same_thread=False)
#                 cursor = connection.cursor()
#                 cursor.execute(
#                     'UPDATE links_for_sosts SET activate_count = activate_count - 1 WHERE link_text = ?',
#                     (form_data.invite_code,)
#                 )
#                 connection.commit()
                
#                 # Проверяем новое количество активаций
#                 cursor.execute('SELECT activate_count FROM links_for_sosts WHERE link_text = ?', (form_data.invite_code,))
#                 new_count = cursor.fetchone()
#                 print(f"Осталось активаций для кода {form_data.invite_code}: {new_count[0] if new_count else 0}")
#                 connection.close()
                
#             except Exception as e:
#                 print(f"Ошибка при обновлении активаций: {e}")
        
#         # Отправка уведомления в Telegram (если нужно)
#         try:
#             connection = sqlite3.connect(main_path, check_same_thread=False)
#             cursor = connection.cursor()

#             if form_data.telegram_id:
#                 # Добавляем в основной клан
#                 cursor.execute(
#                     f'INSERT INTO [{-klan}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
#                     (form_data.telegram_id, form_data.user, form_data.name, form_data.age, form_data.nick, form_data.gameId, form_data.nick, 0, '', datetime.now().strftime('%H:%M:%S %d.%m.%Y'))
#                 )
#                 connection.commit()
            
#                 # Добавляем в общую таблицу пользователей
#                 try:
#                     cursor.execute('INSERT INTO all_users (user_id, username) VALUES (?, ?)', (form_data.telegram_id, form_data.user))
#                     connection.commit()
#                 except sqlite3.IntegrityError:
#                     connection.commit()
#                     cursor.execute('UPDATE all_users SET username = ? WHERE user_id = ?', (form_data.user, form_data.telegram_id))
#                     connection.commit()

#                 # Добавляем в состав в зависимости от sost
#                 if form_data.sost == 1:
#                     try:
#                         cursor.execute(
#                             f'INSERT INTO [{-sost_1}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
#                             (form_data.telegram_id, form_data.user, form_data.name, form_data.age, form_data.nick, form_data.gameId, form_data.nick, 0, '', datetime.now().strftime('%H:%M:%S %d.%m.%Y'))
#                         )
#                     except Exception:
#                         pass
#                     connection.commit()

#                 elif form_data.sost == 2:
#                     try:
#                         cursor.execute(
#                             f'INSERT INTO [{-sost_2}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
#                             (form_data.telegram_id, form_data.user, form_data.name, form_data.age, form_data.nick, form_data.gameId, form_data.nick, 0, '', datetime.now().strftime('%H:%M:%S %d.%m.%Y'))
#                         )
#                     except Exception:
#                         pass
#                     connection.commit()

#                 # Отправляем логи
#                 await prinatie_bot.send_message(
#                     logs_gr,  # logs_gr заменил на конкретный ID
#                     f'<a href="https://t.me/{form_data.user}">Пользователь</a> вошел в клан и {form_data.sost} состав\n\nЕго описание: \nИмя: {form_data.name}\nВозраст: {form_data.age}\nАйди: {form_data.gameId}\nНик: {form_data.nick}',
#                     parse_mode='html'
#                 )

#                 # Добавляем в черный список
#                 try:
#                     cursor.execute('INSERT INTO black_list (user_id, rison) VALUES (?, ?)', (form_data.telegram_id, ''))
#                 except Exception:
#                     pass

#                 # Отправляем инструкции
#                 import asyncio
#                 await asyncio.sleep(0.5)
                
#                 # Получаем правила из базы
#                 try:
#                     cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('pravils',))
#                     pravils_text = cursor.fetchone()
#                     if pravils_text:
#                         await prinatie_bot.send_message(
#                             form_data.telegram_id,
#                             f"!!Ознакомься!!\n\n{pravils_text[0]}"
#                         )
#                 except Exception:
#                     pass
                
#                 await gaid(form_data.telegram_id)
#                 await asyncio.sleep(0.5)
                
#                 # Отправляем фото с инструкцией


#                 # Основное уведомление
#                 await prinatie_bot.send_message(
#                     form_data.telegram_id,
#                     f"✅ Твое описание! \n\n📋 Данные:\n• Имя: {form_data.name}\n• Возраст: {form_data.age}\n• Игровой ник: {form_data.nick}\n• Игровой ID: {form_data.gameId}"
#                 )

#         except Exception as e:
#             print(f"Ошибка отправки уведомления: {e}")
#             return {
#                 "status": "error", 
#                 "message": f"Скорее всего ты уже в клане"
#             }





        
#         # Возвращаем успешный ответ
#         return {
#             "status": "success",
#             "message": "Заявка в клан успешно принята",
#             "data": {
#                 "telegram_id": form_data.telegram_id,
#                 "user": form_data.user,
#                 "name": form_data.name,
#                 "age": form_data.age,
#                 "nick": form_data.nick,
#                 "gameId": form_data.gameId,
#                 "submitted_at": datetime.now().isoformat()
#             }
#         }
        
#     except json.JSONDecodeError as e:
#         print(f"Ошибка парсинга JSON: {e}")
#         return {
#             "status": "error",
#             "message": f"Ошибка парсинга JSON: {str(e)}"
#         }
#     except Exception as e:
#         print(f"Общая ошибка: {e}")
#         return {
#             "status": "error", 
#             "message": f"Ошибка обработки: {str(e)}"
#         }


# async def get_users_sdk(chat: str):
       
#     connection = sqlite3.connect(main_path)
#     cursor = connection.cursor()
#     userss = cursor.execute(f'SELECT * FROM [{chats_names[chat]}]').fetchall()
#     users = {}
#     index = 1
#     for user in userss:
#             tg_ids = user[0]
#             usernames = user[1]
#             names = user[2]
#             age = user[3]
#             nik_pubg = user[4]
#             id_pubg = user[5]
#             nik = user[6]
#             rang = user[7]
#             last_date = user[8]
#             date_vhod = user[9]
#             mess_count = user[10]

#             # Пытаемся получить статус участника в чате; если его больше нет в чате,
#             # Telegram может вернуть ошибку "member not found" — тогда считаем, что
#             # пользователь не состоит в чате.
#             try:
#                 chat_member = await bot.get_chat_member(-(chats_names[chat]), tg_ids)
#                 status = chat_member.status
#             except Exception:
#                 status = 'left'

#             if status == 'administrator':
#                 chat_status = '👨🏻‍🔧 Телеграм-админ этого чата'
#             elif status == 'creator':
#                 chat_status = '👨🏻‍🔧 Создатель этого чата'
#             elif status == 'member' or status == 'restricted':
#                 chat_status = '💚 Состоит в чате'
#             else:
#                 chat_status = '💔 Не состоит в чате'

#             users[index] = {
#                 'tg_ids': tg_ids,
#                 'username': usernames,
#                 'name': names,
#                 'age': age,
#                 'nik_pubg': nik_pubg,
#                 'id_pubg': id_pubg,
#                 'nik': nik,
#                 'rang': rang,
#                 'last_date': last_date,
#                 'date_vhod': date_vhod,
#                 'mess_count': mess_count,
#                 'status': chat_status,
#             }
#             index += 1
#     return users

# def get_dk_sdk(chat: str):

#     connection = sqlite3.connect(main_path)
#     cursor = connection.cursor()

#     cursor.execute(f'SELECT * FROM [{chat}]')
#     dks = cursor.fetchall()
#     dkss = {}
#     index = 1
#     for dk in dks:
#          command = dk[0]
#          access = dk[1]
#          index+=1
#          dkss[index] = {'command': command_name[command], 'access': access}
         
#     return dkss


# async def snat_admn_warn(user_id, number_warn, warn_count_new, chat_id):
#     connection = sqlite3.connect(warn_path, check_same_thread=False)
#     cursor = connection.cursor()
#     num_list = ['nul', 'first', 'second', 'therd']
#     number_warn_dell = f'{num_list[number_warn]}_warn'
#     number_moder = f'{num_list[number_warn]}_moder'
#     try:
#         text = cursor.execute(f'SELECT {number_warn_dell} FROM [{(chat_id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
#     except IndexError:
#         return
#     moder = cursor.execute(f'SELECT {number_moder} FROM [{(chat_id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
#     cursor.execute(f'UPDATE [{(chat_id)}] SET warns_count = ? WHERE tg_id = ?',
#                    (warn_count_new, user_id))
#     connection.commit()
#     cursor.execute(f'UPDATE [{(chat_id)}] SET {number_warn_dell} = ? WHERE tg_id = ?',
#                    (None, user_id))
#     connection.commit()
#     cursor.execute(f"SELECT * FROM [{(chat_id)}] WHERE tg_id=?", (user_id,))
#     connection.commit()
#     warns = cursor.fetchall()[0]

#     first_warn = warns[2]
#     second_warn = warns[3]
#     therd_warn = warns[4]
#     first_mod = warns[5]
#     second_mod = warns[6]
#     therd_mod = warns[7]

#     if number_warn == 1:
#         first_warn = second_warn
#         second_warn = therd_warn
#         therd_warn = None
#         first_mod = second_mod
#         second_mod = therd_mod
#         therd_mod = None
#     if number_warn == 2:
#         second_warn = therd_warn
#         therd_warn = None
#         second_mod = therd_mod
#         therd_mod = None
#     number_warn_dell = f'{num_list[number_warn]}_warn'
#     cursor.execute(f'UPDATE [{(chat_id)}] SET first_warn = ? WHERE tg_id = ?',
#                    (first_warn, user_id))
#     cursor.execute(f'UPDATE [{(chat_id)}] SET second_warn = ? WHERE tg_id = ?',
#                    (second_warn, user_id))
#     cursor.execute(f'UPDATE [{(chat_id)}] SET therd_warn = ? WHERE tg_id = ?',(therd_warn, user_id))
#     cursor.execute(f'UPDATE [{(chat_id)}] SET first_moder = ? WHERE tg_id = ?',
#                    (first_mod, user_id))
#     cursor.execute(f'UPDATE [{(chat_id)}] SET second_moder = ? WHERE tg_id = ?',
#                    (second_mod, user_id))
#     cursor.execute(f'UPDATE [{(chat_id)}] SET therd_moder = ? WHERE tg_id = ?',
#                    (therd_mod, user_id))
#     connection.commit()

#     cursor.execute(f'INSERT INTO [{(chat_id)}snat] (user_id, warn_text, moder_give, moder_snat) VALUES (?, ?, ?, ?)', (user_id, text, moder, 'Admin Panel'))
#     connection.commit()
#     cursor.execute(f'DELETE FROM [{(chat_id)}snat] WHERE moder_give IS NULL AND warn_text IS NULL')
#     connection.commit()

# async def insert_ban_user(user_id, user_men, moder_men, comments, message_id, chat_id):
#     connection = sqlite3.connect(main_path, check_same_thread=False)
#     cursor = connection.cursor()
#     try:
#         pubg_id = cursor.execute(f"SELECT id_pubg FROM [{-(chat_id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
#     except IndexError:
#         pubg_id = 'неизвестен'
#     date = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
#     try:
#         cursor.execute(f'INSERT INTO [{-(chat_id)}bans] (tg_id, id_pubg, message_id, prichina, date, user_men, moder_men) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, pubg_id, message_id, comments, date, user_men, moder_men))
#     except sqlite3.IntegrityError:
#         cursor.execute(f'UPDATE [{-(chat_id)}bans] SET id_pubg = ? WHERE tg_id = ?', (pubg_id, user_id))
#         cursor.execute(f'UPDATE [{-(chat_id)}bans] SET message_id = ? WHERE tg_id = ?', (message_id, user_id))
#         cursor.execute(f'UPDATE [{-(chat_id)}bans] SET prichina = ? WHERE tg_id = ?', (comments, user_id))
#         cursor.execute(f'UPDATE [{-(chat_id)}bans] SET date = ? WHERE tg_id = ?', (date, user_id))
#         cursor.execute(f'UPDATE [{-(chat_id)}bans] SET user_men = ? WHERE tg_id = ?', (user_men, user_id))
#         cursor.execute(f'UPDATE [{-(chat_id)}bans] SET moder_men = ? WHERE tg_id = ?', (moder_men, user_id))
#     connection.commit()
#     try:
#         cursor.execute(f'DELETE FROM [{-(chat_id)}] WHERE tg_id = ?', (user_id, ))
#         connection.commit()
#     except sqlite3.OperationalError:
#         pass

#     connection.commit()

# async def admin_ban(chat: str, user_id: int, reason: Optional[str], admin_id: Optional[int] = None, admin_name: Optional[str] = None) -> any:

#         user_men = GetUserByID(user_id).mention
#         admin_display = admin_name or "Некий админ"
#         await snat_admn_warn(user_id, 3, 2, chats_names[chat])
#         await snat_admn_warn(user_id, 2, 1, chats_names[chat])
#         await snat_admn_warn(user_id, 1, 0, chats_names[chat])
#         message_idd = (await bot.send_message(-(chats_names[chat]), f'<b>{voscl}Внимание{voscl}</b>\n{circle_em}Злостный нарушитель {user_men} получает бан и покидает нас\n👮‍♂️Выгнал его: {admin_display}\n{mes_em}Выгнали его за: {reason}', parse_mode='html')).message_id
#         await insert_ban_user(user_id, user_men, admin_display, reason, message_idd, -(chats_names[chat]))
#         await bot.ban_chat_member(-(chats_names[chat]), user_id)

# def dell_sdk(chat_id: int, user_id: int) -> Any:
        
#     connection = sqlite3.connect(main_path, check_same_thread=False)
#     cursor = connection.cursor()
#     try:
#         cursor.execute(f'DELETE FROM [{chat_id}] WHERE tg_id = ?', (user_id, ))
#         connection.commit()
#     except sqlite3.OperationalError:
#         pass

#     connection.commit()

# def full_dell_sdk(user_id: int) -> Any:
        
#     connection = sqlite3.connect(main_path, check_same_thread=False)
#     cursor = connection.cursor()
#     for chat_id in chats_names.values():
#         try:
#             cursor.execute(f'DELETE FROM [{chat_id}] WHERE tg_id = ?', (user_id, ))
#             connection.commit()
#         except sqlite3.OperationalError:
#             pass

#     connection.commit()


# async def admin_warn_dell(user_id: int, chat_id: int, number_warn: int, new_warns_count: int, admin_name: str | None = None): #Удаляет нужное предупреждение с сообщением в чат 
#     await snat_admn_warn(user_id, number_warn, new_warns_count, chat_id)
#     mention = GetUserByID(user_id).mention
#     admin_display = admin_name or "Некий админ"
#     await bot.send_message(chat_id=-(chat_id), text=f'{mention}, с тебя сняли одно предупреждение\n👮‍♂️Добрый модер: {admin_display}\n{mes_em} Количество твоих предупреждений: {new_warns_count} из 3\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»', parse_mode='html')

# @app.get("/users/{chat}")
# async def get_users(chat: str):
#     if chat in chats_names.keys():
#         users = await get_users_sdk(chat)
#         return users
#     else:
#         raise HTTPException(status_code=404, detail="Chat not found")
    
# @app.get("/dks/{chat}")
# def get_dks(chat: str):
#     if chat in ['klan', 'sostav']:
#         dkss = get_dk_sdk(chat)
#         return dkss
#     else:
#         raise HTTPException(status_code=404, detail="Chat not found")

# @app.get('/recom/{user}')
# def get_recom(user: int):
#     connection = sqlite3.connect(main_path, check_same_thread=False)
#     cursor = connection.cursor()
#     all = cursor.execute('SELECT * FROM recommendation WHERE user_id = ?', (user,)).fetchall()
#     recomendations = []
#     for rec in all:
#         print(rec)
#         id = rec[0]
#         pubg_id = rec[1]
#         moder_id = rec[2]
#         reason = rec[3]
#         rang = rec[4]
#         date = rec[5]
#         rec_id = rec[6]
#         recom = {"id": id,
#                  "pubg_id": pubg_id,
#                  "moder_id": moder_id,
#                  "reason": reason,
#                  "rang": rang,
#                  "date": date,
#                  "rec_id": rec_id,
#                  }
#         recomendations.append(recom)
#     return recomendations

# @app.get('/recom-clan/{chat}')
# def get_recom_clan(chat: str):
#     if chat not in chats_names:
#         raise HTTPException(status_code=404, detail="Chat not found")
#     chat_id = chats_names[chat]
#     connection = sqlite3.connect(main_path, check_same_thread=False)
#     cursor = connection.cursor()
#     cursor.execute('SELECT * FROM recommendation')
#     rows = cursor.fetchall()
#     recomendations = []
#     for row in rows:
#         user_id, pubg_id, moder, comments, rang, date, recom_id = row
#         recom = {

#             "user_id": user_id,
#             "pubg_id": pubg_id,
#             "moder": moder,
#             "reason": comments,
#             "rang": rang,
#             "date": date,
#             "rec_id": recom_id,

#         }
#         recomendations.append(recom)
#     return recomendations

# @app.post('/recom-remove')
# def recom_remove(action: RecomRemoveAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")

#     ensure_not_self_action(action.admin_id, action.user_id, 'remove recommendation')
    
#     print(f"Removing recommendation: rec_id={action.rec_id}, user_id={action.user_id} by admin {action.admin_id} ({action.admin_name})")
#     connection = sqlite3.connect(main_path, check_same_thread=False)
#     cursor = connection.cursor()
#     if action.user_id is None:
#         cursor.execute('DELETE FROM recommendation WHERE recom_id = ?', (action.rec_id,))
#     else:
#         cursor.execute('DELETE FROM recommendation WHERE recom_id = ? AND user_id = ?', (action.rec_id, action.user_id))
#     deleted = cursor.rowcount
#     connection.commit()
#     if deleted == 0:
#         raise HTTPException(status_code=404, detail="Recommendation not found")
#     return {"status": "ok", "deleted": deleted}

# @app.post('/recom-add')
# async def recom_add(action: RecomAddAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")

#     ensure_not_self_action(action.admin_id, action.user_id, 'recommend')
    
#     last_recom_user_id = action.user_id
#     last_recom_reason = action.reason
#     last_recom_position = action.position
#     last_recom_username = action.username
#     last_recom_pubg_nik = action.pubg_nik
#     admin_display = action.admin_name or "Некий админ"
#     date = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
#     id_recom = password_generator.generate(count=1, length=8, chars='ASDFGHJKL12345678')
#     print(f'recom_add {action.user_id} by admin {action.admin_id} ({action.admin_name})')
#     print(last_recom_user_id, last_recom_reason, last_recom_position, last_recom_username, last_recom_pubg_nik)
#     connection = sqlite3.connect(main_path, check_same_thread=False)
#     cursor = connection.cursor()
#     cursor.execute(
#         'INSERT INTO recommendation (user_id, pubg_id, moder, comments, rang, date, recom_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
#         (last_recom_user_id, last_recom_pubg_nik, admin_display, last_recom_reason, last_recom_position, date, id_recom))
#     connection.commit()
#     try:
#         await bot.send_message(chat_id=last_recom_user_id, text=f'{voscl} Поздравляю {voscl}\nВы получили рекомендацию от <i>{admin_display}</i>\n<b>Причина рекомендации:</b> {last_recom_reason}\n<b>Должность:</b> {last_recom_position}', parse_mode='html')
#     except TelegramBadRequest:
#         pass
#     return {"status": "ok"}


# @app.post('/create-link')
# def create_link(action: CreateLinkAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     sost = action.sost
#     activate_count = action.activate_count
#     link = f"WERTY-{password_generator.generate(length=8, chars='ASDFGHJKL12345678')}"
#     print(f'create_link {link} sost={sost} count={activate_count} by admin {action.admin_id} ({action.admin_name})')
#     connection = sqlite3.connect(datahelp_path, check_same_thread=False)
#     cursor = connection.cursor()
#     cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)', (link, activate_count, sost))
#     connection.commit()
#     connection.close()
#     return {"link": link, "activate_count": activate_count, "sost": sost}


# @app.post('/delete-link')
# def delete_link(action: DeleteLinkAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     print(f'delete_link {action.link} by admin {action.admin_id} ({action.admin_name})')
#     connection = sqlite3.connect(datahelp_path, check_same_thread=False)
#     cursor = connection.cursor()
#     cursor.execute('DELETE FROM links_for_sosts WHERE link_text = ?', (action.link,))
#     deleted = cursor.rowcount
#     connection.commit()
#     connection.close()
#     if deleted == 0:
#         raise HTTPException(status_code=404, detail="Link not found")
#     return {"status": "ok", "deleted": deleted}


# @app.get('/all-links')
# def get_all_links():
#     connection = sqlite3.connect(datahelp_path, check_same_thread=False)
#     cursor = connection.cursor()
#     cursor.execute('SELECT link_text, activate_count, sost FROM links_for_sosts')
#     rows = cursor.fetchall()
#     connection.close()
#     links = [{"link": row[0], "activate_count": row[1], "sost": row[2]} for row in rows]
#     return links


# @app.get('/warns/{chat}/{user}')
# async def get_warns(chat: str, user: int):
#     connection = sqlite3.connect(warn_path, check_same_thread=False)
#     cursor = connection.cursor()
#     cursor.execute(f"SELECT warns_count FROM [{(chats_names[chat])}] WHERE tg_id=?", (user,))
#     row = cursor.fetchone()
#     cnt = row[0] if row else 0

#     warns = []
#     if cnt > 0:
#         cursor.execute(f"SELECT first_warn, second_warn, therd_warn, first_moder, second_moder, therd_moder FROM [{(chats_names[chat])}] WHERE tg_id=?", (user,))
#         row = cursor.fetchone()
#         first_warn, second_warn, therd_warn = row[0], row[1], row[2]
#         first_moder, second_moder, therd_moder = row[3], row[4], row[5]

#         if first_warn:
#             warns.append({"num": 1, "reason": first_warn, "moder": first_moder})
#         if second_warn:
#             warns.append({"num": 2, "reason": second_warn, "moder": second_moder})
#         if therd_warn:
#             warns.append({"num": 3, "reason": therd_warn, "moder": therd_moder})

#     return warns[:3]


# @app.post("/ban")
# async def ban(action: BanAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")

#     ensure_not_self_action(action.admin_id, int(action.userid), 'ban')
    
#     chat = action.chat
#     userid = action.userid
#     reason = action.reason
#     admin_id = action.admin_id
#     admin_name = action.admin_name
#     print(f'b {chat} {userid} {reason} by admin {admin_id} ({admin_name})')
#     await admin_ban(chat, int(userid), reason, admin_id, admin_name)
#     return {"status": "ok"}

# @app.post("/dell")
# def dell(action: UserAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")

#     ensure_not_self_action(action.admin_id, int(action.userid), 'delete')
    
#     chat = action.chat
#     userid = action.userid
#     print(f'd {chat} {userid} by admin {action.admin_id} ({action.admin_name})')
#     chat_id = chats_names.get(chat)
#     if chat_id is None:
#         raise HTTPException(status_code=404, detail="Chat not found")
#     dell_sdk(chat_id, int(userid))
#     return {"status": "ok"}

# @app.post("/full_dell")
# def full_dell(action: UserAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")

#     ensure_not_self_action(action.admin_id, int(action.userid), 'full delete')
    
#     chat = action.chat
#     userid = action.userid
#     print(f'fd {chat} {userid} by admin {action.admin_id} ({action.admin_name})')
#     full_dell_sdk(userid)
#     return {"status": "ok"}



# @app.post("/snat_warn")
# async def snat_warn(action: SnatWarnAction):
#     # Проверка прав доступа
#     if not check_admin_rights(action.admin_id):
#         raise HTTPException(status_code=403, detail="Access denied")

#     ensure_not_self_action(action.admin_id, int(action.userid), 'remove warn')
    
#     chat = action.chat
#     userid = action.userid
#     num = action.num
#     admin_name = action.admin_name
#     connection = sqlite3.connect(warn_path, check_same_thread=False)
#     cursor = connection.cursor()
#     cursor.execute(f"SELECT warns_count FROM [{(chats_names[chat])}] WHERE tg_id=?", (userid,))
#     row = cursor.fetchone()
#     cnt = row[0] if row else 0

#     await admin_warn_dell(int(userid), chats_names[chat], num, max(cnt - 1, 0), admin_name)
#     print(f'snat_warn {chat} {userid} {num} by admin {action.admin_id} ({action.admin_name})')
#     return {"status": "ok"}

# @app.post('/send-link-to-bot')
# async def send_link_to_bot(action: SendLinkToBotAction):
#     try:
#         # Проверка прав доступа
#         if not check_admin_rights(action.admin_id):
#             raise HTTPException(status_code=403, detail="Access denied")
#         # Отправляем ссылку в админ-бот
#         admin_chat_id = [8015726709, 1240656726]  # ID админа (можно вынести в конфиг)
#         for us in admin_chat_id:
#             await bot.send_message(
#                 us,
#                 f"🔗 Новая ссылка создана:\n\n<code>{action.link}</code>\n\n📊 Параметры:\n• Состав: {action.sost}\n• Активаций: {action.activate_count}",
#                 parse_mode='HTML'
#             )
#         return {"status": "ok"}
#     except Exception as e:
#         print(f'Error sending link to bot: {e}')
#         return {"status": "error", "error": str(e)}

# ssl_context.load_cert_chain('/etc/letsencrypt/live/ezh-dev.ru/cert.pem', keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem')


# if  __name__ == '__main__':
#     uvicorn.run('api:app', reload=True, host="0.0.0.0", ssl_keyfile='/etc/letsencrypt/live/ezh-dev.ru/privkey.pem', ssl_certfile='/etc/letsencrypt/live/ezh-dev.ru/cert.pem')
