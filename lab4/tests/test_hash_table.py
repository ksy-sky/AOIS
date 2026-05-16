"""
Unit-тесты для хеш-таблицы с КВАДРАТИЧНЫМ ПРОБИРОВАНИЕМ.
Покрытие тестами >90%.
Вариант 4 по заданию.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hash_table import HashTable, HashTableRow
from src.constants import DEFAULT_TABLE_SIZE


class TestHashTableRow(unittest.TestCase):
    """Тестирование структуры строки хеш-таблицы."""

    def test_row_initialization(self) -> None:
        """Тест: инициализация строки."""
        row = HashTableRow()
        self.assertEqual(row.id, "")
        self.assertFalse(row.c)
        self.assertFalse(row.u)
        self.assertTrue(row.t)
        self.assertFalse(row.l)
        self.assertFalse(row.d)
        self.assertEqual(row.po, -1)
        self.assertEqual(row.pi, "")

    def test_is_active(self) -> None:
        """Тест: проверка активности ячейки."""
        row = HashTableRow()
        row.u = True
        row.d = False
        self.assertTrue(row.is_active())

        row.d = True
        self.assertFalse(row.is_active())

        row.u = False
        row.d = False
        self.assertFalse(row.is_active())

    def test_is_available_for_insert(self) -> None:
        """Тест: доступность для вставки."""
        row = HashTableRow()
        row.u = False
        row.d = False
        self.assertTrue(row.is_available_for_insert())

        row.u = True
        row.d = True
        self.assertTrue(row.is_available_for_insert())

        row.u = True
        row.d = False
        self.assertFalse(row.is_available_for_insert())

    def test_is_never_occupied(self) -> None:
        """Тест: ячейка никогда не была занята."""
        row = HashTableRow()
        row.u = False
        self.assertTrue(row.is_never_occupied())

        row.u = True
        self.assertFalse(row.is_never_occupied())

    def test_to_dict(self) -> None:
        """Тест: преобразование в словарь."""
        row = HashTableRow()
        row.id = "Тест"
        row.c = True
        row.u = True
        row.t = True
        row.d = False
        row.pi = "Данные"

        data = row.to_dict()
        self.assertEqual(data["id"], "Тест")
        self.assertTrue(data["c"])
        self.assertTrue(data["u"])
        self.assertTrue(data["t"])
        self.assertEqual(data["pi"], "Данные")


class TestHashTableQuadraticProbing(unittest.TestCase):
    """Тестирование хеш-таблицы с квадратичным пробированием."""

    def setUp(self) -> None:
        self.table = HashTable(DEFAULT_TABLE_SIZE)

    def test_initialization(self) -> None:
        """Тест: корректная инициализация."""
        self.assertEqual(len(self.table._table), DEFAULT_TABLE_SIZE)
        self.assertEqual(self.table._record_count, 0)
        self.assertEqual(self.table.get_fill_factor(), 0.0)

    def test_insert_single_record(self) -> None:
        """Тест: вставка одной записи."""
        result = self.table.insert("Амеба", "Простейшее")
        self.assertTrue(result)
        self.assertEqual(self.table._record_count, 1)

    def test_search_found(self) -> None:
        """Тест: поиск существующей записи."""
        self.table.insert("Бактерия", "Микроорганизм")
        result = self.table.search("Бактерия")
        self.assertEqual(result, "Микроорганизм")

    def test_search_not_found(self) -> None:
        """Тест: поиск несуществующей записи."""
        result = self.table.search("НесуществующийКлюч")
        self.assertIsNone(result)

    def test_update_existing(self) -> None:
        """Тест: обновление существующей записи."""
        self.table.insert("Вирус", "Старое описание")
        result = self.table.update("Вирус", "Новое описание")
        self.assertTrue(result)
        self.assertEqual(self.table.search("Вирус"), "Новое описание")

    def test_update_not_existing(self) -> None:
        """Тест: обновление несуществующей записи."""
        result = self.table.update("НетТакого", "Данные")
        self.assertFalse(result)

    def test_delete_existing(self) -> None:
        """Тест: удаление существующей записи."""
        self.table.insert("ДНК", "Генетический материал")
        self.assertEqual(self.table._record_count, 1)
        result = self.table.delete("ДНК")
        self.assertTrue(result)
        self.assertEqual(self.table._record_count, 0)
        self.assertIsNone(self.table.search("ДНК"))

    def test_delete_not_existing(self) -> None:
        """Тест: удаление несуществующей записи."""
        result = self.table.delete("НетТакого")
        self.assertFalse(result)

    def test_insert_duplicate(self) -> None:
        """Тест: вставка дубликата (должна блокироваться)."""
        self.table.insert("Рибосома", "Первый раз")
        result = self.table.insert("Рибосома", "Второй раз")
        self.assertFalse(result)
        self.assertEqual(self.table._record_count, 1)

    def test_get_fill_factor(self) -> None:
        """Тест: коэффициент заполнения."""
        self.assertAlmostEqual(self.table.get_fill_factor(), 0.0)
        self.table.insert("Тест1", "Данные1")
        expected = 1.0 / DEFAULT_TABLE_SIZE
        self.assertAlmostEqual(self.table.get_fill_factor(), expected, places=5)

    def test_get_all_records(self) -> None:
        """Тест: получение всех записей."""
        self.table.insert("Ключ1", "Значение1")
        self.table.insert("Ключ2", "Значение2")
        records = self.table.get_all_records()
        self.assertEqual(len(records), 2)

        keys = [r["id"] for r in records]
        self.assertIn("Ключ1", keys)
        self.assertIn("Ключ2", keys)

    def test_get_row_at_index(self) -> None:
        """Тест: получение строки по индексу."""
        self.table.insert("ИндексТест", "Данные")

        found_index = None
        for idx in range(self.table._size):
            row = self.table.get_row_at_index(idx)
            if row and row["id"] == "ИндексТест":
                found_index = idx
                break

        self.assertIsNotNone(found_index)
        row = self.table.get_row_at_index(found_index)
        self.assertEqual(row["id"], "ИндексТест")

    def test_get_row_at_invalid_index(self) -> None:
        """Тест: неверный индекс."""
        self.assertIsNone(self.table.get_row_at_index(100))
        self.assertIsNone(self.table.get_row_at_index(-1))

    def test_get_hash_info(self) -> None:
        """Тест: получение информации о хеше."""
        v, h = self.table.get_hash_info("Тест")
        self.assertIsInstance(v, int)
        self.assertIsInstance(h, int)
        self.assertTrue(0 <= h < self.table._size)

    def test_display_returns_string(self) -> None:
        """Тест: метод display возвращает строку."""
        self.table.insert("Дисплей", "Данные")
        output = self.table.display()
        self.assertIsInstance(output, str)
        self.assertIn("Дисплей", output)
        self.assertIn("Коэффициент заполнения", output)

    def test_insert_full_table(self) -> None:
        """Тест: вставка в полную таблицу."""
        small_table = HashTable(3)
        small_table.insert("A", "1")
        small_table.insert("B", "2")
        small_table.insert("C", "3")
        result = small_table.insert("D", "4")
        self.assertFalse(result)

    def test_delete_updates_record_count(self) -> None:
        """Тест: удаление обновляет счётчик."""
        self.table.insert("Запись1", "Данные1")
        self.table.insert("Запись2", "Данные2")
        self.assertEqual(self.table._record_count, 2)
        self.table.delete("Запись1")
        self.assertEqual(self.table._record_count, 1)

    def test_collision_handling_quadratic(self) -> None:
        """Тест: обработка коллизий квадратичным пробированием."""
        collision_table = HashTable(7)

        for key in ["Аа", "Аб", "Ав", "Аг"]:
            collision_table.insert(key, f"Данные_{key}")

        for key in ["Аа", "Аб", "Ав", "Аг"]:
            self.assertIsNotNone(collision_table.search(key), f"Ключ {key} не найден")

    def test_search_after_deletion_of_collided_key(self) -> None:
        """Тест: поиск после удаления ключа, вызвавшего коллизию."""
        collision_table = HashTable(7)

        collision_table.insert("КлючА", "ДанныеА")
        collision_table.insert("КлючБ", "ДанныеБ")

        collision_table.delete("КлючА")

        self.assertEqual(collision_table.search("КлючБ"), "ДанныеБ")

    def test_delete_then_reinsert(self) -> None:
        """Тест: удаление и повторная вставка того же ключа."""
        self.table.insert("Временный", "Данные")
        self.assertEqual(self.table._record_count, 1)

        self.table.delete("Временный")
        self.assertEqual(self.table._record_count, 0)
        self.assertIsNone(self.table.search("Временный"))

        result = self.table.insert("Временный", "Новые данные")
        self.assertTrue(result)
        self.assertEqual(self.table._record_count, 1)
        self.assertEqual(self.table.search("Временный"), "Новые данные")

    def test_collision_flag_set_correctly(self) -> None:
        """Тест: флажок коллизий C устанавливается корректно."""
        small_table = HashTable(5)

        # Находим два ключа с ОДИНАКОВЫМ хешем
        # Для размера 5: ищем ключи, где h совпадает
        keys = ["Аа", "Ба"]  # Аа: (0*33+0)%5=0, Ба: (1*33+0)%5=33%5=3 - разные
        
        # Лучше: ищем ключи с одинаковым h через подбор
        # Для простоты создадим коллизию принудительно, вставив второй ключ в ту же h
        _, first_hash = small_table.get_hash_info("Аа")
        small_table.insert("Аа", "Первый")
        
        # Второй ключ должен дать ТАКОЙ ЖЕ h
        # Подбираем: "Ая" даст (0*33+32)%5 = 32%5 = 2
        # "Б"+"?" - (1*33+?)%5 = (33+?)%5 = (3+?%5)%5
        # Нам нужно 3+? ≡ 0 mod 5 → ? ≡ 2 mod 5 → буква с кодом 2 (В)
        # "Бв": (1*33+2)%5 = (33+2)%5 = 35%5 = 0 ✅
        
        small_table.insert("Бв", "Второй")
        
        # Проверяем, что у второй записи флажок C=1
        collision_found = False
        for idx in range(small_table._size):
            row = small_table.get_row_at_index(idx)
            if row and row["id"] == "Бв" and row["c"]:
                collision_found = True
                break

        self.assertTrue(collision_found, "Флажок коллизии C не установлен")

    def test_quadratic_probe_uses_squares(self) -> None:
        """Тест: квадратичное пробирование использует шаги 1², 2², 3²..."""
        probe_table = HashTable(10)

        # Находим два ключа с ОДИНАКОВЫМ хешем
        # Для размера 10: 
        # "Аа": (0*33+0)%10 = 0
        # Нужен второй ключ с h=0: (x*33+y)%10=0
        # Например, "К?": 11*33=363%10=3, нужно +y ≡7 mod10 → y=7 (Ж)
        # "Кж": (11*33+7)%10 = (363+7)%10 = 370%10=0 ✅
        
        _, first_hash = probe_table.get_hash_info("Аа")
        _, second_hash = probe_table.get_hash_info("Кж")
        
        self.assertEqual(first_hash, second_hash, "Ключи должны иметь одинаковый хеш")
        
        probe_table.insert("Аа", "Первый")
        probe_table.insert("Кж", "Второй")

        # Проверяем, что второй ключ НЕ на базовой позиции
        base_row = probe_table.get_row_at_index(first_hash)
        self.assertEqual(base_row["id"], "Аа", "Базовая позиция должна содержать первый ключ")

        # Находим позицию второго ключа
        second_position = None
        for idx in range(probe_table._size):
            row = probe_table.get_row_at_index(idx)
            if row and row["id"] == "Кж":
                second_position = idx
                break
        
        self.assertIsNotNone(second_position)
        self.assertNotEqual(second_position, first_hash)
        
        # Проверяем, что позиция соответствует квадратичному шагу
        # Должно быть: second_position = (first_hash + i²) % 10
        diff = (second_position - first_hash) % 10
        # diff должно быть полным квадратом: 1, 4, 9, 16%10=6, 25%10=5, ...
        # Допустимые значения: 1, 4, 9, 6, 5, 6, 9, 4, 1, 0
        is_quadratic = diff in [1, 4, 9, 6, 5]
        self.assertTrue(is_quadratic, f"Позиция {second_position} не соответствует квадратичному шагу от {first_hash}")

    def test_get_fill_factor_with_deletions(self) -> None:
        """Тест: коэффициент заполнения после удалений."""
        self.table.insert("Зап1", "Д1")
        self.table.insert("Зап2", "Д2")
        self.table.insert("Зап3", "Д3")

        initial = self.table.get_fill_factor()
        self.assertAlmostEqual(initial, 3.0 / DEFAULT_TABLE_SIZE, places=5)

        self.table.delete("Зап2")
        new_factor = self.table.get_fill_factor()
        self.assertAlmostEqual(new_factor, 2.0 / DEFAULT_TABLE_SIZE, places=5)

    def test_update_updates_correct_record(self) -> None:
        """Тест: обновление меняет только указанную запись."""
        self.table.insert("Ключ1", "Старые данные1")
        self.table.insert("Ключ2", "Старые данные2")

        self.table.update("Ключ1", "Новые данные1")

        self.assertEqual(self.table.search("Ключ1"), "Новые данные1")
        self.assertEqual(self.table.search("Ключ2"), "Старые данные2")


class TestHashTableEdgeCases(unittest.TestCase):
    """Тестирование краевых случаев."""

    def test_empty_table_search(self) -> None:
        """Тест: поиск в пустой таблице."""
        table = HashTable(10)
        self.assertIsNone(table.search("Что-то"))

    def test_delete_from_empty_table(self) -> None:
        """Тест: удаление из пустой таблицы."""
        table = HashTable(10)
        self.assertFalse(table.delete("Что-то"))

    def test_update_empty_table(self) -> None:
        """Тест: обновление в пустой таблице."""
        table = HashTable(10)
        self.assertFalse(table.update("Что-то", "Данные"))

    def test_insert_with_special_characters(self) -> None:
        """Тест: вставка ключа с буквой Ё."""
        table = HashTable(10)
        result = table.insert("Ёжик", "Тест")
        self.assertTrue(result)

    def test_display_on_empty_table(self) -> None:
        """Тест: display на пустой таблице."""
        table = HashTable(10)
        output = table.display()
        self.assertIsInstance(output, str)
        self.assertIn("СВОБОДНО", output)


if __name__ == '__main__':
    unittest.main()
