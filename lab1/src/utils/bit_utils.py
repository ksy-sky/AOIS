from typing import List, Tuple


class BitUtils:
    """Класс с утилитарными методами для работы с битами"""
    
    def not_bits(self, bits: List[int]) -> List[int]:
        """Побитовое НЕ (инверсия)"""
        result = []
        for b in bits:
            if b == 0:
                result.append(1)
            else:
                result.append(0)
        return result
    
    def and_bits(self, a: List[int], b: List[int]) -> List[int]:
        """Побитовое И"""
        if len(a) != len(b):
            raise ValueError("Длины массивов должны совпадать")
        result = []
        for i in range(len(a)):
            if a[i] == 1 and b[i] == 1:
                result.append(1)
            else:
                result.append(0)
        return result
    
    def or_bits(self, a: List[int], b: List[int]) -> List[int]:
        """Побитовое ИЛИ"""
        if len(a) != len(b):
            raise ValueError("Длины массивов должны совпадать")
        result = []
        for i in range(len(a)):
            if a[i] == 1 or b[i] == 1:
                result.append(1)
            else:
                result.append(0)
        return result
    
    def xor_bits(self, a: List[int], b: List[int]) -> List[int]:
        """Побитовое исключающее ИЛИ (XOR)"""
        if len(a) != len(b):
            raise ValueError("Длины массивов должны совпадать")
        result = []
        for i in range(len(a)):
            if a[i] != b[i]:
                result.append(1)
            else:
                result.append(0)
        return result
    
    def half_adder(self, bit_a: int, bit_b: int) -> Tuple[int, int]:
        """Полусумматор"""
        total = bit_a + bit_b
        return (total % 2, total // 2)
    
    def full_adder(self, bit_a: int, bit_b: int, carry_in: int) -> Tuple[int, int]:
        """Полный сумматор"""
        total = bit_a + bit_b + carry_in
        return (total % 2, total // 2)
    
    def add_bits(self, a: List[int], b: List[int], carry_in: int = 0) -> Tuple[List[int], int]:
        """Сложение двух битовых массивов"""
        if len(a) != len(b):
            raise ValueError("Длины массивов должны совпадать")
        
        result = []
        carry = carry_in
        for i in range(len(a) - 1, -1, -1):
            sum_bit, carry = self.full_adder(a[i], b[i], carry)
            result.insert(0, sum_bit)
        
        return result, carry
    
    def shift_left(self, bits: List[int], n: int) -> List[int]:
        """Логический сдвиг влево"""
        if n <= 0:
            return bits.copy()
        if n >= len(bits):
            return [0] * len(bits)
        return bits[n:] + [0] * n
    
    def shift_right_logical(self, bits: List[int], n: int) -> List[int]:
        """Логический сдвиг вправо"""
        if n <= 0:
            return bits.copy()
        if n >= len(bits):
            return [0] * len(bits)
        return [0] * n + bits[:-n]
    
    def shift_right_arithmetic(self, bits: List[int], n: int) -> List[int]:
        """Арифметический сдвиг вправо (сохраняет знак)"""
        if n <= 0:
            return bits.copy()
        if n >= len(bits):
            return [bits[0]] * len(bits)
        return [bits[0]] * n + bits[:-n]
