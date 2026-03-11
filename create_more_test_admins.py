import sqlite3

# Создаем дополнительных тестовых администраторов
conn = sqlite3.connect('databases/admin.db')
cursor = conn.cursor()

# Тестовые администраторы с разными правами
test_admins = [
    (987654321, 1002143434937, 'Admin User 1', 1, 0, 1, 0, 0),  # 2 права
    (555666777, 1002143434937, 'Admin User 2', 0, 1, 1, 1, 0),  # 3 права  
    (111222333, 1002143434937, 'Admin User 3', 1, 1, 1, 1, 1),  # 5 прав
    (444555666, 1002143434937, 'Admin User 4', 0, 0, 0, 0, 0),  # 0 прав (только запись в admins)
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
cursor.execute('SELECT user_id, chat_name, can_see_users, can_do_admin, can_recom, can_links, can_dk FROM admins WHERE chat_id = ?', (1002143434937,))
results = cursor.fetchall()

print("Тестовые администраторы в чате 1002143434937:")
for result in results:
    user_id, chat_name, see_users, do_admin, recom, links, dk = result
    active_rights = sum([see_users, do_admin, recom, links, dk])
    print(f"User {user_id} ({chat_name}): {active_rights} прав")

conn.close()
print("\nТеперь есть 5 тестовых администраторов с разным количеством прав!")
