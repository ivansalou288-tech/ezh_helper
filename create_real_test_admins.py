import sqlite3

# Создаем тестовых администраторов для чата -1003012971064
conn = sqlite3.connect('databases/admin.db')
cursor = conn.cursor()

# Тестовые администраторы для реального чата
test_admins = [
    (2145327187, -1003012971064, 'Real Admin 1', 1, 1, 1, 0, 0),  # 3 права
    (5272451448, -1003012971064, 'Real Admin 2', 0, 1, 1, 1, 0),  # 3 права  
    (5763062214, -1003012971064, 'Real Admin 3', 1, 1, 1, 1, 1),  # 5 прав
    (1401086794, -1003012971064, 'Real Admin 4', 0, 0, 0, 0, 0),  # 0 прав
]

for admin in test_admins:
    user_id, chat_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk = admin
    cursor.execute('''
        INSERT OR REPLACE INTO admins 
        (user_id, chat_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', admin)

conn.commit()

# Проверяем что добавилось
cursor.execute('SELECT user_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk FROM admins WHERE chat_id = ?', (-1003012971064,))
results = cursor.fetchall()

print("Тестовые администраторы в чате -1003012971064:")
for result in results:
    user_id, chat_name, see_users, do_admin, recom, links, dk = result
    active_rights = sum([see_users, do_admin, recom, links, dk])
    print(f"User {user_id} ({chat_name}): {active_rights} прав")

conn.close()
print("\nТеперь есть тестовые администраторы для реального чата!")
