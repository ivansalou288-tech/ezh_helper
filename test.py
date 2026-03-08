from pydantic.types import T
from main.config3 import *
from api import *
def get_warns(chat: str, user: int):
    chat_id = chats_names[chat]
    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM [{(chat_id)}] WHERE tg_id=?", (user,))
    warnlist = []
    try:
        warns = cursor.fetchall()[0]
        warns_count = warns[1]
        first_warn = warns[2]
        second_warn = warns[3]
        therd_warn = warns[4]
        first_mod = warns[5]
        second_mod = warns[6]
        therd_mod = warns[7]
        print(therd_mod)
        # if first_warn == None or first_warn == 'None':
        #     first_warn = ''
        # if second_warn == None or second_warn == 'None':
        #     second_warn = ''
        # if therd_warn == None or therd_warn == 'None':
        #     therd_warn = ''
        frst = {"num": 1,
                "reason": first_warn,
                "moder": first_mod,}
        second = {"num": 2,
                  "reason": second_warn,
                  "moder": second_mod}
        thrd = {"num": 3,
                  "reason": therd_warn,
                  "moder": therd_mod}
        if first_mod != '' and first_mod != ' ' and first_mod != None and first_mod != 'None':
            warnlist.append(frst)
        if second_mod != '' and second_mod != ' ' and second_mod != None and second_mod != 'None':
            warnlist.append(second)
        if therd_mod != '' and therd_mod != ' ' and therd_mod != None and therd_mod != 'None':
            warnlist.append(thrd)
        return warnlist
    except IndexError:
        return warnlist

print(get_warns('sost-1',1987276133))