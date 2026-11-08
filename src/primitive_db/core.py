from primitive_db.decorators import confirm_action, handle_db_errors, log_time


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создание таблицы
    create_table <имя_таблицы> <столбец1:тип> <столбец2:тип>"""

    valid_types = ["str", "int", "bool"]

    if table_name in metadata:
        raise ValueError(f"Таблица {table_name} уже существует.")

    for col_name, col_type in columns:
        if col_type not in valid_types:
            raise ValueError(
                f"Ошибка типа, недопустимый тип {col_type} для столбца {col_name}"
            )

    if any(name.lower() == "id" for name, _ in columns):
        all_columns = [list(c) for c in columns]
    else:
        all_columns = [["ID", "int"], *[list(c) for c in columns]]

    metadata[table_name] = {"columns": all_columns}
    return metadata

@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Удаление таблицы"""

    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не существует")

    del metadata[table_name]
    return metadata


def coerce(val, col_type):
    """Приведение значения к типу столбца"""
    if col_type == "int":
        return int(val)
    if col_type == "bool":
        if isinstance(val, bool):
            return val
        return str(val).strip().lower() in ("true", "1", "yes", "t", "y")
    return str(val).strip()

@log_time
@handle_db_errors
def insert(metadata, table_name, values, table_data):
    """Вставка значений в таблицу"""

    if table_name not in metadata:
        raise KeyError(f"Ошибка: таблица {table_name} не существует")

    columns = metadata[table_name]["columns"]
    exp_cols = columns[1:]

    if len(values) != len(exp_cols):
        raise ValueError(
            f"Ошибка: ожидалось {len(exp_cols)} значений, передано {len(values)}"
            )

    row = {}
    for (col_name, col_type), val in zip(exp_cols, values):
        row[col_name] = coerce(val, col_type)

    new_id = max((int(r["ID"]) for r in table_data), default=0) + 1
    order_row = {"ID": new_id, **row}
    table_data.append(order_row)

    return table_data

@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    if not where_clause:
        return table_data
    else:
        return [
            row
            for row in table_data
            if all(row.get(k) == v for k, v in where_clause.items())
        ]

@handle_db_errors
def update(table_data, set_clause, where_clause):
    if not where_clause:
        raise ValueError('Не задано условие обновления')

    affected = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            for k, v in set_clause.items():
                row[k] = v
            affected.append(row["ID"])
    return table_data, affected

@confirm_action("удаление записей")
def delete(table_data, where_clause):
    if not where_clause:
        raise ValueError('Не задано условие удаления')

    return [
        row for row in table_data
        if not all(row.get(k) == v for k, v in where_clause.items())
    ]
