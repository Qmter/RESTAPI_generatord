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
        lazy_load=True
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
            raise KeyError(
                f"Эндпоинт или метод не найден: {endpoint} {method.upper()}")

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
            raise KeyError(
                f"Нет параметров или requestBody для {endpoint} {method.upper()}")

    else:
        raise ValueError(
            "Укажите либо (endpoint + method), либо schema_ref_path")


def generate_fake_data(schema, available_interfaces, seed=None):
    """
    Генерирует фейковые данные и исправляет boolean и const.
    """
    if seed is not None:
        random.seed(seed)

    faker = JSF(schema)
    fake_data = faker.generate()

    # Заменяем ifname на реальный из списка
    if 'ifname' in fake_data and len(available_interfaces) != 0:
        fake_data['ifname'] = random.choice(available_interfaces)

    # Рекурсивно исправляем 1 → True, 0 → False
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


def generate_fake_data_add(schema, available_interfaces, seed=None):
    """
    Генерирует фейковые данные для добавления интерфейсов c предварительной проверкой существования интерфейса.
    """
    if seed is not None:
        random.seed(seed)

    faker = JSF(schema)
    fake_data = faker.generate()

    # Заменяем ifname если такой уже существует
    if 'ifname' in fake_data:
        while fake_data['ifname'] in available_interfaces:
            fake_data = faker.generate()

    return fake_data


def generate_fake_data_delete(schema, available_interfaces, seed=None):
    """
    Генерирует фейковые данные для удаления интерфейсов c предварительной проверкой существования интерфейса.
    """
    if seed is not None:
        random.seed(seed)

    faker = JSF(schema)
    fake_data = faker.generate()

    # Заменяем ifname если такой уже существует
    if 'ifname' in fake_data:
        while fake_data['ifname'] in available_interfaces:
            fake_data = faker.generate()

    return fake_data
