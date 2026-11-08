import os
import re
import shlex

from prettytable import PrettyTable

from primitive_db.core import (
    coerce,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA = "db_meta.json"


def welcome():
    print("Первая попытка запустить проект!")
    print()
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print()
    print("***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя> values (<v1>, <v2>, ...) - создать запись")
    print("<command> select from <имя> - прочитать все записи")
    print(
        "<command> select from <имя> where <столбец> = <значение> "
        "- прочитать по условию"
    )
    print(
        "<command> update <имя> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить"
    )
    print("<command> delete from <имя> where <столбец> = <значение> - удалить")
    print("<command> info <имя> - информация о таблице")
    print()
    print("Общие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_column(col):
    """Корректное представление колонок
    ['name:str', 'age:int'] -> ([('name', 'str'), ('age', 'int')], None)"""

    columns = []
    for item in col:
        if ":" not in item:
            return None, f"Некорректное значение {item}, ожидается название:тип"

        name, col_type = item.split(":", 1)
        if not name:
            return None, "Пустое имя столбца"
        columns.append((name, col_type))
    return columns, None


def parse_insert_values(raw):
    """'\"Sergei\", 28, true' -> ['Sergei', '28', 'true']."""
    tokens = re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\s]+)', raw)
    values = []
    for dq, sq, unq in tokens:
        if dq:
            values.append(dq)
        elif sq:
            values.append(sq)
        else:
            values.append(unq)
    return values


def parser_where(args, columns):
    """Превращение строки вида ['age', '=', '28'] или ['age=28']
    в {'age': 28}"""

    if len(args) == 1 and "=" in args[0]:
        left, right = args[0].split("=", 1)
        args = [left, "=", right]

    if len(args) != 3 or args[1] != "=":
        return None, "Ошибка: ожидалось <столбец> = <значение>"

    col, _, var = args
    actual_name = None
    actual_type = None
    for col_name, col_type in columns:
        if col_name.lower() == col.lower():
            actual_name = col_name
            actual_type = col_type
            break

    if actual_name is None:
        return None, f"Столбец {col} не существует"

    try:
        value = coerce(var, actual_type)
    except (ValueError, TypeError):
        return None, f"Некорректное значение {var} для столбца {actual_name}"

    return {actual_name: value}, None


def print_table(table_data, columns):
    if not table_data:
        return "Нет данных"
    pt = PrettyTable()
    pt.field_names = [name for name, _ in columns]
    for row in table_data:
        pt.add_row([row.get(name) for name, _ in columns])
    print(pt)


def run():
    """Основная функция"""

    print_help()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        match = re.match(
            r"^insert\s+into\s+(\S+)\s+values\s*\((.+)\)\s*$",
            user_input,
            re.IGNORECASE,
        )
        if match:
            table_name = match.group(1)
            raw_values = match.group(2)

            metadata = load_metadata(METADATA)
            if table_name not in metadata:
                print(f'Таблица "{table_name}" не существует. Попробуйте снова.')
                continue

            values = parse_insert_values(raw_values)
            table_data = load_table_data(table_name)

            new_data = insert(metadata, table_name, values, table_data)
            if new_data is None:
                continue

            save_table_data(table_name, new_data)
            new_id = new_data[-1]["ID"]
            print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Некорректное значение: {e}. Попробуйте снова.")
            continue

        command = args[0].lower()
        rest = args[1:]

        if command == "exit":
            print("Выход")
            break

        if command == "help":
            print_help()
            continue

        if command == "create_table":
            if len(rest) < 2:
                print(
                    "Некорректное значение: "
                    "создание таблицы требует название таблицы и колонок"
                )
                continue
            table_name = rest[0]
            columns, error = parse_column(rest[1:])
            if error:
                print(f"{error}. Попробуйте снова.")
                continue

            metadata = load_metadata(METADATA)
            metadata = create_table(metadata, table_name, columns)
            if metadata is None:
                continue

            save_metadata(METADATA, metadata)
            created = metadata[table_name]["columns"]
            cols_str = ", ".join(f"{n}:{t}" for n, t in created)

            print(f"Таблица {table_name} успешно создана со столбцами: {cols_str}")
            continue

        if command == "drop_table":
            if len(rest) != 1:
                print("Ошибка: требуется 1 имя таблицы.")
                continue

            metadata = load_metadata(METADATA)
            metadata = drop_table(metadata, rest[0])
            if metadata is None:
                continue

            save_metadata(METADATA, metadata)
            data_file = os.path.join("data", f"{rest[0]}.json")
            if os.path.exists(data_file):
                os.remove(data_file)

            print(f"Таблица {rest[0]} успешно удалена.")
            continue

        if command == "list_tables":
            metadata = load_metadata(METADATA)
            table = list(metadata.keys())
            if not table:
                print("Список таблиц пуст.")
            else:
                for name in table:
                    print(f"- {name}")
            continue

        if command == "select":
            if not rest or rest[0].lower() != "from":
                print("Ошибка. Используйте select from <таблица> [where...]")
                continue
            if len(rest) < 2:
                print("Ошибка, требуется имя таблицы")
                continue

            table_name = rest[1]
            metadata = load_metadata(METADATA)
            if rest[1] not in metadata:
                print(f'Таблица "{table_name}" не существует. Попробуйте снова.')
                continue

            columns = metadata[table_name]["columns"]
            where_clause = None
            if len(rest) > 2:
                if rest[2].lower() != "where":
                    print("Ошибка: ожидается where")
                    continue
                where_clause, error = parser_where(rest[3:], columns)
                if error:
                    print(f"{error}. Попробуйте снова.")
                    continue

            table_data = load_table_data(table_name)
            result = select(table_data, where_clause)
            if result is None:
                continue

            print_table(result, columns)
            continue

        if command == "update":
            if len(rest) < 4 or rest[1].lower() != "set":
                print(
                    "Некорректное значение: используйте "
                    "update <таблица> set ... where ... Попробуйте снова."
                )
                continue

            table_name = rest[0]
            metadata = load_metadata(METADATA)
            if table_name not in metadata:
                print(f'Таблица "{table_name}" не существует. Попробуйте снова.')
                continue

            columns = metadata[table_name]["columns"]
            where_idx = next(
                (i for i, a in enumerate(rest) if a.lower() == "where"),
                None,
            )
            if where_idx is None:
                print("Некорректное значение: update требует where. Попробуйте снова.")
                continue

            set_clause, error = parser_where(rest[2:where_idx], columns)
            if error:
                print(f"{error}. Попробуйте снова.")
                continue

            where_clause, error = parser_where(rest[where_idx + 1 :], columns)
            if error:
                print(f"{error}. Попробуйте снова.")
                continue

            table_data = load_table_data(table_name)
            new_data, affected = update(table_data, set_clause, where_clause)
            if new_data is None:
                continue
            if not affected:
                print("Нет записей для обновления.")
                continue

            save_table_data(table_name, new_data)
            for rid in affected:
                print(f'Запись с ID={rid} в таблице "{table_name}" успешно обновлена.')
            continue

        if command == "delete":
            if len(rest) < 4 or rest[0].lower() != "from" or rest[2].lower() != "where":
                print(
                    "Некорректное значение: используйте "
                    "delete from <таблица> where ... Попробуйте снова."
                )
                continue

            table_name = rest[1]
            metadata = load_metadata(METADATA)
            if table_name not in metadata:
                print(f'Таблица "{table_name}" не существует. Попробуйте снова.')
                continue

            columns = metadata[table_name]["columns"]
            where_clause, error = parser_where(rest[3:], columns)
            if error:
                print(f"{error}. Попробуйте снова.")
                continue

            table_data = load_table_data(table_name)
            deleted_ids = [
                row["ID"]
                for row in table_data
                if all(row.get(k) == v for k, v in where_clause.items())
                ]
            new_data = delete(table_data, where_clause)
            if new_data is None:
                continue

            if not deleted_ids:
                print("Нет записей для удаления.")
                continue

            save_table_data(table_name, new_data)
            for rid in deleted_ids:
                print(f'Запись с ID={rid} успешно удалена из таблицы "{table_name}".')
            continue

        if command == "info":
            if len(rest) != 1:
                print(
                    "Некорректное значение: info требует имя таблицы. Попробуйте снова."
                )
                continue

            table_name = rest[0]
            metadata = load_metadata(METADATA)
            if table_name not in metadata:
                print(f'Таблица "{table_name}" не существует. Попробуйте снова.')
                continue

            columns = metadata[table_name]["columns"]
            table_data = load_table_data(table_name)
            cols_str = ", ".join(f"{n}:{t}" for n, t in columns)
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {cols_str}")
            print(f"Количество записей: {len(table_data)}")
            continue

        if command == "insert":
            print(
                'Некорректное значение: используйте "insert into <таблица> '
                'values (значение1, значение2, ...)". Попробуйте снова.'
            )
            continue

        print(f"Функции {command} нет. Попробуйте снова.")
