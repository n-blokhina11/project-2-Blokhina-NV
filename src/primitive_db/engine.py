import shlex

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

METADATA = 'db_meta.json'

def welcome():
    print('Первая попытка запустить проект!')
    print()
    print('***')
    print('<command> exit - выйти из программы')
    print('<command> help - справочная информация')


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def parse_column(col):
    """Корректное представление колонок
    ['name:str', 'age:int'] -> ([('name', 'str'), ('age', 'int')], None)"""

    columns = []
    for item in col:
        if ':' not in item:
            return None, f'Некорректное значение {item}, ожидается название:тип'

        name, col_type = item.split(':', 1)
        if not name:
            return None, 'Пустое имя столбца'
        columns.append((name, col_type))
    return columns, None


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

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f'Некорректное значение: {e}. Попробуйте снова.')
            continue

        command = args[0].lower()
        rest = args[1:]

        if command == 'exit':
            print('Выход')
            break

        if command == 'help':
            print_help()
            continue

        if command == 'create_table':
            if len(rest) < 2:
                print('Некорректное значение: ' \
                'создание таблицы требует название таблицы и колонок')
                continue
            table_name = rest[0]
            columns, error = parse_column(rest[1:])
            if error:
                print(f'{error}. Попробуйте снова.')
                continue

            metadata = load_metadata(METADATA)
            metadata, error = create_table(metadata, table_name, columns)
            if error:
                print(f'{error}. Попробуйте снова.')
                continue

            save_metadata(METADATA, metadata)
            created = metadata[table_name]['columns']
            cols_str = ', '.join(f'{n}:{t}' for n, t in created)

            print(f'Таблица {table_name} успешно создана со столбцами: {cols_str}')
            continue

        if command == 'drop_table':
            if len(rest) != 1:
                print('Ошибка: требуется 1 имя таблицы.')
                continue

            metadata = load_metadata(METADATA)
            metadata, error = drop_table(metadata, rest[0])

            if error:
                print(f'{error}. Попробуйте снова.')
                continue

            save_metadata(METADATA, metadata)
            print(f'Таблица {rest[0]} успешно удалена.')
            continue

        if command == 'list_tables':
            metadata = load_metadata(METADATA)
            table = list(metadata.keys())
            if not table:
                print('Список таблиц пуст.')
            else:
                for name in table:
                    print(f'- {name}')
            continue

        print(f'Функции {command} нет. Попробуйте снова.')

        


