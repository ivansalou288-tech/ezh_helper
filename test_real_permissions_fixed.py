import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Тестируем реальных пользователей из логов
test_users = [
    (2145327187, 3),  # Real Admin 1
    (5272451448, 3),  # Real Admin 2  
    (5763062214, 5),  # Real Admin 3
    (1401086794, 0),  # Real Admin 4
    (999999999, 0),   # Не существует
]

chat_id = -1003012971064

print("Тестирование эндпоинта /user_permissions:")
print("="*50)

for user_id, expected_rights in test_users:
    try:
        url = f"https://ezh-dev.ru:3000/user_permissions/{chat_id}/{user_id}"
        response = requests.get(url, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                perms = data.get("data", {})
                actual_rights = sum([v for k, v in perms.items() if isinstance(v, bool) and v])
                status = "OK" if actual_rights == expected_rights else "FAIL"
                print(f"{status} User {user_id}: {actual_rights} прав (ожидалось: {expected_rights})")
            else:
                print(f"FAIL User {user_id}: API Error - {data.get('message')}")
        else:
            print(f"FAIL User {user_id}: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"FAIL User {user_id}: Network Error - {e}")

print("="*50)
print("Готово! Теперь индикаторы прав должны работать в admin_functions.html")
