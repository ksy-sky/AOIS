from typing import Tuple
from ..core.binary32 import Binary32


class GrayBCD:
    """Работа с двоично-десятичным кодом в Gray коде"""
    
    GRAY_TO_DIGIT = {
        (0,0,0,0): 0, (0,0,0,1): 1, (0,0,1,1): 2, (0,0,1,0): 3,
        (0,1,1,0): 4, (0,1,1,1): 5, (0,1,0,1): 6, (0,1,0,0): 7,
        (1,1,0,0): 8, (1,1,0,1): 9,
    }
    
    DIGIT_TO_GRAY = {v: list(k) for k, v in GRAY_TO_DIGIT.items()}
    
    MAX_DIGITS = 8
    BITS_PER_DIGIT = 4
    TOTAL_BITS = MAX_DIGITS * BITS_PER_DIGIT
    
    def to_gray_bcd(self, value: int) -> Binary32:
        if value < 0:
            raise ValueError("Gray BCD поддерживает только неотрицательные числа")
        
        # Получаем цифры числа
        if value == 0:
            digits = [0] * self.MAX_DIGITS
        else:
            digits = []
            temp = value
            while temp > 0:
                digits.insert(0, temp % 10)
                temp = temp // 10
            # Дополняем нулями слева до MAX_DIGITS
            digits = [0] * (self.MAX_DIGITS - len(digits)) + digits
        
        bits = []
        for digit in digits:
            bits.extend(self.DIGIT_TO_GRAY[digit])
        
        return Binary32(bits)
    
    def from_gray_bcd(self, bits: Binary32) -> int:
        result = 0
        for i in range(0, self.TOTAL_BITS, self.BITS_PER_DIGIT):
            gray = tuple(bits.bits[i:i+self.BITS_PER_DIGIT])
            result = result * 10 + self.GRAY_TO_DIGIT[gray]
        return result
    
    def add(self, a: Binary32, b: Binary32) -> Tuple[Binary32, bool]:
        """Сложение в Gray BCD"""
        a_digits = self._gray_to_digits(a)
        b_digits = self._gray_to_digits(b)
        
        result_digits = [0] * self.MAX_DIGITS
        carry = 0
        
        # Складываем с младшего разряда (справа)
        for i in range(self.MAX_DIGITS - 1, -1, -1):
            total = a_digits[i] + b_digits[i] + carry
            if total >= 10:
                result_digits[i] = total - 10
                carry = 1
            else:
                result_digits[i] = total
                carry = 0
        
        overflow = (carry == 1)
        
        # Если переполнение, обнуляем результат
        if overflow:
            result_digits = [0] * self.MAX_DIGITS
        
        bits = []
        for digit in result_digits:
            bits.extend(self.DIGIT_TO_GRAY[digit])
        
        return Binary32(bits), overflow
    
    def add_dec(self, a: int, b: int) -> Tuple[Binary32, int, bool]:
        """Сложение десятичных чисел через Gray BCD"""
        a_bin = self.to_gray_bcd(a)
        b_bin = self.to_gray_bcd(b)
        result_bin, overflow = self.add(a_bin, b_bin)
        result_dec = self.from_gray_bcd(result_bin)
        return result_bin, result_dec, overflow
    
    def _gray_to_digits(self, bits: Binary32) -> list:
        """Преобразование Gray BCD в список цифр (от старшего к младшему)"""
        digits = []
        for i in range(0, self.TOTAL_BITS, self.BITS_PER_DIGIT):
            gray = tuple(bits.bits[i:i+self.BITS_PER_DIGIT])
            digits.append(self.GRAY_TO_DIGIT[gray])
        return digits
