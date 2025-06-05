from typing import List


def is_valid_vehicle_number(number: str, serial_numbers: List[int]) -> bool:
    """Валидация номера велосипеда"""
    try:
        number = int(number)
    except Exception:
        return False

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


def parse_input_transport_numbers(text: str) -> [int]:
    """
    Парсинг введенных номеров транспорта при массовом добавлении
    Пример строки: 1-100, 101, 103, 105
    """
    duplicate_result = []
    try:
        # проверяем на введенные запятые
        if "," in text.strip():
            text_numbers = [num.strip() for num in text.split(",")]   # ["U1-U100", "U1", "U3", "U5"]
            for words in text_numbers:
                if "-" in words:
                    words_split = words.split("-")  # ["1, 100"]
                    duplicate_result.extend(range(int(words_split[0]), int(words_split[1]) + 1))
                else:
                    duplicate_result.append(int(words))
        elif "-" in text:
            words_split = text.split("-")  # ["1, 100"]
            duplicate_result.extend(range(int(words_split[0]), int(words_split[1]) + 1))

        else:
            duplicate_result.append(int(text))
    except Exception as e:
        raise e

    # remove duplicates
    result = []
    for num in duplicate_result:
        if not num in result:
            result.append(num)

    # make order
    result.sort()

    return result


def transport_list_to_str(transports: list[int]) -> str:
    """Из списка сортированного serial_number транспортов формирует строку для вывода"""
    result = []
    expected_n = 1
    sub_result = []

    for n in transports:
        # если диапазон пустой
        if not sub_result:
            sub_result.append(str(n))
            expected_n = n + 1

        # если диапазон начат
        else:
            # если ожидаемое значение равно поступившему
            if expected_n == n:
                # добавляем в диапазон
                sub_result.append(n)
                expected_n += 1

            # если ожидаемое значение не равно поступившему
            else:
                # добавляем диапазон в результат
                if len(sub_result) < 3:
                    # добавляем числа отдельно
                    for number in sub_result:
                        result.append(str(number))
                else:
                    # добавляем числа через -
                    result.append(f"{sub_result[0]}-{sub_result[-1]}")

                # начинаем диапазон заново
                sub_result = [n]
                expected_n = n + 1

    # отрабатываем последнее число
    if len(sub_result) < 3:
        # добавляем числа отдельно
        for number in sub_result:
            result.append(str(number))
    else:
        # добавляем числа через -
        result.append(f"{sub_result[0]}-{sub_result[-1]}")

    return ", ".join(result)


if __name__ == "__main__":
    print(transport_list_to_str([1, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 103, 112, 113, 114]))
    # from_transport_list_to_srt([1, 3, 4, 5, 6, 103, 112])

