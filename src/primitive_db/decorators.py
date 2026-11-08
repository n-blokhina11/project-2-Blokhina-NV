import functools
import time


def handle_db_errors(func):
    """Перехват ошибок KeyError, ValueError и FileNotFoundError"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print('Ошибка: файл в данных не найден')
        except KeyError as e:
            print(f'Ошибка: таблица или столбец {e} не найден')
        except ValueError as e:
            print(f'Ошибка валидации: {e}')
        except Exception as e:
            print(f'Непредвиденная ошибка {e}')

    return wrapper

def confirm_action(action_name):
    """Запрос у пользователя подтверждения для опасных операций"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = input('Вы уверены, что хотите выполнить ' \
            f'операцию "{action_name}"? [y/n]: ').strip().lower()
            if answer != 'y':
                print('Отмена')
                return None
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def log_time(func):
    """Замер времени выполнения операции"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start
        print(f'Функция {func.__name__} выполнилась за {duration:.3f} секунд')
        return result
    
    return wrapper

def create_cacher():
    """Возвращение функции cache_result(key, value_func) с кэшем в замыкании"""

    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        value = value_func()
        cache[key] = value
        return value
    return cache_result




    