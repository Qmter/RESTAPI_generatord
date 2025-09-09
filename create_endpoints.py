# create_endpoints.py
import json
import os

# Настройки
OPENAPI_FILE = "config/openapi.json"
OUTPUT_FILE = "endpoints_methods.txt"


def main():
    # Проверяем наличие файла
    if not os.path.exists(OPENAPI_FILE):
        print(f"Файл не найден: {OPENAPI_FILE}")
        return

    # Читаем OpenAPI
    with open(OPENAPI_FILE, "r", encoding="utf-8") as f:
        spec = json.load(f)

    # Открываем файл для записи
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        # Проходим по всем путям
        for endpoint, methods in spec.get("paths", {}).items():
            for method in methods.keys():
                # Записываем в формате: /endpoint%METHOD
                out_f.write(f"{endpoint}%{method.upper()}\n")

    print(f"Все эндпоинты сохранены в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
