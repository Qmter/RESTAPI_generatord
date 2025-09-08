# generate_tests.py

import json
import os
import sys
from jsf import JSF
import jsonref
from openapi_utils import generate_fake_data, load_openapi_schema, generate_fake_data_add
import requests_tests


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


# Фуенкия для создания PRESET в тестах
def make_preset(endpoint: str, method: str, available_interfaces: list, interface_type: str) -> dict:
    """Функция для создания PRESET
    endpoint - тестиремый ендпоинт,
    method - метод HTTP,
    available_interfaces - существующие интерфейсы,
    interface_type - тип интерфейса (eth. vlan. bond и т.д.)
    """
    # Разрешаем схему с $ref
    resolved_shema = load_openapi_schema(
        openapi_path=OPENAPI_FILE,
        endpoint=endpoint,
        method=method
    )

    # Создаем схему теста
    test_json = {}

    # Добавляем ключ PRESET в схему теста
    test_json["PRESET"] = {}

    # Индикатор шагов PRESET
    test_step = 1

    # Проверки на действия ендпоинтов
    # Проверка есть в ендпоинте delete
    if 'delete' in endpoint:
        # создаем ендпоинт с противополоным действеим delete -> add
        endpoint_add = '/'.join(endpoint.split('/')[:-1]) + '/add'

        # Разрешаем схему на добавление
        resolved_shema_add = load_openapi_schema(
            openapi_path=OPENAPI_FILE,
            endpoint=endpoint_add,
            method=method
        )

        # Создаем сам тест
        test_json["PRESET"][f"{test_step}"] = {
            "type": method.upper(),
            "endpoint": endpoint_add,
            "schema": generate_fake_data_add(resolved_shema_add, available_interfaces=available_interfaces),
            "errCode": 0,
            "httpCode": 200
        }

        # Возвращаем созданный тест
        return test_json

    # if 'capability' in endpoint:
    #     print("CAPABILITY")
    # Возвразаем пустой PRESET если не трубуется
    return test_json


# Фунеция для создания оснвных тестов
def make_tests(endpoint: str, method: str, available_interfaces: list, interface_type: str) -> dict:
    """Функция для создания основных тестов
    endpoint - тестиремый ендпоинт,
    method - метод HTTP,
    available_interfaces - существующие интерфейсы,
    interface_type - тип интерфейса (eth. vlan. bond и т.д.)"""

    # Проверки на действия ендпоинтов
    if 'add' in endpoint:
        ...
    if 'delete' in endpoint:
        ...
    if 'capability' in endpoint:
        ...


def make_after_test(endpoint: str, method: str, available_interfaces: list) -> dict:
    ...


# Функция для рекурсивного нахождения требуемых аргументов в ендпоинте
def find_args(schema: dict, method: str, used_args=[]) -> list:
    """Функция для рекурсивного нахождения требуемых аргументов в ендпоинте
    schema - разрешенная схема ендпоинта,
    method - метод HTTP,
    user_args - список аргументов, которые используются в ендпоинте"""

    #  Проверка методов (так как в разных методах используются разные ключи(post - requestBody, get - parameters))
    if method == 'post':
        for i in schema:
            used_args.append(i)
            if 'type' in schema[i]:
                if schema[i]['type'] == 'object':
                    return find_args(schema[i]['properties'], method='post')
            if 'oneOf' in schema[i]:
                for i in schema[i]['oneOf']:
                    if 'properties' in i:
                        return find_args(i['properties'], method='post')
                    elif 'const' in i:
                        used_args.append(list(i.keys())[0])

    if method == 'get':
        for i in schema:
            used_args.append(i)

    # Возвращае  список использованных аргументов
    return used_args


def main(endpoint: str, method: str):

    interface = ''

    # Разрешаем схему с $ref
    resolved_schema = load_openapi_schema(
        openapi_path=OPENAPI_FILE,
        endpoint=endpoint,
        method=method
    )

    # Определяем какой тип интерфейса в ендпоинте
    if 'ethernet' in endpoint:
        interface = 'ethernet'
    if 'bonding' in endpoint:
        interface = 'bonding'
    if 'bridge' in endpoint:
        interface = 'bridge'
    if 'vlan' in endpoint:
        interface = 'vlan'
    if 'eth_vlan' in endpoint:
        interface = 'eth-vlan'
    if 'loopback' in endpoint:
        interface = 'loopback'
    if 'switchport' in endpoint:
        interface = 'switchport'
    if 'tunnel' in endpoint:
        interface = 'tunnel'
    if 'wlan' in endpoint:
        interface = 'wlan'

    print('---------------------------')
    print('ИНТЕРФЕЙС:')
    print(interface)
    print('---------------------------')

    # Вспомагательный запрос для получения существующих интерфейсов
    response_interfaces = requests_tests.get_interfaces(interface=interface)
    available_interfaces = response_interfaces['result']['interfaces'][0]['ifname']

    print('ДОСТУПНЫЕ ИНТЕРФЕЙСЫ ----', available_interfaces)

    print()

    print('---------------------------')
    print("РАЗРЕШЕННАЯ СХЕМА:")
    print(json.dumps(resolved_schema, indent=2))
    print('---------------------------')

    if method == 'post':
        used_args = find_args(resolved_schema['properties'], method=method)

        print('---------------------------')
        print('ИСПОЛЬЗОВАННЫЕ АРГУМЕНТЫ:')
        print(used_args)
        print('---------------------------')

        print('---------------------------')
        print('ФЕЙКОВЫЕ ДАННЫЕ:')
        for i in range(10):
            print(f'ДАННЫЕ №{i}')
            data = generate_fake_data(
                resolved_schema, available_interfaces=available_interfaces)
            print(data)
            print('---------------------------')

    elif method == 'get':
        used_args = list(resolved_schema.get("properties", {}).keys())

        print('---------------------------')
        print('ИСПОЛЬЗОВАННЫЕ АРГУМЕНТЫ:')
        print(used_args)
        print('---------------------------')

        print('---------------------------')
        print('ФЕЙКОВЫЕ ДАННЫЕ:')
        for i in range(10):
            print(f'ДАННЫЕ №{i}')
            data = generate_fake_data(
                resolved_schema, available_interfaces=available_interfaces)
            print(data)
            print('---------------------------')

    # Получаем PRESET для ендпоинта
    preset = make_preset(endpoint=endpoint, method=method,
                         available_interfaces=available_interfaces, interface_type=interface)
    print('---------------------------')
    print("PRESET")
    print(json.dumps(preset, indent=1))
    print('---------------------------')

    # print(preset['PRESET']['1']['schema'])


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

    operation = path_item[method]

    # Запуск
    main(endpoint=endpoint, method=method)
    # make_preset(endpoint, method, operation)
