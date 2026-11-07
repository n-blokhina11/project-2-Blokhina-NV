def create_table(metadata, table_name, columns):
    """Создание таблицы
    create_table <имя_таблицы> <столбец1:тип> <столбец2:тип>"""

    valid_types = ["str", "int", "bool"]

    if table_name in metadata:
        return metadata, f"Ошибка: Таблица {table_name} уже существует."

    for col_name, col_type in columns:
        if col_type not in valid_types:
            return metadata, (
                f"Ошибка типа, недопустимый тип {col_type} для столбца {col_name}"
            )

    if any(name.lower() == "id" for name, _ in columns):
        all_columns = [list(c) for c in columns]
    else:
        all_columns = [["ID", "int"], *[list(c) for c in columns]]

    metadata[table_name] = {"columns": all_columns}
    return metadata, None


def drop_table(metadata, table_name):
    """Удаление таблицы"""

    if table_name not in metadata:
        return metadata, f"Ошибка: таблица {table_name} не существует"

    del metadata[table_name]
    return metadata, None


def coerce(val, col_type):
    """Приведение значения к типу столбца"""
    if col_type == "int":
        return int(val)
    if col_type == "bool":
        if isinstance(val, bool):
            return val
        return str(val).strip().lower() in ("true", "1", "yes", "t", "y")
    return str(val).strip()


def insert(metadata, table_name, values, table_data):
    """Вставка значений в таблицу"""

    if table_name not in metadata:
        return None, f"Ошибка: таблица {table_name} не существует"

    columns = metadata[table_name]["columns"]
    exp_cols = columns[1:]

    if len(values) != len(exp_cols):
        err = f"Ошибка: ожидалось {len(exp_cols)} значений, передано {len(values)}"
        return table_data, err

    row = {}
    for (col_name, col_type), val in zip(exp_cols, values):
        try:
            row[col_name] = coerce(val, col_type)
        except (ValueError, TypeError):
            return None, f"Некорректное значение {val} для столбца {col_name}"

    new_id = max((int(r["ID"]) for r in table_data), default=0) + 1
    order_row = {"ID": new_id, **row}
    table_data.append(order_row)

    return table_data, None


def select(table_data, where_clause=None):
    if not where_clause:
        return table_data
    else:
        return [
            row
            for row in table_data
            if all(row.get(k) == v for k, v in where_clause.items())
        ]


def update(table_data, set_clause, where_clause):
    if not where_clause:
        return table_data, []

    aff = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            for k, v in set_clause.items():
                row[k] = v
            aff.append(row["ID"])
    return table_data, aff


def delete(table_data, where_clause):
    if not where_clause:
        return table_data, []

    deleted = []
    new_data = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            deleted.append(row["ID"])
        else:
            new_data.append(row)
    return new_data, deleted
