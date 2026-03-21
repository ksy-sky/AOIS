from typing import List, Optional

class Binary32:
    # Константы
    BITS_COUNT = 32
    
    def __init__(self, bits: Optional[List[int]] = None):
        if bits is None:
            self.bits = [0] * self.BITS_COUNT
        elif len(bits) == self.BITS_COUNT:
            for b in bits:
                if b not in (0, 1):
                    raise ValueError(f"Бит должен быть 0 или 1, получено {b}")
            self.bits = bits.copy()
        else:
            raise ValueError(f"Длина должна быть {self.BITS_COUNT}, получено {len(bits)}")
    
    def __str__(self) -> str:
        return ''.join(str(bit) for bit in self.bits)
    
    def __repr__(self) -> str:
        return f"Binary32('{self}')"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Binary32):
            return False
        return self.bits == other.bits
    
    def __getitem__(self, index: int) -> int:
        if 0 <= index < self.BITS_COUNT:
            return self.bits[index]
        raise IndexError(f"Индекс {index} вне диапазона [0, {self.BITS_COUNT - 1}]")
    
    def __setitem__(self, index: int, value: int) -> None:
        if not 0 <= index < self.BITS_COUNT:
            raise IndexError(f"Индекс {index} вне диапазона [0, {self.BITS_COUNT - 1}]")
        if value not in (0, 1):
            raise ValueError(f"Бит должен быть 0 или 1, получено {value}")
        self.bits[index] = value
    
    def copy(self) -> 'Binary32':
        return Binary32(self.bits)
    
    def to_hex(self) -> str:
        hex_chars = ['0', '1', '2', '3', '4', '5', '6', '7',
                     '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        hex_str = ''
        for i in range(0, self.BITS_COUNT, 4):
            nibble = 0
            for j in range(4):
                nibble = nibble * 2 + self.bits[i + j]
            hex_str += hex_chars[nibble]
        return hex_str
    
    def is_negative(self) -> bool:
        return self.bits[0] == 1
    
    def get_magnitude(self) -> List[int]:
        return self.bits[1:].copy()
    
    def set_magnitude(self, magnitude: List[int]) -> None:
        if len(magnitude) != self.BITS_COUNT - 1:
            raise ValueError(f"Длина модуля должна быть {self.BITS_COUNT - 1}, получено {len(magnitude)}")
        for b in magnitude:
            if b not in (0, 1):
                raise ValueError(f"Бит должен быть 0 или 1, получено {b}")
        self.bits[1:] = magnitude.copy()
        
    @classmethod
    def from_int(cls, value: int, bits_count: int = 32) -> 'Binary32':
        if bits_count != 32:
            raise ValueError("Поддерживается только 32 бита")
        
        max_value = 1
        for _ in range(32):
            max_value = max_value * 2
        max_value = max_value - 1
        
        if value < 0 or value > max_value:
            raise ValueError(f"Значение {value} вне диапазона [0, {max_value}]")
        
        bits = []
        temp = value
        power = 1
        for _ in range(31):
            power = power * 2
        
        for _ in range(32):
            if temp >= power:
                bits.append(1)
                temp = temp - power
            else:
                bits.append(0)
            power = power // 2
        
        return cls(bits)
    
    def to_int(self) -> int:
        result = 0
        for bit in self.bits:
            result = result * 2 + bit
        return result
