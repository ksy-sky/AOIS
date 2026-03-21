"""
Класс для конвертации целых чисел в различные коды
"""

from typing import Dict
from src.core.binary32 import Binary32
from src.utils.bit_utils import BitUtils


class IntegerConverter:
    """Конвертер целых чисел в прямой, обратный и дополнительный коды"""
    
    # Константы
    MIN_32BIT = -2147483648  # -2^31
    MAX_32BIT = 2147483647   # 2^31 - 1
    MAGNITUDE_BITS = 31
    SPECIAL_VALUE = 2147483648  # 2^31
    
    def __init__(self):
        self.bit_utils = BitUtils()
    
    def to_direct(self, value: int) -> Binary32:
        """Прямой код: знак + модуль"""
        self._validate_range(value)
        sign_bit = 0 if value >= 0 else 1
        magnitude = abs(value)
        
        if value == self.MIN_32BIT:
            # Для -2^31: знак 1, все биты модуля 0 (это специальное представление)
            magnitude_bits = [0] * self.MAGNITUDE_BITS
        else:
            magnitude_bits = self._int_to_bits(magnitude, self.MAGNITUDE_BITS)
        
        return Binary32([sign_bit] + magnitude_bits)
    
    def from_direct(self, bits: Binary32) -> int:
        """Из прямого кода в десятичное"""
        sign_bit = bits.bits[0]
        magnitude = self._bits_to_int(bits.bits[1:])
        
        # Специальный случай: -2^31 (знак 1, все биты модуля 0)
        if sign_bit == 1 and magnitude == 0:
            return self.MIN_32BIT
        
        return magnitude if sign_bit == 0 else -magnitude
    
    def to_inverse(self, value: int) -> Binary32:
        """Обратный код"""
        # Для положительных чисел обратный код = прямой код
        if value >= 0:
            return self.to_direct(value)
        
        # Для отрицательных чисел
        if value == self.MIN_32BIT:
            # Для -2^31 обратный код - это 1 + 31 нулей
            return Binary32([1] + [0] * self.MAGNITUDE_BITS)
        
        magnitude = abs(value)
        magnitude_bits = self._int_to_bits(magnitude, self.MAGNITUDE_BITS)
        # Инвертируем биты модуля
        inverted = self.bit_utils.not_bits(magnitude_bits)
        return Binary32([1] + inverted)
    
    def from_inverse(self, bits: Binary32) -> int:
        """Из обратного кода в десятичное"""
        # Положительные числа
        if bits.bits[0] == 0:
            return self.from_direct(bits)
        
        # Специальный случай: -2^31
        if all(b == 0 for b in bits.bits[1:]):
            return self.MIN_32BIT
        
        # Для отрицательных чисел инвертируем модуль
        magnitude_bits = bits.bits[1:]
        inverted_magnitude = self.bit_utils.not_bits(magnitude_bits)
        magnitude = self._bits_to_int(inverted_magnitude)
        return -magnitude
    
    def to_complement(self, value: int) -> Binary32:
        """Дополнительный код"""
        # Для положительных чисел дополнительный код = прямой код
        if value >= 0:
            return self.to_direct(value)
        
        # Для отрицательных чисел
        if value == self.MIN_32BIT:
            # Для -2^31 дополнительный код - это 1 + 31 нулей
            return Binary32([1] + [0] * self.MAGNITUDE_BITS)
        
        # Дополнительный код = обратный код + 1
        inverse = self.to_inverse(value)
        # Создаем единицу для сложения
        one_bits = [0] * (self.MAGNITUDE_BITS) + [1]
        result_bits, carry = self.bit_utils.add_bits(inverse.bits, one_bits, 0)
        return Binary32(result_bits)
    
    def from_complement(self, bits: Binary32) -> int:
        """Из дополнительного кода в десятичное"""
        # Положительные числа (знаковый бит 0)
        if bits.bits[0] == 0:
            return self.from_direct(bits)
        
        # Специальный случай: -2^31
        if all(b == 0 for b in bits.bits[1:]):
            return self.MIN_32BIT
        
        # Для отрицательных чисел: инвертируем все биты и прибавляем 1
        # Инвертируем все 32 бита
        inverted_bits = self.bit_utils.not_bits(bits.bits)
        # Прибавляем 1
        one_bits = [0] * (self.MAGNITUDE_BITS) + [1]
        result_bits, _ = self.bit_utils.add_bits(inverted_bits, one_bits, 0)
        # Результат - положительное число, делаем его отрицательным
        result = self.from_direct(Binary32(result_bits))
        return -result

    def to_all_codes(self, value: int) -> Dict[str, Binary32]:
        """Получить все три кода"""
        return {
            'direct': self.to_direct(value),
            'inverse': self.to_inverse(value),
            'complement': self.to_complement(value)
        }
    
    def _validate_range(self, value: int) -> None:
        """Проверка диапазона значений"""
        if value < self.MIN_32BIT or value > self.MAX_32BIT:
            raise ValueError(f"Значение {value} вне диапазона [{self.MIN_32BIT}, {self.MAX_32BIT}]")
    
    def _int_to_bits(self, value: int, bits_count: int) -> list:
        """Преобразование в биты без побитовых операторов"""
        bits = []
        temp = value
        power = 1
        for _ in range(bits_count - 1):
            power = power * 2
        
        for _ in range(bits_count):
            if temp >= power:
                bits.append(1)
                temp = temp - power
            else:
                bits.append(0)
            power = power // 2
        
        return bits
    
    def _bits_to_int(self, bits: list) -> int:
        """Преобразование битов в число"""
        result = 0
        for bit in bits:
            result = result * 2 + bit
        return result