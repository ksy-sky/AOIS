"""
Хеш-таблица с квадратичным пробированием (Quadratic Probing).
Вариант 4 по заданию.
Тематика: Биология.

Формула пробирования: index = (hash_address + i²) mod size, i = 1, 2, 3, ...
При удалении используется мягкое удаление (флажок D).
Поиск не останавливается на удалённых ячейках.
"""

from typing import Optional, Tuple, List, Dict, Any
from src.constants import (
    DEFAULT_TABLE_SIZE,
    FLAG_TRUE,
    FLAG_FALSE,
    EMPTY_CELL_MARKER,
    DELETED_CELL_MARKER,
)
from src.hash_functions import HashFunctions


class HashTableRow:
    """
    Структура строки хеш-таблицы.
    Для открытой адресации поля Po и L не используются.
    """

    def __init__(self) -> None:
        self.id: str = ""           # ключевое слово
        self.c: bool = False        # флажок коллизий (была коллизия при вставке)
        self.u: bool = False        # флажок "занято"
        self.t: bool = True         # терминальный флажок (всегда True)
        self.l: bool = False        # флажок связи (не используется)
        self.d: bool = False        # флажок вычеркивания (мягкое удаление)
        self.po: int = -1           # не используется
        self.pi: str = ""           # данные

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "c": self.c, "u": self.u, "t": self.t,
            "l": self.l, "d": self.d, "po": self.po, "pi": self.pi,
        }

    def is_active(self) -> bool:
        """Ячейка активна (занята и не удалена)."""
        return self.u and not self.d

    def is_available_for_insert(self) -> bool:
        """Ячейка доступна для вставки (свободна или удалена)."""
        return not self.u or self.d

    def is_never_occupied(self) -> bool:
        """Ячейка никогда не была занята (терминальное условие для поиска)."""
        return not self.u


class HashTable:
    """
    Хеш-таблица с разрешением коллизий методом КВАДРАТИЧНОГО ПРОБИРОВАНИЯ.
    Формула: index = (start_hash + i²) mod size, i = 1, 2, 3, ...
    Вариант 4 по заданию.
    """

    def __init__(self, size: int = DEFAULT_TABLE_SIZE) -> None:
        self._size: int = size
        self._table: List[HashTableRow] = [HashTableRow() for _ in range(size)]
        self._record_count: int = 0
        self._hash_func = HashFunctions()

    def _quadratic_probe(self, start_hash: int, key: str, for_insert: bool) -> Tuple[int, Optional[str]]:
        """
        Квадратичное пробирование.
        
        for_insert=True:  ищет свободное место (можно использовать удалённые)
        for_insert=False: ищет точное совпадение (останавливается на never_occupied)
        """
        # Проверка базовой позиции
        base_row = self._table[start_hash]

        if for_insert:
            if base_row.is_available_for_insert():
                return start_hash, None
            if base_row.is_active() and base_row.id == key:
                return start_hash, "duplicate"
        else:
            if base_row.is_active() and base_row.id == key:
                return start_hash, None
            if base_row.is_never_occupied():
                return start_hash, "not_found"

        # Квадратичное пробирование
        for step in range(1, self._size + 1):
            offset = step * step
            current_index = (start_hash + offset) % self._size
            row = self._table[current_index]

            if for_insert:
                if row.is_available_for_insert():
                    return current_index, None
                if row.is_active() and row.id == key:
                    return current_index, "duplicate"
            else:
                if row.is_active() and row.id == key:
                    return current_index, None
                if row.is_never_occupied():
                    return current_index, "not_found"

        return -1, "full"

    def insert(self, key: str, data: str) -> bool:
        """Вставка записи."""
        if self._record_count >= self._size:
            return False

        numeric_value = self._hash_func.compute_numeric_value(key)
        hash_address = self._hash_func.compute_hash_address(numeric_value, self._size)

        position, status = self._quadratic_probe(hash_address, key, for_insert=True)

        if status == "duplicate":
            return False
        if position == -1 or status == "full":
            return False

        # Флаг коллизии: позиция отличается от базовой И базовая занята активной записью
        is_collision = (position != hash_address and self._table[hash_address].is_active())

        row = self._table[position]
        row.id = key
        row.c = is_collision
        row.u = True
        row.d = False
        row.t = True
        row.pi = data

        self._record_count += 1
        return True

    def search(self, key: str) -> Optional[str]:
        """Поиск данных по ключу."""
        numeric_value = self._hash_func.compute_numeric_value(key)
        hash_address = self._hash_func.compute_hash_address(numeric_value, self._size)

        position, status = self._quadratic_probe(hash_address, key, for_insert=False)

        if status == "not_found" or position == -1:
            return None

        row = self._table[position]
        if row.is_active() and row.id == key:
            return row.pi

        return None

    def update(self, key: str, new_data: str) -> bool:
        """Обновление данных по ключу."""
        numeric_value = self._hash_func.compute_numeric_value(key)
        hash_address = self._hash_func.compute_hash_address(numeric_value, self._size)

        position, status = self._quadratic_probe(hash_address, key, for_insert=False)

        if status == "not_found" or position == -1:
            return False

        row = self._table[position]
        if row.is_active() and row.id == key:
            row.pi = new_data
            return True

        return False

    def delete(self, key: str) -> bool:
        """
        Мягкое удаление записи.
        Устанавливаем D=1, U оставляем True.
        Это не разрывает цепочку пробирования при поиске.
        """
        numeric_value = self._hash_func.compute_numeric_value(key)
        hash_address = self._hash_func.compute_hash_address(numeric_value, self._size)

        position, status = self._quadratic_probe(hash_address, key, for_insert=False)

        if status == "not_found" or position == -1:
            return False

        row = self._table[position]
        if row.is_active() and row.id == key:
            row.d = True
            self._record_count -= 1
            return True

        return False

    def get_fill_factor(self) -> float:
        """Коэффициент заполнения (активные записи / размер)."""
        return self._record_count / self._size

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Все активные записи."""
        return [row.to_dict() for row in self._table if row.is_active()]

    def get_row_at_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Строка по индексу (для отладки)."""
        if 0 <= index < self._size:
            return self._table[index].to_dict()
        return None

    def display(self) -> str:
        """Вывод таблицы."""
        lines = ["=" * 100]
        lines.append(f"{'№':<3} {'ID':<20} {'C':<2} {'U':<2} {'T':<2} {'L':<2} {'D':<2} {'Po':<4} Pi")
        lines.append("=" * 100)

        for idx, row in enumerate(self._table):
            if row.is_active():
                lines.append(
                    f"{idx:<3} {row.id:<20} "
                    f"{FLAG_TRUE if row.c else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.u else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.t else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.l else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.d else FLAG_FALSE:<2} "
                    f"{row.po:<4} {row.pi[:50]}"
                )
            elif row.u and row.d:
                lines.append(
                    f"{idx:<3} {DELETED_CELL_MARKER}{row.id:<12} "
                    f"{FLAG_TRUE if row.c else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.u else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.t else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.l else FLAG_FALSE:<2} "
                    f"{FLAG_TRUE if row.d else FLAG_FALSE:<2} "
                    f"{row.po:<4} ---"
                )
            else:
                lines.append(f"{idx:<3} {EMPTY_CELL_MARKER:<20} -  -  -  -  -  -    -")

        lines.append("=" * 100)
        lines.append(f"Всего записей: {self._record_count}")
        lines.append(f"Коэффициент заполнения: {self.get_fill_factor():.4f}")
        lines.append("=" * 100)

        return "\n".join(lines)

    def get_hash_info(self, key: str) -> Tuple[int, int]:
        """V и h для ключа."""
        v = self._hash_func.compute_numeric_value(key)
        h = self._hash_func.compute_hash_address(v, self._size)
        return v, h
