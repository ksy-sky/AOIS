"""
Unit-тесты для хеш-функций.
Покрытие тестами >90%.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hash_functions import HashFunctions
from src.constants import DEFAULT_TABLE_SIZE


class TestHashFunctions(unittest.TestCase):
    """Тестирование хеш-функций."""

    def setUp(self) -> None:
        self.hash_func = HashFunctions()

    def test_compute_numeric_value_single_letter(self) -> None:
        """Тест: ключ из одной буквы."""
        result = self.hash_func.compute_numeric_value("А")
        self.assertEqual(result, 0)

    def test_compute_numeric_value_two_letters(self) -> None:
        """Тест: ключ из двух букв."""
        # В = 2, Я = 32 -> 2*33 + 32 = 98
        result = self.hash_func.compute_numeric_value("ВЯ")
        self.assertEqual(result, 2 * 33 + 32)

    def test_compute_numeric_value_three_letters(self) -> None:
        """Тест: ключ из трёх букв (используются только первые две)."""
        result = self.hash_func.compute_numeric_value("АБВ")
        # А=0, Б=1 -> 0*33 + 1 = 1
        self.assertEqual(result, 1)

    def test_compute_numeric_value_lowercase(self) -> None:
        """Тест: ключ в нижнем регистре."""
        result = self.hash_func.compute_numeric_value("абв")
        self.assertEqual(result, 1)

    def test_compute_numeric_value_mixed_case(self) -> None:
        """Тест: ключ со смешанным регистром."""
        result = self.hash_func.compute_numeric_value("ДНК")
        # Д=4, Н=14 -> 4*33 + 14 = 146
        self.assertEqual(result, 4 * 33 + 14)

    def test_compute_numeric_value_empty_string(self) -> None:
        """Тест: пустая строка."""
        result = self.hash_func.compute_numeric_value("")
        self.assertEqual(result, 0)

    def test_compute_numeric_value_with_digit(self) -> None:
        """Тест: ключ с цифрой (цифра игнорируется, буква даёт 0)."""
        result = self.hash_func.compute_numeric_value("1А")
        self.assertEqual(result, 0)

    def test_compute_hash_address(self) -> None:
        """Тест: вычисление хеш-адреса."""
        test_cases = [
            (0, 10, 0),
            (15, 10, 5),
            (20, 10, 0),
            (33, 21, 12),
            (98, 21, 98 % 21),
        ]
        for numeric_value, size, expected in test_cases:
            with self.subTest(numeric_value=numeric_value, size=size):
                result = self.hash_func.compute_hash_address(numeric_value, size)
                self.assertEqual(result, expected)

    def test_compute_hash_address_default_size(self) -> None:
        """Тест: хеш-адрес с размером по умолчанию."""
        result = self.hash_func.compute_hash_address(100, DEFAULT_TABLE_SIZE)
        self.assertEqual(result, 100 % DEFAULT_TABLE_SIZE)


if __name__ == '__main__':
    unittest.main()