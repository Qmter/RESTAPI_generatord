# generate_tests.py

import json
import os
import sys
from jsf import JSF
import jsonref
from openapi_utils import generate_fake_data, load_openapi_schema, generate_fake_data_add, generate_fake_data_interfaces
import requests_tests
import time
import random


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


# Функция для рекурсивного нахождения требуемых аргументов в ендпоинте
def find_args(schema: dict, method: str, used_args=[]) -> list:
    """Функция для рекурсивного нахождения требуемых аргументов в ендпоинте
    schema - разрешенная схема ендпоинта,
    method - метод HTTP,
    user_args - список аргументов, которые используются в ендпоинте"""

    if used_args is None:
        used_args = []

    if not isinstance(schema, dict):
        return used_args

    if method == 'post':
        for key in schema:
            # Добавляем ключ (например, имя поля)
            used_args.append(key)

            prop = schema[key]
            if not isinstance(prop, dict):
                continue

            # Если это объект с properties
            if prop.get("type") == "object":
                if "properties" in prop:
                    find_args(prop["properties"], method="post")
                elif "oneOf" in prop:
                    for option in prop["oneOf"]:
                        if isinstance(option, dict):
                            if "properties" in option:
                                find_args(option["properties"], method="post")
                            elif "const" in option:
                                used_args.append(list(option.keys())[0])

            # Если это oneOf на верхнем уровне (не внутри object)
            elif "oneOf" in prop:
                for option in prop["oneOf"]:
                    if isinstance(option, dict):
                        if option.get("type") == "object" and "properties" in option:
                            find_args(option["properties"], method="post")
                        elif "const" in option:
                            used_args.append(list(option.keys())[0])

            # Если это массив с объектом
            elif prop.get("type") == "array" and isinstance(prop.get("items"), dict):
                items = prop["items"]
                if items.get("type") == "object" and "properties" in items:
                    find_args(items["properties"], method="post")

    elif method == 'get':
        used_args.extend(schema.keys())

    return used_args


# Функция для подсчета аргументов в тестируемой схеме
def count_args_in_test_schema(schema: dict, used_args=None):
    """
    Рекурсивно собирает ВСЕ ключи из переданного объекта (включая вложенные).
    Не добавляет дубликаты.
    """
    if used_args is None:
        used_args = []

    if not isinstance(schema, dict):
        return used_args

    for key, value in schema.items():
        if key not in used_args:
            used_args.append(key)

        # Рекурсивно обходим вложенные объекты и массивы
        if isinstance(value, dict):
            count_args_in_test_schema(value, used_args)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    count_args_in_test_schema(item, used_args)

    return used_args


# Фуенцкия для создания PRESET в тестах
def make_preset(endpoint: str, method: str, interface_type: str, available_interfaces=[]) -> dict:
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
        resolved_schema_add = load_openapi_schema(
            openapi_path=OPENAPI_FILE,
            endpoint=endpoint_add,
            method='post'
        )

        # Создаем сам тест
        test_json["PRESET"][f"{test_step}"] = {
            "type": method.upper(),
            "endpoint": endpoint_add,
            "schema": generate_fake_data_add(resolved_schema_add, available_interfaces=available_interfaces),
        }

        # Возвращаем созданный тест
        return test_json

    if 'capability' in endpoint:
        # создаем ендпоинт для добавления интерфейса
        endpoint_add = '/'.join(endpoint.split('/')[:-1]) + '/add'

        print(f'endpoint_add - {endpoint_add}')

        # Разрешаем схему на добавление
        resolved_schema_add = load_openapi_schema(
            openapi_path=OPENAPI_FILE,
            endpoint=endpoint_add,
            method='post'
        )

        if resolved_schema_add == {}:
            return {"PRESET": {}}

        schema = generate_fake_data_add(
            resolved_schema_add, available_interfaces=available_interfaces)

        # Создаем сам тест
        test_json["PRESET"][f"{test_step}"] = {
            "type": method.upper(),
            "endpoint": endpoint_add,
            "schema": schema,
        }

        # Возвращаем созданный тест
        return test_json
    # Возвразаем пустой PRESET если не трубуется
    return {"PRESET": {}}


# Фунеция для создания оснвных тестов
def make_tests(endpoint: str, method: str, interface_type: str, endpoint_args: list, available_interfaces=[]) -> dict:
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
        # Разрешаем схему с $ref
        resolved_schema = load_openapi_schema(
            openapi_path=OPENAPI_FILE,
            endpoint=endpoint,
            method=method
        )

        # Список аргументов, которые использовались в тестах
        used_args = []

        # Создаем схему теста
        test_json = {}

        # Индикатор шагов теста
        test_step = 1

        # Внутренний индикатор шагов одного теста
        test_step_inside = 1

        # если нету интерфейсов для тестаирования, то создаем PRESET в котором добавляем интерфейс
        preset = make_preset(
            endpoint=endpoint, method=method, interface_type=interface_type)
        # меняем переменную available_interfaces на созданную в PRESET для дальнейшего использования в тестах
        if preset['PRESET'] != {}:
            available_interfaces = [
                preset['PRESET']['1']['schema']['ifname']]

        # Создаем ключи PRESET в тесте
        test_json = preset

        # Создаем ключ шага теста
        test_json[f"{test_step}"] = {}

        # Создаем 5 тестов для генерации (в дальнейшем заменить на проверку всех аргументов ендпоинта)
        while set(sorted(endpoint_args)) != set(sorted(used_args)):
            schema = generate_fake_data_interfaces(
                resolved_schema, available_interfaces=available_interfaces)
            # заменяем рандомно созданный интерфейс на тот который мы создали в PRESET
            schema['ifname'] = random.choice(available_interfaces)

            # Создаем сам тест
            test_json[f"{test_step}"][f"{test_step}.{test_step_inside}"] = {
                "type": method.upper(),
                "endpoint": endpoint,
                "schema": schema,
            }

            # Дополняем used_args на спиок аргументов, который использовался в тестых
            used_args = count_args_in_test_schema(
                schema=schema, used_args=used_args)

            print(used_args, 'АРГУМЕНТЫ ЗА ТЕСТ')

            # print(f'TRY number {test_step_inside}')
            # print(f"shema = {schema}")
            # print(f'endpoint args - {set(endpoint_args)}')
            # print(f'gen args - {set(used_args)}')

            # Увеличиваем внутренний индекс шана на 1
            test_step_inside += 1

        # Возваращаем тест
        return test_json


def make_after_test(endpoint: str, method: str, available_interfaces: list) -> dict:

    ...


def main(endpoint: str, method: str):

    # Создаем переменну interfaces
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

    # print('---------------------------')
    # print('ИНТЕРФЕЙС:')
    # print(interface)
    # print('---------------------------')

    if len(resolved_schema) == 0:
        print('Нет аргументов!')
    else:
        if interface != '':
            # Вспомагательный запрос для получения существующих интерфейсов
            response_interfaces = requests_tests.get_interfaces(
                interface=interface)
            available_interfaces = response_interfaces['result']['interfaces'][0]['ifname']

            # print('ДОСТУПНЫЕ ИНТЕРФЕЙСЫ ----', available_interfaces)

            # print()

            print('---------------------------')
            print("РАЗРЕШЕННАЯ СХЕМА:")
            print(json.dumps(resolved_schema, indent=2))
            print('---------------------------')

            if method == 'post':
                # Находим все аргументы, которые присутствуют в схеме
                if resolved_schema.get("type") == "object" and "properties" in resolved_schema:
                    used_args = find_args(
                        resolved_schema['properties'], method=method)
                    # Удаляем служебные ключи, которые не являются полями в теле запроса
                    used_args = [arg for arg in used_args if arg != 'const']
                else:
                    used_args = []

                # print('---------------------------')
                print('АРГУМЕНТЫ  В СХЕМЕ:')
                print(used_args)
                # print('---------------------------')

                # print('---------------------------')
                # print('ФЕЙКОВЫЕ ДАННЫЕ:')
                # for i in range(10):
                #     print(f'ДАННЫЕ №{i}')
                #     data = generate_fake_data_interfaces(
                #         resolved_schema, available_interfaces=available_interfaces)
                #     print(json.dumps(data, indent=1))
                #     print('---------------------------')

            elif method == 'get':
                # Находим все аргументы, которые присутствуют в схеме
                used_args = [key for key in resolved_schema.get(
                    "properties", {}).keys() if key != 'const']

                # print('---------------------------')
                print('АРГУМЕНТЫ  В СХЕМЕ:')
                print(used_args)
                # print('---------------------------')

                # print('---------------------------')
                # print('ФЕЙКОВЫЕ ДАННЫЕ:')
                # for i in range(10):
                #     print(f'ДАННЫЕ №{i}')
                #     data = generate_fake_data_interfaces(
                #         resolved_schema, available_interfaces=available_interfaces)
                #     print(json.dumps(data, indent=1))
                #     print('---------------------------')

            # # Получаем PRESET для ендпоинта
            # preset = make_preset(endpoint=endpoint, method=method,
            #                      available_interfaces=available_interfaces, interface_type=interface)
            # print('---------------------------')
            # print("PRESET")
            # print(json.dumps(preset, indent=1))
            # print('---------------------------')

            # Запускаем создание тестов
            tests = make_tests(endpoint=endpoint, method=method, available_interfaces=available_interfaces,
                               interface_type=interface, endpoint_args=used_args)
            # print('---------------------------')
            # print("ТЕСТЫ")
            # print(json.dumps(tests, indent=2))

            with open(f'{'_'.join(endpoint.split('/'))}.json', 'w+', encoding='utf-8') as f:
                json.dump(tests, f, indent=2, ensure_ascii=False)

        else:
            print('ЕНДПОИНТ БЕЗ ИНТЕРФЕЙСОВ')

            print()

            print('---------------------------')
            print("РАЗРЕШЕННАЯ СХЕМА:")
            print(json.dumps(resolved_schema, indent=2))
            print('---------------------------')

            if method == 'post':
                # Находим все аргументы, которые присутствуют в схеме
                if resolved_schema.get("type") == "object" and "properties" in resolved_schema:
                    used_args = find_args(
                        resolved_schema['properties'], method=method)
                else:
                    used_args = []

                # print('---------------------------')
                print('АРГУМЕНТЫ  В СХЕМЕ:')
                print(used_args)
                # print('---------------------------')

                # print('---------------------------')
                # print('ФЕЙКОВЫЕ ДАННЫЕ:')
                # for i in range(10):
                #     print(f'ДАННЫЕ №{i}')
                #     data = generate_fake_data(resolved_schema)
                #     print(json.dumps(data, indent=1))
                #     print('---------------------------')

            elif method == 'get':
                # Находим все аргументы, которые присутствуют в схеме
                used_args = list(resolved_schema.get("properties", {}).keys())

                # print('---------------------------')
                print('АРГУМЕНТЫ  В СХЕМЕ:')
                print(used_args)
                # print('---------------------------')

                # print('---------------------------')
                # print('ФЕЙКОВЫЕ ДАННЫЕ:')
                # for i in range(10):
                #     print(f'ДАННЫЕ №{i}')
                #     data = generate_fake_data(
                #         resolved_schema)
                #     print(json.dumps(data, indent=1))
                #     print('---------------------------')

            # # Получаем PRESET для ендпоинта
            # preset = make_preset(
            #     endpoint=endpoint, method=method, interface_type=interface)
            # print('---------------------------')
            # print("PRESET")
            # print(json.dumps(preset, indent=1))
            # print('---------------------------')

            # Запускаем создание тестов
            tests = json.dumps(make_tests(endpoint=endpoint, method=method,
                                          interface_type=interface, endpoint_args=used_args), indent=2)

            with open(f'{'_'.join(endpoint.split('/'))}', 'w+', encoding='utf-8') as f:
                json.dump(tests, f, indent=2, ensure_ascii=False)


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

    main(endpoint=endpoint, method=method)

    # with open('endpoints_methods.txt', 'r', encoding='utf-8') as f:
    #     endpoints = f.read()

    # all_endpoint = endpoints.split('\n')
    # for i in all_endpoint:
    #     print('---------------------------')
    #     print(f'ЕНДПОИНТ {i}')
    #     endpoint = i.split('%')[0]
    #     method = i.split('%')[1]
    #     # Запуск
    #     main(endpoint=endpoint, method=method.lower())
    #     # time.sleep(0.5)
    #     print('---------------------------')
    #     print('---------------------------')
    # # print('---------------------------')

    # make_preset(endpoint, method, operation)
