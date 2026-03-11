import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Тестируем простой эндпоинт
url = "https://ezh-dev.ru:3000/"

try:
    response = requests.get(url, verify=False)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")
