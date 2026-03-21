"""
Арифметика в дополнительном коде
"""

from typing import Tuple
from ..core.binary32 import Binary32
from ..converters.integer_converter import IntegerConverter
from ..utils.bit_utils import BitUtils


class ComplementArithmetic:
    """Арифметические операции в дополнительном коде"""
    
    def __init__(self):
        self.converter = IntegerConverter()
        self.bit_utils = BitUtils()
    
    def add(self, a: Binary32, b: Binary32, check_overflow: bool = True) -> Tuple[Binary32, bool]:
        """Сложение в дополнительном коде"""
        result_bits, _ = self.bit_utils.add_bits(a.bits, b.bits, 0)
        
        overflow = False
        if check_overflow:
            sign_a = a.bits[0]
            sign_b = b.bits[0]
            sign_r = result_bits[0]
            overflow = (sign_a == sign_b) and (sign_a != sign_r)
        
        return Binary32(result_bits), overflow
    
    def negate(self, bits: Binary32) -> Binary32:
        """Получение отрицательного числа (инверсия + 1)"""
        inverted = self.bit_utils.not_bits(bits.bits)
        one = Binary32([0] * 31 + [1])
        result, _ = self.bit_utils.add_bits(inverted, one.bits, 0)
        return Binary32(result)
    
    def subtract(self, a: Binary32, b: Binary32, check_overflow: bool = True) -> Tuple[Binary32, bool]:
        """Вычитание: a - b = a + (-b)"""
        neg_b = self.negate(b)
        return self.add(a, neg_b, check_overflow)
    
    # Унифицированный интерфейс: (Binary32, int, bool)
    def add_dec(self, a: int, b: int) -> Tuple[Binary32, int, bool]:
        """Сложение десятичных чисел через дополнительный код"""
        a_bin = self.converter.to_complement(a)
        b_bin = self.converter.to_complement(b)
        result_bin, overflow = self.add(a_bin, b_bin)
        result_dec = self.converter.from_complement(result_bin)
        return result_bin, result_dec, overflow
    
    def subtract_dec(self, a: int, b: int) -> Tuple[Binary32, int, bool]:
        """Вычитание десятичных чисел через дополнительный код"""
        a_bin = self.converter.to_complement(a)
        b_bin = self.converter.to_complement(b)
        result_bin, overflow = self.subtract(a_bin, b_bin)
        result_dec = self.converter.from_complement(result_bin)
        return result_bin, result_dec, overflow