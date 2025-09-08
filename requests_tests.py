# requests_tests.py
import requests
import urllib3
import config

# Отключаем предупреждения о небезопасном HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = config.AUTH_URL
HEADERS = {'Authorization': config.AUTH_TOKEN}


def get_interfaces(interface: str):
    response = requests.get(
        url=f'{URL}/interfaces/list',
        headers=HEADERS,
        params={'category': interface},
        verify=False
    )
    return response.json()


def post_request(endpoint: str, body: dict):
    ...
