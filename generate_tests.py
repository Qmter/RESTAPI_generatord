# generate_tests.py

import json
import os
import sys
from jsf import JSF
import jsonref
from openapi_utils import generate_fake_data, load_openapi_schema


# Настройки
OPENAPI_FILE = "config/openapi.json"


# Загружаем OpenAPI
if not os.path.exists(OPENAPI_FILE):
    print(f"Файл не найден: {OPENAPI_FILE}")
    sys.exit(1)

with open(OPENAPI_FILE, "r", encoding="utf-8") as f:
    openapi = json.load(f)



def make_preset(endpoint: str, method: str):
    
    # Разрешаем схему с $ref
    resolved_shema = load_openapi_schema(
        openapi_path=OPENAPI_FILE,
        endpoint=endpoint,
        method=method
    )

    if 'add' in endpoint:
        print("ADDD")
    if 'delete' in endpoint:
        print('DELETE')
    if 'capability' in endpoint:
        print(*resolved_shema['properties']['capability']['properties'].keys())
        print("CAPABILITY")


def make_after_test(endpoint: str, method: str, created_interfaces: list):
    ...




def find_args(schema: dict, used_args = []) -> list:
    for i in schema:
        used_args.append(i)
        if 'type' in schema[i]:
            if schema[i]['type'] == 'object':
                    return find_args(schema[i]['properties'], used_args)
        if 'oneOf' in schema[i]:
            for i in schema[i]['oneOf']:
                if 'properties' in i:
                    return find_args(i['properties'], used_args)
                elif 'const' in i:
                    used_args.append(list(i.keys())[0])


    
    return used_args

def main(endpoint: str, method: str):

    # Разрешаем схему с $ref
    resolved_shema = load_openapi_schema(
        openapi_path=OPENAPI_FILE,
        endpoint=endpoint,
        method=method
    )

    data = generate_fake_data(resolved_shema)

    used_args = find_args(resolved_shema['properties'])

    print(used_args)


    for i in range(10):
        data = generate_fake_data(resolved_shema)
        while len(data) == 1:
            data = generate_fake_data(resolved_shema)
        print(data, '----', len(data))




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

    # operation = path_item[method]

    # Запуск
    main('/interfaces/bonding/capability', 'get')
    # make_preset(endpoint, method, operation)