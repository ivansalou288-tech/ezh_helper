import requests
import json

# Тестируем новый эндпоинт
url = "https://ezh-dev.ru:3000/generate_invite_links_by_code"
data = {
    "code": "test123",
    "telegram_id": 123456789,
    "username": "testuser"
}

try:
    response = requests.post(url, json=data)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "success":
            print("✅ Эндпоинт работает!")
            print(f"Чатов найдено: {result['data']['count']}")
            for chat in result['data']['chats']:
                print(f"  - {chat['name']} ({chat['chat_id']})")
        else:
            print(f"❌ Ошибка API: {result.get('message')}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
