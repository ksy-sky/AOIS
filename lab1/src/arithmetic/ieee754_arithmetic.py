"""
Арифметика IEEE-754 (32 бита) с флагами и полной поддержкой спецзначений
"""

from typing import Tuple
from src.core.binary32 import Binary32
from src.converters.ieee754_converter import Ieee754Converter


class Ieee754Arithmetic:
    """Арифметические операции с числами IEEE-754"""
    
    # Флаги операций
    FLAG_NONE = 0
    FLAG_OVERFLOW = 1
    FLAG_UNDERFLOW = 2
    FLAG_INEXACT = 4
    FLAG_INVALID = 8
    
    def __init__(self):
        self.converter = Ieee754Converter()
    
    def _is_nan(self, bits: Binary32) -> bool:
        """Проверка на NaN"""
        exp = 0
        for i in range(8):
            exp = exp * 2 + bits.bits[1 + i]
        if exp != 255:
            return False
        for i in range(9, 32):
            if bits.bits[i] == 1:
                return True
        return False
    
    def _is_infinity(self, bits: Binary32) -> bool:
        """Проверка на бесконечность"""
        exp = 0
        for i in range(8):
            exp = exp * 2 + bits.bits[1 + i]
        if exp != 255:
            return False
        for i in range(9, 32):
            if bits.bits[i] == 1:
                return False
        return True
    
    def _get_infinity(self, sign: int) -> Binary32:
        """Получить бесконечность"""
        bits = [sign] + [1] * 8 + [0] * 23
        return Binary32(bits)
    
    def _float_to_binary32(self, value: float) -> Binary32:
        """Преобразование float в Binary32 через конвертер"""
        return self.converter.to_ieee754(value)
    
    def _binary32_to_float(self, bits: Binary32) -> float:
        """Преобразование Binary32 в float через конвертер"""
        return self.converter.from_ieee754(bits)
    
    def add_dec(self, a: float, b: float) -> Tuple[Binary32, float, int]:
        """Сложение десятичных чисел через IEEE-754"""
        # Проверка на NaN
        if self._is_nan_value(a) or self._is_nan_value(b):
            return self.converter._get_nan(), float('nan'), self.FLAG_INVALID
        
        # Проверка на бесконечности
        a_inf = self._is_inf_value(a)
        b_inf = self._is_inf_value(b)
        
        if a_inf and b_inf:
            if a == b:
                # Одинаковые знаки
                return self._float_to_binary32(a), a, self.FLAG_NONE
            else:
                # Разные знаки - NaN
                return self.converter._get_nan(), float('nan'), self.FLAG_INVALID
        
        if a_inf:
            return self._float_to_binary32(a), a, self.FLAG_NONE
        
        if b_inf:
            return self._float_to_binary32(b), b, self.FLAG_NONE
        
        # Обычное сложение
        result = a + b
        result_bin = self._float_to_binary32(result)
        flags = self.FLAG_NONE
        
        # Проверка на переполнение
        if self._is_inf_value(result) and not self._is_inf_value(a) and not self._is_inf_value(b):
            flags |= self.FLAG_OVERFLOW
        
        return result_bin, result, flags
    
    def multiply_dec(self, a: float, b: float) -> Tuple[Binary32, float, int]:
        """Умножение десятичных чисел через IEEE-754"""
        # Проверка на NaN
        if self._is_nan_value(a) or self._is_nan_value(b):
            return self.converter._get_nan(), float('nan'), self.FLAG_INVALID
        
        # Проверка на бесконечность * 0
        if (self._is_inf_value(a) and b == 0) or (self._is_inf_value(b) and a == 0):
            return self.converter._get_nan(), float('nan'), self.FLAG_INVALID
        
        # Проверка на бесконечности
        a_inf = self._is_inf_value(a)
        b_inf = self._is_inf_value(b)
        
        if a_inf or b_inf:
            sign = 1 if ((a < 0) ^ (b < 0)) else 0
            result = float('-inf') if sign else float('inf')
            return self._float_to_binary32(result), result, self.FLAG_OVERFLOW
        
        # Обычное умножение
        result = a * b
        result_bin = self._float_to_binary32(result)
        flags = self.FLAG_NONE
        
        # Проверка на переполнение
        if self._is_inf_value(result):
            flags |= self.FLAG_OVERFLOW
        
        return result_bin, result, flags
    
    def _is_nan_value(self, value: float) -> bool:
        """Проверка, является ли значение NaN"""
        return str(value) == 'nan' or value != value
    
    def _is_inf_value(self, value: float) -> bool:
        """Проверка, является ли значение бесконечностью"""
        return value == float('inf') or value == float('-inf')
    
    def subtract_dec(self, a: float, b: float) -> Tuple[Binary32, float, int]:
        """Вычитание десятичных чисел через IEEE-754"""
        result = a - b
        result_bin = self._float_to_binary32(result)
        flags = self.FLAG_NONE
        
        if result == float('inf') or result == float('-inf'):
            flags |= self.FLAG_OVERFLOW
        elif result == 0.0 and (a != 0.0 or b != 0.0):
            flags |= self.FLAG_UNDERFLOW
        
        return result_bin, result, flags
    
        """Умножение десятичных чисел через IEEE-754"""
        result = a * b
        result_bin = self._float_to_binary32(result)
        flags = self.FLAG_NONE
        
        if result == float('inf') or result == float('-inf'):
            flags |= self.FLAG_OVERFLOW
        elif result == 0.0 and (a != 0.0 and b != 0.0):
            flags |= self.FLAG_UNDERFLOW
        
        return result_bin, result, flags
    
    def divide_dec(self, a: float, b: float) -> Tuple[Binary32, float, int]:
        """Деление десятичных чисел через IEEE-754"""
        if b == 0.0:
            raise ValueError("Деление на ноль")
        
        result = a / b
        result_bin = self._float_to_binary32(result)
        flags = self.FLAG_NONE
        
        if result == float('inf') or result == float('-inf'):
            flags |= self.FLAG_OVERFLOW
        elif result == 0.0 and a != 0.0:
            flags |= self.FLAG_UNDERFLOW
        
        return result_bin, result, flags
