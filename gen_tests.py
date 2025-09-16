# gen_tests.py
import json
import os
import sys
from jsf import JSF
import jsonref
from openapi_utils import generate_fake_data, load_openapi_schema, generate_fake_data_add, generate_fake_data_interfaces
import requests_tests
import time
import random
import mock_data

# Настройки
OPENAPI_FILE = "config/openapi.json"
TEST_FOLDER = 'tests'


# Загружаем OpenAPI
if not os.path.exists(OPENAPI_FILE):
    print(f"Файл не найден: {OPENAPI_FILE}")
    sys.exit(1)

# Читаем OpenAPI
with open(OPENAPI_FILE, "r", encoding="utf-8") as f:
    openapi = json.load(f)


def identify_interface(endpoint: str):
    for i in mock_data.interfaces.keys():
        if i in endpoint:
            return i

    return ''


def main(endpoint: str, method: str):

    interface = identify_interface(endpoint=endpoint)

    resolved_schema = load_openapi_schema(
        openapi_path=OPENAPI_FILE,
        endpoint=endpoint,
        method=method
    )

    if len(resolved_schema) == 0:
        print('Нет аргументов у ендпоинта')
        return {}

    print('')

    


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python generate_tests.py <endpoint> [method]")
        sys.exit(1)

    endpoint = sys.argv[1]
    method = sys.argv[2].lower() if len(sys.argv) > 2 else "post"

    # Проверяем наличие эндпоинта и метода
    if endpoint not in openapi["paths"]:
        print(f"Эндпоинт не найден: {endpoint}")
        sys.exit(1)

    path_item = openapi["paths"][endpoint]
    if method not in path_item:
        print(f"Метод {method.upper()} не найден для {endpoint}")
        sys.exit(1)

    main(endpoint=endpoint, method=method)
