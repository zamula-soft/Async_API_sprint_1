from functools import wraps
from loguru import logger
import time

def backoff(start_sleep_time: object = 0.1, factor: object = 2, border_sleep_time: object = 10) -> object:
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            n = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error('Ошибка при выполнении функции: {}'.format(func.__name__), e)
                    if t >= border_sleep_time:
                        t = border_sleep_time
                    else:
                        t = start_sleep_time * 2 ^ (n)
                        n += factor
                    time.sleep(t)
        return inner
    return func_wrapper

