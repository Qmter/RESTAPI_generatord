# openapi_utils.py

import os
import json
import jsonref
import requests_tests
import random
from jsf import JSF


def load_openapi_schema(openapi_path, endpoint=None, method=None, schema_ref_path=None):
    """
    Универсальная функция для загрузки и разворачивания JSON-схемы из OpenAPI.
    """
    if not os.path.exists(openapi_path):
        raise FileNotFoundError(f"OpenAPI файл не найден: {openapi_path}")

    with open(openapi_path, "r", encoding="utf-8") as f:

        spec = json.load(f)

    # Полностью разворачиваем все $ref
    resolved_spec = jsonref.replace_refs(
        spec,
        base_uri=f"file://{os.path.abspath(openapi_path)}",
        lazy_load=False
    )

    if schema_ref_path:
        # Обработка прямого пути к схеме
        if schema_ref_path.startswith("#/"):
            parts = [part for part in schema_ref_path[2:].split("/") if part]
            current = resolved_spec
            try:
                for part in parts:
                    current = current[part]
                return current
            except KeyError as e:
                raise KeyError(
                    f"Схема не найдена по пути: {schema_ref_path}") from e

        else:
            parts = schema_ref_path.split(".")
            current = resolved_spec
            try:
                for part in parts:
                    current = current[part]
                return current
            except KeyError as e:
                raise KeyError(
                    f"Схема не найдена по пути: {schema_ref_path}") from e

    elif endpoint and method:
        method = method.lower()
        if ("paths" not in resolved_spec or
                    endpoint not in resolved_spec["paths"] or
                    method not in resolved_spec["paths"][endpoint]
                ):
            print(f"Эндпоинт или метод не найден: {endpoint} {method.upper()}")
            return {}

        operation = resolved_spec["paths"][endpoint][method]

        if "requestBody" in operation:
            # POST, PUT и другие методы с requestBody
            content = operation["requestBody"].get("content", {})
            json_content = content.get(
                "application/json") or content.get("*/*")
            if not json_content or "schema" not in json_content:
                raise KeyError(f"Нет схемы в requestBody для {endpoint}")
            return json_content["schema"]

        elif "parameters" in operation:
            # GET и другие методы с параметрами
            parameters = operation["parameters"]
            schema = {
                "type": "object",
                "properties": {},
                "required": []
            }

            for param in parameters:
                param_name = param["name"]
                param_in = param.get("in", "query")
                param_required = param.get("required", False)
                param_schema = param.get("schema", {})

                if param_in == "query":
                    schema["properties"][param_name] = param_schema
                    if param_required:
                        schema["required"].append(param_name)

            return schema

        else:
            print(
                f"Нет параметров или requestBody для {endpoint} {method.upper()}")
            return {}

    else:
        raise ValueError(
            "Укажите либо (endpoint + method), либо schema_ref_path")


def preprocess_schema_for_jsf(schema):
    """
    Рекурсивно заменяет oneOf на первый подходящий элемент.
    """
    if isinstance(schema, dict):
        if 'oneOf' in schema:
            # Выбираем первый элемент, который НЕ является const или примитивом
            for option in schema['oneOf']:
                if isinstance(option, dict) and 'type' in option:
                    return preprocess_schema_for_jsf(option)
            # Если нет подходящего — берём первый
            return preprocess_schema_for_jsf(schema['oneOf'][0])

        # Рекурсивно обрабатываем остальные поля
        return {k: preprocess_schema_for_jsf(v) for k, v in schema.items()}

    elif isinstance(schema, list):
        return [preprocess_schema_for_jsf(item) for item in schema]

    else:
        return schema


def generate_fake_data_interfaces(schema, available_interfaces, seed=None):
    if seed is not None:
        random.seed(seed)

    try:
        faker = JSF(schema)
        fake_data = faker.generate()
    except Exception as e:
        print(f"JSF failed in generate_fake_data_interfaces: {e}")
        return {}

    # Проверка типа
    if not isinstance(fake_data, dict):
        return fake_data

    if 'ifname' in fake_data and available_interfaces:
        fake_data['ifname'] = random.choice(available_interfaces)

    def fix_bools(obj):
        if isinstance(obj, dict):
            return {k: fix_bools(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [fix_bools(item) for item in obj]
        elif obj == 1:
            return True
        elif obj == 0:
            return False
        else:
            return obj

    return fix_bools(fake_data)


def generate_fake_data(schema):
    try:
        faker = JSF(schema)
        fake_data = faker.generate()

        def fix_bools(obj):
            if isinstance(obj, dict):
                return {k: fix_bools(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_bools(item) for item in obj]
            elif obj == 1:
                return True
            elif obj == 0:
                return False
            else:
                return obj

        return fix_bools(fake_data)

    except Exception as e:
        print(f"JSF failed: {e}. Using fallback.")
        # Fallback: ручная генерация по ключам
        result = {}
        props = schema.get("properties", {})
        for key, prop in props.items():
            if prop.get("type") == "string":
                result[key] = f"fake_{key}"
            elif prop.get("type") == "integer":
                result[key] = 123
            elif prop.get("type") == "boolean":
                result[key] = True
            elif prop.get("type") == "null" or prop.get("type") is None:
                result[key] = None
            else:
                result[key] = None
        return result


def generate_fake_data_add(schema, available_interfaces, seed=None):
    """
    Генерирует фейковые данные для добавления интерфейсов.
    Проверяет, что сгенерированные данные — это словарь, и что ifname не дублируется.
    """
    if seed is not None:
        random.seed(seed)

    faker = JSF(schema)
    fake_data = faker.generate()

    # Защита: если схема возвращает не dict — возвращаем как есть
    if not isinstance(fake_data, dict):
        return fake_data
    #
    # Проверяем наличие ifname и перегенерируем, если он уже существует
    if 'ifname' in fake_data and available_interfaces:
        while fake_data.get('ifname') in available_interfaces:
            fake_data = faker.generate()
            # Снова проверяем тип после перегенерации
            if not isinstance(fake_data, dict):
                return fake_data

    return fake_data


def generate_fake_data_delete(schema, available_interfaces, seed=None):
    """
    Генерирует фейковые данные для удаления интерфейсов.
    """
    if seed is not None:
        random.seed(seed)

    faker = JSF(schema)
    fake_data = faker.generate()

    if not isinstance(fake_data, dict):
        return fake_data

    if 'ifname' in fake_data and available_interfaces:
        while fake_data.get('ifname') in available_interfaces:
            fake_data = faker.generate()
            if not isinstance(fake_data, dict):
                return fake_data

    return fake_data
