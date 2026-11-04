def create_table(metadata, table_name, columns):
    """Создание таблицы
    create_table <имя_таблицы> <столбец1:тип> <столбец2:тип>"""

    valid_types = ['str', 'int', 'bool']

    if table_name in metadata:
        return metadata, f'Ошибка: Таблица {table_name} уже существует.'

    for col_name, col_type in columns:
        if col_type not in valid_types:
            return metadata, (f'Ошибка типа, недопустимый тип {col_type} '
                              f'для столбца {col_name}')

    if any(name.lower() == 'id' for name, _ in columns):
        all_columns = [list(c) for c in columns]
    else:
        all_columns = [['ID', 'int'], *[list(c) for c in columns]]

    metadata[table_name] = {'columns':all_columns}
    return metadata, None

def drop_table(metadata, table_name):
    """Удаление таблицы"""

    if table_name not in metadata:
        return metadata, f'Ошибка: таблица {table_name} не существует'

    del metadata[table_name]
    return metadata, None

