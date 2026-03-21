from ..core.binary32 import Binary32

class Ieee754Converter:
    """Конвертер чисел с плавающей точкой в IEEE-754"""
    
    # Константы
    EXPONENT_BIAS = 127
    EXPONENT_BITS = 8
    MANTISSA_BITS = 23
    EXPONENT_MAX = 255
    EXPONENT_MIN = 0
    MIN_NORMAL_EXPONENT = -126
    MAX_NORMAL_EXPONENT = 127
    
    def to_ieee754(self, value: float) -> Binary32:
        """Преобразование float в IEEE-754"""
        # Проверка на NaN
        if self._is_nan(value):
            return self._get_nan()
        
        # Проверка на бесконечность
        if self._is_infinity(value):
            return self._get_infinity(value)
        
        # Ноль
        if value == 0.0:
            sign = 1 if str(value).startswith('-') else 0
            return Binary32([sign] + [0] * 31)
        
        sign = 0 if value > 0 else 1
        value = abs(value)
        
        # Нормализация
        exponent = 0
        if value >= 2.0:
            while value >= 2.0 and exponent < self.MAX_NORMAL_EXPONENT + 1:
                value = value / 2.0
                exponent = exponent + 1
        elif value < 1.0:
            while value < 1.0 and exponent > self.MIN_NORMAL_EXPONENT - 1:
                value = value * 2.0
                exponent = exponent - 1
        
        exponent_bias = exponent + self.EXPONENT_BIAS
        
        # Проверка на переполнение
        if exponent_bias >= self.EXPONENT_MAX:
            return self._get_infinity(value if sign == 0 else -value)
        
        # Денормализованное число
        if exponent_bias <= 0:
            exponent_bits = self._int_to_bits(0, self.EXPONENT_BITS)
            shift = 1 - exponent_bias
            mantissa = value
            for _ in range(shift):
                mantissa = mantissa / 2.0
            mantissa_bits = self._float_to_mantissa(mantissa)
        else:
            exponent_bits = self._int_to_bits(exponent_bias, self.EXPONENT_BITS)
            mantissa = value - 1.0
            mantissa_bits = self._float_to_mantissa(mantissa)
        
        return Binary32([sign] + exponent_bits + mantissa_bits)
    
    def from_ieee754(self, bits: Binary32) -> float:
        """Преобразование IEEE-754 в float (возвращает число, а не строку!)"""
        sign = bits.bits[0]
        exponent = self._bits_to_int(bits.bits[1:1+self.EXPONENT_BITS])
        mantissa_bits = bits.bits[1+self.EXPONENT_BITS:]
        
        # Проверка на спецзначения
        if exponent == self.EXPONENT_MAX:
            if all(b == 0 for b in mantissa_bits):
                return float('-inf') if sign == 1 else float('inf')
            else:
                return float('nan')
        
        # Вычисляем мантиссу
        mantissa = 0.0
        power = 0.5
        for i in range(self.MANTISSA_BITS):
            if mantissa_bits[i] == 1:
                mantissa = mantissa + power
            power = power / 2.0
        
        # Денормализованное число
        if exponent == 0:
            return (-1.0 if sign == 1 else 1.0) * mantissa * (2.0 ** (self.MIN_NORMAL_EXPONENT))
        
        # Нормализованное число
        mantissa = mantissa + 1.0
        return (-1.0 if sign == 1 else 1.0) * mantissa * (2.0 ** (exponent - self.EXPONENT_BIAS))
    
    def debug_explain(self, bits: Binary32) -> str:
        """Подробное объяснение представления (для отладки) - возвращает строку"""
        sign = bits.bits[0]
        exp_bits = bits.bits[1:1+self.EXPONENT_BITS]
        mant_bits = bits.bits[1+self.EXPONENT_BITS:]
        
        exp_value = 0
        for b in exp_bits:
            exp_value = exp_value * 2 + b
        
        # Проверка на спецзначения
        if exp_value == self.EXPONENT_MAX:
            if all(b == 0 for b in mant_bits):
                return f"Знак: {sign} → {('-' if sign else '+')}∞ (бесконечность)"
            else:
                return f"Знак: {sign} → NaN (не число)"
        
        mant_value = 0.0
        power = 0.5
        for b in mant_bits:
            if b == 1:
                mant_value = mant_value + power
            power = power / 2.0
        
        # Денормализованное число
        if exp_value == 0:
            return (f"Знак: {sign} ({'отрицательное' if sign else 'положительное'})\n"
                    f"Денормализованное число\n"
                    f"Экспонента: 0 (реальная: -126)\n"
                    f"Мантисса (без скрытой единицы): {mant_value}\n"
                    f"Формула: (-1)^{sign} × {mant_value} × 2^{-126}")
        
        # Нормализованное число
        mant_value = mant_value + 1.0
        return (f"Знак: {sign} ({'отрицательное' if sign else 'положительное'})\n"
                f"Экспонента: {exp_value} - {self.EXPONENT_BIAS} = {exp_value - self.EXPONENT_BIAS}\n"
                f"Мантисса (со скрытой единицей): {mant_value}\n"
                f"Формула: (-1)^{sign} × {mant_value} × 2^{exp_value - self.EXPONENT_BIAS}")
    
    def _is_nan(self, value: float) -> bool:
        """Проверка на NaN"""
        return str(value) == 'nan' or value != value
    
    def _is_infinity(self, value: float) -> bool:
        """Проверка на бесконечность"""
        return str(value) == 'inf' or str(value) == '-inf' or value == float('inf') or value == float('-inf')
    
    def _get_nan(self) -> Binary32:
        """Получить NaN (тихое)"""
        bits = [0] + [1] * 8 + [1] + [0] * 22
        return Binary32(bits)
    
    def _get_infinity(self, value: float) -> Binary32:
        """Получить бесконечность"""
        sign = 1 if value < 0 else 0
        bits = [sign] + [1] * 8 + [0] * 23
        return Binary32(bits)
    
    def _float_to_mantissa(self, mantissa: float) -> list:
        """Преобразование мантиссы в 23 бита"""
        mantissa_bits = []
        for _ in range(self.MANTISSA_BITS):
            mantissa = mantissa * 2.0
            if mantissa >= 1.0:
                mantissa_bits.append(1)
                mantissa = mantissa - 1.0
            else:
                mantissa_bits.append(0)
        return mantissa_bits
    
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
