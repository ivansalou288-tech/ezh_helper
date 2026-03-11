import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Тестируем старый эндпоинт проверки кода
url = "https://ezh-dev.ru:3000/check_invite_code"
data = {"code": "test123"}

try:
    response = requests.post(url, json=data, verify=False)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
