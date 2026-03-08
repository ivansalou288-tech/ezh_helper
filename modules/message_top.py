import html
import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Optional

from aiogram import Router, types, F, Bot
from main.config3 import get_db_path, init_chat_db, chats

router = Router()



def _parse_limit(text: Optional[str], default: int = 10, max_limit: int = 50) -> int:
    if not text:
        return default
    parts = text.strip().split()
    if not parts:
        return default
    # поддержка: "топ сообщений 20"
    last = parts[-1]
    if last.isdigit():
        try:
            val = int(last)
            if val < 1:
                return default
            return min(val, max_limit)
        except Exception:
            return default
    return default


def _detect_message_counter_column(cursor: sqlite3.Cursor) -> Optional[str]:
    try:
        cols = [row[1] for row in cursor.execute(f"PRAGMA table_info([users])").fetchall()]
    except sqlite3.OperationalError:
        return None
    for candidate in ("mess_count", "message_count", "messages_count", "msg_count", "messages"):
        if candidate in cols:
            return candidate
    return None

#? EN: Shows the all‑time top users by message count in this chat (supports optional limit like «!топ сообщений 20»).
#* RU: Показывает топ пользователей по количеству сообщений за всё время в этом чате (поддерживает лимит, например «!топ сообщений 20»).
@router.message(
    F.text.lower().startswith(("топ вся", "!топ сообщений")),
    ~F.is_forward()
)
async def show_messages_top_all_time(message: types.Message) -> None:
    # Только в группах
    if message.chat.id == message.from_user.id:
        await message.answer("📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!")
        return

    # Только в рабочих чатах
    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    limit = _parse_limit(message.text)
    chat_id = message.chat.id
    
    # Initialize database for this chat if it doesn't exist
    init_chat_db(chat_id)
    
    db_path = get_db_path(chat_id)
    connection = sqlite3.connect(db_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        counter_col = _detect_message_counter_column(cursor)
        if not counter_col:
            await message.reply("📝В базе не найдено поле счётчика сообщений (ожидаю `mess_count`).")
            return

        try:
            rows = cursor.execute(
                f"""
                SELECT tg_id, username, nik, name, {counter_col}
                FROM users
                ORDER BY {counter_col} DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        except sqlite3.OperationalError:
            await message.reply("📝Не найдена таблица пользователей этого чата в базе.")
            return

        lines = []
        place = 0
        for tg_id, username, nik, name, cnt in rows:
            # служебная строка, которую иногда кладут как "all"
            if username == "all":
                continue
            try:
                tg_id_int = int(tg_id)
            except Exception:
                continue
            try:
                cnt_int = int(cnt or 0)
            except Exception:
                cnt_int = 0

            display = nik or name or (f"@{username}" if username else None) or "Пользователь"
            place += 1
            if place == 1:
                mest = '🥇'
            elif place == 2:
                mest = '🥈'
            elif place == 3:
                mest = '🥉'
            else:
                mest = place
            lines.append(
                f"<b>{mest}.</b> <a href=\"tg://user?id={tg_id_int}\">{html.escape(str(display))}</a> — <b>{cnt_int}</b>"
            )

            if place >= limit:
                break

        if not lines:
            await message.reply("📝Пока нет данных для топа сообщений.")
            return

        text = "🏆 <b>Топ сообщений за всё время</b>\n\n" + "\n".join(lines)
        await message.reply(text, parse_mode="HTML", disable_web_page_preview=True)
    finally:
        try:
            connection.close()
        except Exception:
            pass


