## Управление таблицами

### Установка

```bash
pip install primitive-db
```

### Запуск

```bash
database
```

### Команды

| Команда | Описание |
|---|---|
| `create_table <имя> <столбец:тип> ...` | Создать таблицу. `ID:int` добавляется автоматически, если не указан. |
| `list_tables` | Показать список всех таблиц. |
| `drop_table <имя>` | Удалить таблицу. |
| `help` | Справка. |
| `exit` | Выход. |

Поддерживаемые типы: `int`, `str`, `bool`.

### Пример

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```