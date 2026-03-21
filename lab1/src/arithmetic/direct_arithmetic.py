"""
Арифметика в прямом коде (умножение и деление) с fixed-point представлением
"""

from typing import Tuple
from ..core.binary32 import Binary32
from ..converters.integer_converter import IntegerConverter
from ..utils.bit_utils import BitUtils


class DirectArithmetic:
    """Арифметические операции в прямом коде"""
    
    # Константы для fixed-point формата 16.16
    INTEGER_BITS = 16
    FRACTIONAL_BITS = 16
    MAX_INTEGER = 65535
    MAX_32BIT = 2147483647
    
    def __init__(self):
        self.converter = IntegerConverter()
        self.bit_utils = BitUtils()
    
    def multiply(self, a: Binary32, b: Binary32) -> Tuple[Binary32, bool]:
        """Умножение двух чисел в прямом коде"""
        sign_a = a.bits[0]
        sign_b = b.bits[0]
        sign_result = 0 if sign_a == sign_b else 1
        
        val_a = self._bits_to_int(a.bits[1:])
        val_b = self._bits_to_int(b.bits[1:])
        
        result_mag = 0
        overflow = False
        temp_b = val_b
        
        for _ in range(31):
            if temp_b % 2 == 1:
                if result_mag > self.MAX_32BIT - val_a:
                    overflow = True
                    result_mag = self.MAX_32BIT
                    break
                result_mag = result_mag + val_a
            val_a = val_a * 2
            temp_b = temp_b // 2
        
        if result_mag >= 2147483648:
            overflow = True
            result_mag = self.MAX_32BIT
        
        result_value = result_mag if sign_result == 0 else -result_mag
        return self.converter.to_direct(result_value), overflow
    
    def divide(self, dividend: Binary32, divisor: Binary32) -> Tuple[Binary32, bool]:
        """
        Деление в прямом коде с fixed-point представлением (16.16)
        Возвращает: (результат, переполнение)
        """
        if divisor.bits == [0] * 32:
            raise ValueError("Деление на ноль")
        
        sign_d = dividend.bits[0]
        sign_v = divisor.bits[0]
        sign_result = 0 if sign_d == sign_v else 1
        
        mag_d = self._bits_to_int(dividend.bits[1:])
        mag_v = self._bits_to_int(divisor.bits[1:])
        
        if mag_v == 0:
            raise ValueError("Деление на ноль")
        
        integer_part = 0
        remainder = mag_d
        overflow = False
        
        while remainder >= mag_v:
            remainder = remainder - mag_v
            integer_part = integer_part + 1
            if integer_part > self.MAX_INTEGER:
                overflow = True
                integer_part = self.MAX_INTEGER
                break
        
        fractional_bits = []
        for _ in range(self.FRACTIONAL_BITS):
            remainder = remainder * 2
            if remainder >= mag_v:
                fractional_bits.append(1)
                remainder = remainder - mag_v
            else:
                fractional_bits.append(0)
        
        integer_bits = self._int_to_bits(integer_part, self.INTEGER_BITS)
        magnitude_bits = integer_bits + fractional_bits
        
        if len(magnitude_bits) > 31:
            magnitude_bits = magnitude_bits[:31]
        elif len(magnitude_bits) < 31:
            magnitude_bits = [0] * (31 - len(magnitude_bits)) + magnitude_bits
        
        return Binary32([sign_result] + magnitude_bits), overflow
    
    # Унифицированный интерфейс: (Binary32, int, bool) для умножения
    def multiply_dec(self, a: int, b: int) -> Tuple[Binary32, int, bool]:
        """Умножение десятичных чисел через прямой код"""
        result_bin, overflow = self.multiply(
            self.converter.to_direct(a),
            self.converter.to_direct(b)
        )
        result_dec = self.converter.from_direct(result_bin)
        return result_bin, result_dec, overflow
    
    # Унифицированный интерфейс: (Binary32, float, bool) для деления
    def divide_dec(self, dividend: int, divisor: int) -> Tuple[Binary32, float, bool]:
        """Деление десятичных чисел через прямой код (fixed-point 16.16)"""
        result_bin, overflow = self.divide(
            self.converter.to_direct(dividend),
            self.converter.to_direct(divisor)
        )
        
        # Извлекаем десятичное значение из результата для вывода
        sign = result_bin.bits[0]
        magnitude_bits = result_bin.bits[1:]
        
        # Целая часть (первые 16 бит)
        integer_bits = magnitude_bits[:self.INTEGER_BITS]
        integer_part = 0
        for bit in integer_bits:
            integer_part = integer_part * 2 + bit
        
        # Дробная часть (последние 16 бит)
        fractional_bits = magnitude_bits[self.INTEGER_BITS:self.INTEGER_BITS + self.FRACTIONAL_BITS]
        fractional_part = 0.0
        power = 0.5
        for bit in fractional_bits:
            if bit == 1:
                fractional_part = fractional_part + power
            power = power / 2.0
        
        result_dec = integer_part + fractional_part
        if sign == 1:
            result_dec = -result_dec
        
        return result_bin, result_dec, overflow
    
    def _int_to_bits(self, value: int, bits_count: int) -> list:
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
        result = 0
        for bit in bits:
            result = result * 2 + bit
        return result