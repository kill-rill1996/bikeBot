from typing import List


def is_valid_vehicle_number(number: str, serial_numbers: List[int]) -> bool:
    """Валидация номера велосипеда"""
    try:
        number = int(number)
    except Exception:
        return False

    # TODO поправить в соответствии с ТЗ
    if number not in serial_numbers:
        return False

    return True


def is_valid_duration(duration: str) -> bool:
    """Валидация времени работы"""
    try:
        duration = int(duration)
    except Exception:
        return False

    if duration < 5 or duration > 480:
        return False

    return True


def is_valid_tg_id(tg_id: str) -> bool:
    """Проверка правильности tg id"""
    try:
        tg_id = int(tg_id)
    except Exception:
        return False

    return True




