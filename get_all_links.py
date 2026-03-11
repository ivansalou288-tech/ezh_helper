import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Получаем все ссылки с сервера
url = "https://ezh-dev.ru:3000/api/links/all"

try:
    response = requests.get(url, verify=False)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
