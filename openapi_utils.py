# openapi_utils.py

import os
import json
import jsonref
from jsf import JSF

def load_openapi_schema(openapi_path, endpoint=None, method=None, schema_ref_path=None):
    """
    Универсальная функция для загрузки и разворачивания JSON-схемы из OpenAPI.

    :param openapi_path: Путь к файлу openapi.json
    :param endpoint: Путь эндпоинта (например, '/interfaces/ethernet/capability')
    :param method: HTTP-метод (post, put, get и т.д.)
    :param schema_ref_path: Альтернативно — путь к схеме в формате:
                            "components.schemas.in_interfaces_ethernet_capability_write"
                            или "#/components/schemas/..."
    :return: Полностью развёрнутая схема (dict) или None
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

    # Схема может быть получена разными способами
    if schema_ref_path:
        # Поддержка двух форматов: dotted path или JSON Pointer
        if schema_ref_path.startswith("#/"):
            # Пример: "#/components/schemas/MySchema"
            parts = [part for part in schema_ref_path[2:].split("/") if part]
            current = resolved_spec
            try:
                for part in parts:
                    current = current[part]
                return current
            except KeyError as e:
                raise KeyError(f"Схема не найдена по пути: {schema_ref_path}") from e

        else:
            # Пример: "components.schemas.MySchema"
            parts = schema_ref_path.split(".")
            current = resolved_spec
            try:
                for part in parts:
                    current = current[part]
                return current
            except KeyError as e:
                raise KeyError(f"Схема не найдена по пути: {schema_ref_path}") from e

    elif endpoint and method:
        # Извлекаем схему из requestBody
        method = method.lower()
        if (
            "paths" not in resolved_spec or
            endpoint not in resolved_spec["paths"] or
            method not in resolved_spec["paths"][endpoint]
        ):
            raise KeyError(f"Эндпоинт или метод не найден: {endpoint} {method.upper()}")

        operation = resolved_spec["paths"][endpoint][method]

        if "requestBody" not in operation:
            print(f"{method.upper()} {endpoint} не имеет requestBody")
            return None

        content = operation["requestBody"].get("content", {})
        json_content = content.get("application/json") or content.get("*/*")
        if not json_content or "schema" not in json_content:
            raise KeyError(f"Нет схемы в requestBody для {endpoint}")

        return json_content["schema"]

    else:
        raise ValueError("Укажите либо (endpoint + method), либо schema_ref_path")


def generate_fake_data(schema, seed=None):
    """
    Генерирует фейковые данные по схеме с помощью JSF.
    :param schema: JSON-схема (уже без $ref)
    :param seed: Опциональное зеркало для воспроизводимости
    :return: Сгенерированные данные
    """
    if seed is not None:
        import random
        random.seed(seed)

    faker = JSF(schema)
    return faker.generate()