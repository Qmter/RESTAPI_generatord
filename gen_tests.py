# gen_tests.py
import json
import os
import sys
from jsf import JSF
import jsonref
from openapi_utils import generate_fake_data, load_openapi_schema, generate_fake_data_add, generate_fake_data_interfaces
import requests_tests
from generate_tests import find_args
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


def make_test(endpoint: str, method: str, resolved_schema: dict, schem_args: list = None, interface_type: str = ''):
    test_json = {}

    test_json["PRESET"] = {}


    for i in range(20):

        test_schema = generate_fake_data(resolved_schema)

        test_json[f'{i}'] = {}

        test_json[f'{i}'] = {
            'type': method.upper(),
            'endpoint': endpoint,
            'schema': test_schema
        }


    
    test_json['AFTER-TEST'] = {}

    print('ИСПОЛЬЗОВАННЫЕ АРГУМЕНТЫ: ', schem_args)

    

    
    return test_json


def main(endpoint: str, method: str):

    interface_type = identify_interface(endpoint=endpoint)

    resolved_schema = load_openapi_schema(
        openapi_path=OPENAPI_FILE,
        endpoint=endpoint,
        method=method
    )

    if len(resolved_schema) == 0:
        print('Нет аргументов у ендпоинта')
        return {}

    if method == 'post':
        # Находим все аргументы, которые присутствуют в схеме POST
        if resolved_schema.get("type") == "object" and "properties" in resolved_schema:
            schem_args = find_args(
                resolved_schema['properties'], method=method)
            # Удаляем служебные ключи, которые не являются полями в теле запроса
            schem_args = [arg for arg in schem_args if arg != 'const']
        else:
            schem_args = []

    elif method == 'get':
        # Находим все аргументы, которые присутствуют в схеме GET
        schem_args = [key for key in resolved_schema.get(
            "properties", {}).keys() if key != 'const']
        

    test = make_test(endpoint=endpoint, method=method, interface_type=interface_type, resolved_schema=resolved_schema, schem_args=schem_args)
    #print(json.dumps(test, indent=2))
    with open(f'{TEST_FOLDER}/{endpoint.replace('/', '_')[1:]}_{method.upper()}.json', 'w', encoding='utf-8') as f:
        json.dump(test, f, indent=2, ensure_ascii=False)

    


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Использование: python generate_tests.py <endpoint> [method]")
    #     sys.exit(1)

    # endpoint = sys.argv[1]
    # method = sys.argv[2].lower() if len(sys.argv) > 2 else "post"

    # # Проверяем наличие эндпоинта и метода
    # if endpoint not in openapi["paths"]:
    #     print(f"Эндпоинт не найден: {endpoint}")
    #     sys.exit(1)

    # path_item = openapi["paths"][endpoint]
    # if method not in path_item:
    #     print(f"Метод {method.upper()} не найден для {endpoint}")
    #     sys.exit(1)

    with open('endpoints.txt', 'r', encoding='utf-8') as f:
        endpoints = f.read()
    
    endpoints_list = endpoints.split('\n')
    
    for i in endpoints_list:
        main(endpoint=i.split('%')[0], method=i.split('%')[1])
