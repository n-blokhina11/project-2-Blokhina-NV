import json
import os


def load_metadata(filepath):
    """Загрузка данных из JSON,
    если файл не найден - возвращает пустой словарь"""

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    return data if isinstance(data, dict) else {}


def save_metadata(filepath, data):
    """Сохранение данных в JSON-файл"""

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_table_data(table_name):
    """Загрузка таблиц"""

    filepath = os.path.join("data", f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохранение таблиц в каталоге data"""

    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
