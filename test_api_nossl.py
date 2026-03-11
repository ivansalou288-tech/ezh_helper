import requests
import json
import urllib3

# Отключаем проверку SSL для теста
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Тестируем новый эндпоинт
url = "https://ezh-dev.ru:3000/generate_invite_links_by_code"
data = {
    "code": "test123",
    "telegram_id": 123456789,
    "username": "testuser"
}

try:
    response = requests.post(url, json=data, verify=False)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "success":
            print("API endpoint works!")
            print(f"Chats found: {result['data']['count']}")
            for chat in result['data']['chats']:
                print(f"  - {chat['name']} ({chat['chat_id']})")
        else:
            print(f"API Error: {result.get('message')}")
    else:
        print(f"HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"Connection Error: {e}")
