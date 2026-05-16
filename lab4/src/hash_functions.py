"""
Модуль с хеш-функциями для преобразования ключевых слов.
Реализует перевод ключа в числовое значение V и вычисление хеш-адреса h(V).
"""

from src.constants import (
    ALPHABET_SIZE,
    FIRST_LETTER_INDEX,
    SECOND_LETTER_INDEX,
    POSITIONAL_BASE,
)


class HashFunctions:
    """
    Класс, инкапсулирующий все хеш-функции.
    Следует принципу единственной ответственности (SRP).
    """

    _RUSSIAN_ALPHABET: str = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

    @classmethod
    def _get_letter_code(cls, letter: str) -> int:
        """
        Получение числового кода буквы (А=0, Б=1, ..., Я=32).
        """
        upper_letter = letter.upper()
        position = cls._RUSSIAN_ALPHABET.find(upper_letter)
        return position if position != -1 else 0

    @classmethod
    def compute_numeric_value(cls, key: str) -> int:
        """
        Перевод ключевого слова в числовое значение V.
        V = код1 * 33^1 + код2 * 33^0 (по первым двум буквам).
        """
        if len(key) < 2:
            return 0

        first_code = cls._get_letter_code(key[FIRST_LETTER_INDEX])
        second_code = cls._get_letter_code(key[SECOND_LETTER_INDEX])

        return first_code * POSITIONAL_BASE + second_code

    @classmethod
    def compute_hash_address(cls, numeric_value: int, table_size: int) -> int:
        """
        Преобразование числового значения V в хеш-адрес.
        h(V) = V mod H
        """
        return numeric_value % table_size