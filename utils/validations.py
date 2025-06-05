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


def from_transport_list_to_srt(transports: list[int]) -> str:
    """Из списка сортированного serial_number транспортов формирует строку для вывода"""
    string_result = ""
    max_index = len(transports) - 1
    end_num = 0

    index = 0
    for serial_number in transports:
        if index >= max_index:
            break

        # добавляем первое число
        if index == 0:
            string_result += string_result + f"{serial_number}"
            # проверяем совпадение со след. числом
            if serial_number == transports[index+1]:
                end_num = transports[index+1]

        # отрабатываем обычные числа (не первые) если совпали
        if serial_number == transports[index + 1]:
            end_num = transports[index + 1]

        # отрабатываем обычные числа
        else:
            # если не было совпашвих совпали
            if end_num != 0:
                string_result += f"-{end_num}"
                string_result += f" {serial_number}"
                end_num = serial_number
            # если не были совпашвие
            else:
                string_result += f" {serial_number}"

        index += 1

    print(string_result)


if __name__ == "__main__":
    from_transport_list_to_srt([1, 3, 4, 5, 6, 103, 112])

