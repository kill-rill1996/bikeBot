def is_valid_vehicle_number(number) -> bool:
    """Валидация номера велосипеда"""
    try:
        number = int(number)
    except Exception:
        return False

    # TODO поправить в соответствии с ТЗ
    if number < 1 or number > 100:
        return False

    return True
