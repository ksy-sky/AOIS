"""
Глобальные константы для хеш-таблицы.
Все магические числа вынесены в отдельный конфигурационный файл.
"""

# Параметры хеш-таблицы
DEFAULT_TABLE_SIZE: int = 21  # > 20 строк по требованию
ALPHABET_SIZE: int = 33  # русский алфавит (А=0...Я=32)

# Коды флажков (для читаемости)
FLAG_TRUE: int = 1
FLAG_FALSE: int = 0

# Индексные константы
FIRST_LETTER_INDEX: int = 0
SECOND_LETTER_INDEX: int = 1
POSITIONAL_BASE: int = 33  # основание позиционной системы счисления

# Строковые константы для вывода
EMPTY_CELL_MARKER: str = "[СВОБОДНО]"
DELETED_CELL_MARKER: str = "[УДАЛЕНО]"
COLLISION_MESSAGE: str = "Коллизия!"