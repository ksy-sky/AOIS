# tests/test_all.py
"""
Полный набор тстов для всех модулей конвертеров
Запуск: pytest tests/test_all.py -v --cov=src --cov-report=term-missing
"""

import pytest
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем тестируемые модули из src
from src.utils.bit_utils import BitUtils
from src.core.binary32 import Binary32
from src.converters.ieee754_converter import Ieee754Converter
from src.converters.integer_converter import IntegerConverter
from src.bcd.gray_bcd import GrayBCD
from src.arithmetic.complement_arithmetic import ComplementArithmetic
from src.arithmetic.direct_arithmetic import DirectArithmetic
from src.arithmetic.ieee754_arithmetic import Ieee754Arithmetic

# ==================== FIXTURES ====================

@pytest.fixture
def bit_utils():
    """Фикстура для BitUtils"""
    return BitUtils()


@pytest.fixture
def binary32_instance():
    """Фикстура для Binary32"""
    return Binary32([0] * 32)


@pytest.fixture
def ieee754_converter():
    """Фикстура для Ieee754Converter"""
    return Ieee754Converter()


@pytest.fixture
def integer_converter():
    """Фикстура для IntegerConverter"""
    return IntegerConverter()


# ==================== TESTS FOR BIT_UTILS ====================

class TestBitUtils:
    """Тесты для BitUtils"""
    
    def test_not_bits(self, bit_utils):
        """Тест побитового НЕ"""
        assert bit_utils.not_bits([0, 0, 1, 1]) == [1, 1, 0, 0]
        assert bit_utils.not_bits([1, 1, 1]) == [0, 0, 0]
        assert bit_utils.not_bits([0, 0, 0]) == [1, 1, 1]
        assert bit_utils.not_bits([]) == []
    
    def test_and_bits(self, bit_utils):
        """Тест побитового И"""
        assert bit_utils.and_bits([1, 1, 0, 0], [1, 0, 1, 0]) == [1, 0, 0, 0]
        assert bit_utils.and_bits([1, 1, 1], [1, 1, 1]) == [1, 1, 1]
        assert bit_utils.and_bits([0, 0, 0], [1, 1, 1]) == [0, 0, 0]
        
        with pytest.raises(ValueError, match="Длины массивов должны совпадать"):
            bit_utils.and_bits([1, 0], [1, 0, 1])
    
    def test_or_bits(self, bit_utils):
        """Тест побитового ИЛИ"""
        assert bit_utils.or_bits([1, 1, 0, 0], [1, 0, 1, 0]) == [1, 1, 1, 0]
        assert bit_utils.or_bits([0, 0, 0], [1, 1, 1]) == [1, 1, 1]
        assert bit_utils.or_bits([0, 0], [0, 0]) == [0, 0]
        
        with pytest.raises(ValueError):
            bit_utils.or_bits([1], [1, 0])
    
    def test_xor_bits(self, bit_utils):
        """Тест побитового XOR"""
        assert bit_utils.xor_bits([1, 1, 0, 0], [1, 0, 1, 0]) == [0, 1, 1, 0]
        assert bit_utils.xor_bits([1, 0, 1], [1, 0, 1]) == [0, 0, 0]
        
        with pytest.raises(ValueError):
            bit_utils.xor_bits([1], [1, 0])
    
    def test_half_adder(self, bit_utils):
        """Тест полусумматора"""
        assert bit_utils.half_adder(0, 0) == (0, 0)
        assert bit_utils.half_adder(0, 1) == (1, 0)
        assert bit_utils.half_adder(1, 0) == (1, 0)
        assert bit_utils.half_adder(1, 1) == (0, 1)
    
    def test_full_adder(self, bit_utils):
        """Тест полного сумматора"""
        assert bit_utils.full_adder(0, 0, 0) == (0, 0)
        assert bit_utils.full_adder(0, 1, 0) == (1, 0)
        assert bit_utils.full_adder(1, 1, 0) == (0, 1)
        assert bit_utils.full_adder(1, 1, 1) == (1, 1)
        assert bit_utils.full_adder(0, 1, 1) == (0, 1)
    
    def test_add_bits(self, bit_utils):
        """Тест сложения битовых массивов"""
        result, carry = bit_utils.add_bits([0, 1], [0, 1])
        assert result == [1, 0]
        assert carry == 0
        
        result, carry = bit_utils.add_bits([1, 1], [0, 1])
        assert result == [0, 0]
        assert carry == 1
        
        result, carry = bit_utils.add_bits([0, 1], [0, 1], 1)
        assert result == [1, 1]
        assert carry == 0
        
        with pytest.raises(ValueError):
            bit_utils.add_bits([1, 0], [1])
    
    def test_shift_left(self, bit_utils):
        """Тест сдвига влево"""
        bits = [1, 0, 1, 0]
        assert bit_utils.shift_left(bits, 0) == [1, 0, 1, 0]
        assert bit_utils.shift_left(bits, 1) == [0, 1, 0, 0]
        assert bit_utils.shift_left(bits, 2) == [1, 0, 0, 0]
        assert bit_utils.shift_left(bits, 4) == [0, 0, 0, 0]
        assert bit_utils.shift_left(bits, 5) == [0, 0, 0, 0]
    
    def test_shift_right_logical(self, bit_utils):
        """Тест логического сдвига вправо"""
        bits = [1, 0, 1, 0]
        assert bit_utils.shift_right_logical(bits, 0) == [1, 0, 1, 0]
        assert bit_utils.shift_right_logical(bits, 1) == [0, 1, 0, 1]
        assert bit_utils.shift_right_logical(bits, 2) == [0, 0, 1, 0]
        assert bit_utils.shift_right_logical(bits, 4) == [0, 0, 0, 0]
    
    def test_shift_right_arithmetic(self, bit_utils):
        """Тест арифметического сдвига вправо"""
        bits_pos = [0, 1, 0, 1]
        assert bit_utils.shift_right_arithmetic(bits_pos, 1) == [0, 0, 1, 0]
        assert bit_utils.shift_right_arithmetic(bits_pos, 2) == [0, 0, 0, 1]
        
        bits_neg = [1, 0, 1, 0]
        assert bit_utils.shift_right_arithmetic(bits_neg, 1) == [1, 1, 0, 1]
        assert bit_utils.shift_right_arithmetic(bits_neg, 2) == [1, 1, 1, 0]
        assert bit_utils.shift_right_arithmetic(bits_neg, 4) == [1, 1, 1, 1]


# ==================== TESTS FOR BINARY32 ====================

class TestBinary32:
    """Тесты для Binary32"""
    
    def test_constructor_default(self):
        """Тест конструктора по умолчанию"""
        b = Binary32()
        assert b.bits == [0] * 32
        assert str(b) == '0' * 32
    
    def test_constructor_with_bits(self):
        """Тест конструктора с битами"""
        bits = [1] * 32
        b = Binary32(bits)
        assert b.bits == bits
        
        with pytest.raises(ValueError, match="Длина должна быть 32"):
            Binary32([1, 0])
        
        with pytest.raises(ValueError, match="Бит должен быть 0 или 1"):
            Binary32([2] * 32)
    
    def test_str_and_repr(self):
        """Тест строкового представления"""
        b = Binary32([1, 0, 1, 0] + [0] * 28)
        assert str(b) == '1010' + '0' * 28
        assert repr(b) == "Binary32('1010" + '0' * 28 + "')"
    
    def test_equality(self):
        """Тест сравнения"""
        b1 = Binary32([1] * 32)
        b2 = Binary32([1] * 32)
        b3 = Binary32([0] * 32)
        
        assert b1 == b2
        assert b1 != b3
        assert b1 != "not a binary32"
    
    def test_getitem(self, binary32_instance):
        """Тест получения бита по индексу"""
        binary32_instance.bits[5] = 1
        assert binary32_instance[5] == 1
        
        with pytest.raises(IndexError):
            _ = binary32_instance[32]
    
    def test_setitem(self, binary32_instance):
        """Тест установки бита по индексу"""
        binary32_instance[10] = 1
        assert binary32_instance.bits[10] == 1
        
        with pytest.raises(IndexError):
            binary32_instance[32] = 1
        with pytest.raises(ValueError):
            binary32_instance[0] = 2
    
    def test_copy(self):
        """Тест копирования"""
        b = Binary32([1, 0] + [0] * 30)
        copied = b.copy()
        assert copied == b
        assert copied is not b
    
    def test_to_hex(self):
        """Тест преобразования в шестнадцатеричную строку"""
        b = Binary32([0] * 32)
        assert b.to_hex() == '0' * 8
        
        b = Binary32([1, 1, 1, 1] + [0] * 28)
        assert b.to_hex() == 'f0000000'
    
    def test_is_negative(self):
        """Тест проверки знака"""
        b = Binary32([1] + [0] * 31)
        assert b.is_negative() is True
        
        b = Binary32([0] + [1] * 31)
        assert b.is_negative() is False
    
    def test_get_magnitude(self):
        """Тест получения модуля"""
        b = Binary32([1, 1, 0, 1] + [0] * 28)
        assert b.get_magnitude() == [1, 0, 1] + [0] * 28
    
    def test_set_magnitude(self):
        """Тест установки модуля"""
        b = Binary32()
        magnitude = [1] * 31
        b.set_magnitude(magnitude)
        assert b.bits[1:] == magnitude
        
        with pytest.raises(ValueError):
            b.set_magnitude([1] * 30)
    
    def test_from_int(self):
        """Тест создания из целого числа"""
        b = Binary32.from_int(0)
        assert b.to_int() == 0
        
        b = Binary32.from_int(255)
        assert b.to_int() == 255
        
        b = Binary32.from_int(2**32 - 1)
        assert b.to_int() == 2**32 - 1
        
        with pytest.raises(ValueError):
            Binary32.from_int(-1)
        with pytest.raises(ValueError):
            Binary32.from_int(2**32)
    
    def test_to_int(self):
        """Тест преобразования в целое число"""
        b = Binary32([0] * 32)
        assert b.to_int() == 0
        
        b = Binary32([1] * 32)
        assert b.to_int() == 2**32 - 1


# ==================== TESTS FOR IEEE754_CONVERTER ====================

class TestIeee754Converter:
    """Тесты для Ieee754Converter"""
    
    def test_nan_conversion(self, ieee754_converter):
        """Тест преобразования NaN"""
        nan_result = ieee754_converter.to_ieee754(float('nan'))
        assert nan_result.bits[1:9] == [1] * 8
        assert any(b == 1 for b in nan_result.bits[9:])
        
        from_nan = ieee754_converter.from_ieee754(nan_result)
        assert str(from_nan) == 'nan'
    
    def test_infinity_conversion(self, ieee754_converter):
        """Тест преобразования бесконечности"""
        pos_inf = ieee754_converter.to_ieee754(float('inf'))
        assert pos_inf.bits[0] == 0
        assert pos_inf.bits[1:9] == [1] * 8
        assert all(b == 0 for b in pos_inf.bits[9:])
        
        neg_inf = ieee754_converter.to_ieee754(float('-inf'))
        assert neg_inf.bits[0] == 1
        assert neg_inf.bits[1:9] == [1] * 8
        assert all(b == 0 for b in neg_inf.bits[9:])
        
        from_inf = ieee754_converter.from_ieee754(pos_inf)
        assert from_inf == float('inf')
    
    def test_zero_conversion(self, ieee754_converter):
        """Тест преобразования нуля"""
        pos_zero = ieee754_converter.to_ieee754(0.0)
        assert pos_zero.bits[0] == 0
        assert all(b == 0 for b in pos_zero.bits[1:])
        
        from_zero = ieee754_converter.from_ieee754(pos_zero)
        assert from_zero == 0.0
    
    def test_positive_normal_numbers(self, ieee754_converter):
        """Тест положительных нормализованных чисел"""
        test_cases = [1.0, 2.0, 0.5, 3.14, 123.456]
        for value in test_cases:
            converted = ieee754_converter.to_ieee754(value)
            back = ieee754_converter.from_ieee754(converted)
            if value != 0:
                assert abs(back - value) / abs(value) < 1e-6
    
    def test_negative_normal_numbers(self, ieee754_converter):
        """Тест отрицательных нормализованных чисел"""
        test_cases = [-1.0, -2.0, -0.5, -3.14, -123.456]
        for value in test_cases:
            converted = ieee754_converter.to_ieee754(value)
            back = ieee754_converter.from_ieee754(converted)
            if value != 0:
                assert abs(back - value) / abs(value) < 1e-6
    
    def test_debug_explain(self, ieee754_converter):
        """Тест отладочного объяснения"""
        b = Binary32([0] * 32)
        explanation = ieee754_converter.debug_explain(b)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_is_nan(self, ieee754_converter):
        """Тест проверки на NaN"""
        assert ieee754_converter._is_nan(float('nan')) is True
        assert ieee754_converter._is_nan(1.0) is False
    
    def test_is_infinity(self, ieee754_converter):
        """Тест проверки на бесконечность"""
        assert ieee754_converter._is_infinity(float('inf')) is True
        assert ieee754_converter._is_infinity(float('-inf')) is True
        assert ieee754_converter._is_infinity(1.0) is False


# ==================== TESTS FOR INTEGER_CONVERTER ====================

class TestIntegerConverter:
    """Тесты для IntegerConverter"""
    
    def test_positive_direct_code(self, integer_converter):
        """Тест прямого кода для положительных чисел"""
        test_cases = [0, 1, 127, 255, 2**31 - 1]
        for value in test_cases:
            direct = integer_converter.to_direct(value)
            back = integer_converter.from_direct(direct)
            assert back == value
            assert direct.bits[0] == 0
    
    def test_negative_direct_code(self, integer_converter):
        """Тест прямого кода для отрицательных чисел"""
        test_cases = [-1, -127, -255, -2**31 + 1]
        for value in test_cases:
            direct = integer_converter.to_direct(value)
            back = integer_converter.from_direct(direct)
            assert back == value
            assert direct.bits[0] == 1
    
    
    def test_positive_inverse_code(self, integer_converter):
        """Тест обратного кода для положительных чисел"""
        test_cases = [0, 1, 127, 255, 2**31 - 1]
        for value in test_cases:
            inverse = integer_converter.to_inverse(value)
            back = integer_converter.from_inverse(inverse)
            assert back == value
    
    def test_negative_inverse_code(self, integer_converter):
        """Тест обратного кода для отрицательных чисел"""
        test_cases = [-1, -127, -255]
        for value in test_cases:
            inverse = integer_converter.to_inverse(value)
            back = integer_converter.from_inverse(inverse)
            assert back == value
        
        # Проверяем минимальное значение (особый случай)
        min_value = -2**31
        inverse = integer_converter.to_inverse(min_value)
        back = integer_converter.from_inverse(inverse)
        assert back == min_value
    
    def test_min_value_inverse(self, integer_converter):
        """Тест минимального значения в обратном коде"""
        min_value = -2**31
        inverse = integer_converter.to_inverse(min_value)
        back = integer_converter.from_inverse(inverse)
        assert back == min_value
        # Проверяем, что обратный код для -2^31 - это 1 + 31 нулей
        assert inverse.bits[0] == 1
        assert all(b == 0 for b in inverse.bits[1:])
    
    def test_positive_complement_code(self, integer_converter):
        """Тест дополнительного кода для положительных чисел"""
        test_cases = [0, 1, 127, 255, 2**31 - 1]
        for value in test_cases:
            complement = integer_converter.to_complement(value)
            back = integer_converter.from_complement(complement)
            assert back == value
    
    def test_min_value_direct(self, integer_converter):
        """Тест минимального значения в прямом коде"""
        min_value = -2**31
        direct = integer_converter.to_direct(min_value)
        back = integer_converter.from_direct(direct)
        # В прямом коде минимальное число представляется как 1 + 31 нулей
        assert back == min_value
        # Проверяем структуру: знак 1, все остальные биты 0
        assert direct.bits[0] == 1
        assert all(b == 0 for b in direct.bits[1:])
    
    def test_negative_complement_code(self, integer_converter):
        """Тест дополнительного кода для отрицательных чисел"""
        # Тестируем обычные отрицательные числа
        test_cases = [-1, -127, -255, -2**31 + 1]
        for value in test_cases:
            complement = integer_converter.to_complement(value)
            back = integer_converter.from_complement(complement)
            assert back == value, f"Failed for value {value}"
        
        # Тестируем минимальное значение
        min_value = -2**31
        complement = integer_converter.to_complement(min_value)
        back = integer_converter.from_complement(complement)
        assert back == min_value
        
        # Проверяем, что для -1 дополнительный код - все единицы
        if -1 in test_cases:
            complement_minus_one = integer_converter.to_complement(-1)
            assert all(b == 1 for b in complement_minus_one.bits)
    
    def test_all_codes(self, integer_converter):
        """Тест получения всех кодов"""
        # Тест для положительного числа
        value = 42
        codes = integer_converter.to_all_codes(value)
        assert 'direct' in codes
        assert 'inverse' in codes
        assert 'complement' in codes
        
        # Проверяем, что для положительного числа все коды одинаковы
        assert codes['direct'].bits == codes['inverse'].bits == codes['complement'].bits
        
        # Проверяем обратное преобразование
        assert integer_converter.from_direct(codes['direct']) == value
        assert integer_converter.from_inverse(codes['inverse']) == value
        assert integer_converter.from_complement(codes['complement']) == value
        
        # Тест для отрицательного числа
        value = -42
        codes = integer_converter.to_all_codes(value)
        assert integer_converter.from_direct(codes['direct']) == value
        assert integer_converter.from_inverse(codes['inverse']) == value
        assert integer_converter.from_complement(codes['complement']) == value
        
        # Для отрицательного числа прямой и обратный коды должны различаться
        assert codes['direct'].bits != codes['inverse'].bits
        
        # Тест для минимального значения
        value = -2**31
        codes = integer_converter.to_all_codes(value)
        assert integer_converter.from_direct(codes['direct']) == value
        assert integer_converter.from_inverse(codes['inverse']) == value
        assert integer_converter.from_complement(codes['complement']) == value
        
        # Для минимального значения все коды одинаковы (1 + 31 нулей)
        assert codes['direct'].bits == codes['inverse'].bits == codes['complement'].bits
        assert codes['direct'].bits[0] == 1
        assert all(b == 0 for b in codes['direct'].bits[1:])

    def test_range_validation(self, integer_converter):
        """Тест валидации диапазона"""
        with pytest.raises(ValueError):
            integer_converter.to_direct(2**31)
        with pytest.raises(ValueError):
            integer_converter.to_direct(-2**31 - 1)
    
    def test_conversion_consistency(self, integer_converter):
        """Тест согласованности преобразований"""
        test_values = [-100, -50, -1, 0, 1, 50, 100, 2**31 - 1, -2**31 + 1]
        for value in test_values:
            direct = integer_converter.to_direct(value)
            inverse = integer_converter.to_inverse(value)
            complement = integer_converter.to_complement(value)
            
            if value >= 0:
                # Для положительных чисел все коды одинаковы
                assert direct.bits == inverse.bits == complement.bits
            elif value != -2**31:
                # Для отрицательных чисел прямой и обратный коды различаются
                # (кроме минимального значения, где они совпадают)
                if value != -2**31 + 1:  # Для -2^31+1 они разные
                    assert direct.bits != inverse.bits
    
    def test_property_inverse_complement_relation(self, integer_converter):
        """Тест связи между обратным и дополнительным кодом"""
        # Для обычных отрицательных чисел
        value = -42
        inverse = integer_converter.to_inverse(value)
        complement = integer_converter.to_complement(value)
        
        one = Binary32([0] * 31 + [1])
        result, _ = integer_converter.bit_utils.add_bits(inverse.bits, one.bits)
        assert result == complement.bits
        
        # Для минимального числа
        value = -2**31
        inverse = integer_converter.to_inverse(value)
        complement = integer_converter.to_complement(value)
        assert inverse.bits == complement.bits  # Для -2^31 они совпадают

# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Интеграционные тесты"""
    
    def test_ieee754_and_binary32_integration(self, ieee754_converter):
        """Тест интеграции IEEE754 и Binary32"""
        value = 3.14159
        ieee_bits = ieee754_converter.to_ieee754(value)
        assert isinstance(ieee_bits, Binary32)
        
        back = ieee754_converter.from_ieee754(ieee_bits)
        assert abs(back - value) < 1e-5
    
    def test_all_converters_consistency(self, integer_converter, ieee754_converter):
        """Тест согласованности всех конвертеров"""
        int_values = [0, 1, 42, 100]
        for value in int_values:
            int_bits = integer_converter.to_direct(value)
            float_bits = ieee754_converter.to_ieee754(float(value))
            
            assert isinstance(int_bits, Binary32)
            assert isinstance(float_bits, Binary32)


# ==================== EDGE CASES ====================

class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_binary32_edge_cases(self):
        """Тест граничных случаев Binary32"""
        max_bits = Binary32([1] * 32)
        assert max_bits.to_int() == 2**32 - 1
        
        min_bits = Binary32([0] * 32)
        assert min_bits.to_int() == 0
    
    def test_ieee754_edge_cases(self, ieee754_converter):
        """Тест граничных случаев IEEE754"""
        huge = 1e39
        converted = ieee754_converter.to_ieee754(huge)
        back = ieee754_converter.from_ieee754(converted)
        assert back == float('inf')
    
    def test_integer_converter_edge_cases(self, integer_converter):
        """Тест граничных случаев IntegerConverter"""
        max_pos = 2**31 - 1
        direct = integer_converter.to_direct(max_pos)
        assert integer_converter.from_direct(direct) == max_pos
        
        min_neg = -2**31
        complement = integer_converter.to_complement(min_neg)
        assert integer_converter.from_complement(complement) == min_neg
    
    def test_bit_utils_edge_cases(self, bit_utils):
        """Тест граничных случаев BitUtils"""
        bits = [1, 0, 1]
        assert bit_utils.shift_left(bits, 0) == bits
        assert bit_utils.shift_right_logical(bits, 0) == bits
        assert bit_utils.shift_right_arithmetic(bits, 0) == bits
        
        assert bit_utils.shift_left(bits, 10) == [0, 0, 0]
        assert bit_utils.shift_right_logical(bits, 10) == [0, 0, 0]
# ==================== TESTS FOR GRAY_BCD ====================

class TestGrayBCD:
    """Тесты для Gray BCD"""
    
    @pytest.fixture
    def gray_bcd(self):
        return GrayBCD()
    
    def test_to_gray_bcd_zero(self, gray_bcd):
        """Тест преобразования нуля"""
        result = gray_bcd.to_gray_bcd(0)
        assert len(result.bits) == 32
        assert all(b == 0 for b in result.bits)
    
    def test_to_gray_bcd_single_digit(self, gray_bcd):
        """Тест преобразования однозначных чисел"""
        test_cases = [
            (1, [0,0,0,1]),
            (2, [0,0,1,1]),
            (3, [0,0,1,0]),
            (4, [0,1,1,0]),
            (5, [0,1,1,1]),
            (6, [0,1,0,1]),
            (7, [0,1,0,0]),
            (8, [1,1,0,0]),
            (9, [1,1,0,1]),
        ]
        
        for value, expected_gray in test_cases:
            result = gray_bcd.to_gray_bcd(value)
            # Проверяем последнюю тетраду (младший разряд)
            last_four = result.bits[28:32]
            assert last_four == expected_gray, f"Failed for {value}: got {last_four}, expected {expected_gray}"
    
    def test_to_gray_bcd_multiple_digits(self, gray_bcd):
        """Тест преобразования многозначных чисел"""
        result = gray_bcd.to_gray_bcd(123)
        # Gray BCD: цифры идут от старшего к младшему
        # 1 -> 0001, 2 -> 0011, 3 -> 0010
        # В 32 битах: [0]*20 + [0001][0011][0010]
        expected_pattern = [0,0,0,1, 0,0,1,1, 0,0,1,0]
        # Проверяем последние 12 бит (3 цифры)
        last_12 = result.bits[20:32]
        assert last_12 == expected_pattern, f"Expected {expected_pattern}, got {last_12}"
    
    def test_from_gray_bcd(self, gray_bcd):
        """Тест обратного преобразования"""
        test_cases = [0, 1, 9, 10, 99, 123, 99999999]
        for value in test_cases:
            encoded = gray_bcd.to_gray_bcd(value)
            decoded = gray_bcd.from_gray_bcd(encoded)
            assert decoded == value, f"Failed for {value}: got {decoded}"
    
    def test_negative_value(self, gray_bcd):
        """Тест отрицательного значения"""
        with pytest.raises(ValueError, match="Gray BCD поддерживает только неотрицательные числа"):
            gray_bcd.to_gray_bcd(-1)
    
    def test_add_dec(self, gray_bcd):
        """Тест сложения десятичных чисел через Gray BCD"""
        result_bin, result_dec, overflow = gray_bcd.add_dec(123, 456)
        assert result_dec == 579
        assert overflow == False
        
        result_bin, result_dec, overflow = gray_bcd.add_dec(99999999, 1)
        assert result_dec == 0
        assert overflow == True
    
    def test_gray_to_digits(self, gray_bcd):
        """Тест внутреннего метода преобразования"""
        encoded = gray_bcd.to_gray_bcd(12345)
        digits = gray_bcd._gray_to_digits(encoded)
        # Должно быть 8 цифр: [0,0,0,1,2,3,4,5]
        assert len(digits) == 8
        assert digits[-5:] == [1, 2, 3, 4, 5]  # Последние 5 цифр

# ==================== TESTS FOR COMPLEMENT_ARITHMETIC ====================

class TestComplementArithmetic:
    """Тесты для арифметики в дополнительном коде"""
    
    @pytest.fixture
    def comp_arith(self):
        from src.arithmetic.complement_arithmetic import ComplementArithmetic
        return ComplementArithmetic()
    
    def test_add_positive_numbers(self, comp_arith):
        """Тест сложения положительных чисел"""
        test_cases = [(5, 3, 8), (0, 0, 0), (100, 200, 300)]
        for a, b, expected in test_cases:
            result_bin, overflow = comp_arith.add(
                comp_arith.converter.to_complement(a),
                comp_arith.converter.to_complement(b)
            )
            result = comp_arith.converter.from_complement(result_bin)
            assert result == expected
            assert overflow == False
    
    def test_add_negative_numbers(self, comp_arith):
        """Тест сложения отрицательных чисел"""
        test_cases = [(-5, -3, -8), (-100, -200, -300)]
        for a, b, expected in test_cases:
            result_bin, overflow = comp_arith.add(
                comp_arith.converter.to_complement(a),
                comp_arith.converter.to_complement(b)
            )
            result = comp_arith.converter.from_complement(result_bin)
            assert result == expected
            assert overflow == False
    
    def test_add_mixed_signs(self, comp_arith):
        """Тест сложения чисел с разными знаками"""
        test_cases = [(5, -3, 2), (-5, 3, -2), (10, -10, 0)]
        for a, b, expected in test_cases:
            result_bin, overflow = comp_arith.add(
                comp_arith.converter.to_complement(a),
                comp_arith.converter.to_complement(b)
            )
            result = comp_arith.converter.from_complement(result_bin)
            assert result == expected
            assert overflow == False
    
    def test_add_overflow(self, comp_arith):
        """Тест переполнения при сложении"""
        max_val = 2**31 - 1
        # Положительное переполнение
        result_bin, overflow = comp_arith.add(
            comp_arith.converter.to_complement(max_val),
            comp_arith.converter.to_complement(1)
        )
        assert overflow == True
        
        # Отрицательное переполнение
        min_val = -2**31
        result_bin, overflow = comp_arith.add(
            comp_arith.converter.to_complement(min_val),
            comp_arith.converter.to_complement(-1)
        )
        assert overflow == True
    
    def test_negate(self, comp_arith):
        """Тест получения отрицательного числа"""
        test_cases = [5, -5, 0, 100, -100]
        for value in test_cases:
            original = comp_arith.converter.to_complement(value)
            negated = comp_arith.negate(original)
            result = comp_arith.converter.from_complement(negated)
            assert result == -value
    
    def test_subtract(self, comp_arith):
        """Тест вычитания"""
        test_cases = [(10, 3, 7), (5, 10, -5), (0, 5, -5), (-5, -3, -2)]
        for a, b, expected in test_cases:
            result_bin, overflow = comp_arith.subtract(
                comp_arith.converter.to_complement(a),
                comp_arith.converter.to_complement(b)
            )
            result = comp_arith.converter.from_complement(result_bin)
            assert result == expected
            assert overflow == False
    
    def test_add_dec(self, comp_arith):
        """Тест сложения десятичных чисел"""
        result_bin, result_dec, overflow = comp_arith.add_dec(10, 20)
        assert result_dec == 30
        assert overflow == False
        
        result_bin, result_dec, overflow = comp_arith.add_dec(2**31 - 1, 1)
        assert overflow == True
    
    def test_subtract_dec(self, comp_arith):
        """Тест вычитания десятичных чисел"""
        result_bin, result_dec, overflow = comp_arith.subtract_dec(20, 10)
        assert result_dec == 10
        assert overflow == False
        
        result_bin, result_dec, overflow = comp_arith.subtract_dec(10, 20)
        assert result_dec == -10


# ==================== TESTS FOR DIRECT_ARITHMETIC ====================

class TestDirectArithmetic:
    """Тесты для арифметики в прямом коде"""
    
    @pytest.fixture
    def direct_arith(self):
        from src.arithmetic.direct_arithmetic import DirectArithmetic
        return DirectArithmetic()
    
    def test_multiply_positive(self, direct_arith):
        """Тест умножения положительных чисел"""
        test_cases = [(5, 3, 15), (0, 10, 0), (100, 200, 20000)]
        for a, b, expected in test_cases:
            result_bin, overflow = direct_arith.multiply(
                direct_arith.converter.to_direct(a),
                direct_arith.converter.to_direct(b)
            )
            result = direct_arith.converter.from_direct(result_bin)
            assert result == expected
            assert overflow == False
    
    def test_multiply_negative(self, direct_arith):
        """Тест умножения отрицательных чисел"""
        test_cases = [(-5, 3, -15), (5, -3, -15), (-5, -3, 15)]
        for a, b, expected in test_cases:
            result_bin, overflow = direct_arith.multiply(
                direct_arith.converter.to_direct(a),
                direct_arith.converter.to_direct(b)
            )
            result = direct_arith.converter.from_direct(result_bin)
            assert result == expected
            assert overflow == False
    
    def test_multiply_overflow(self, direct_arith):
        """Тест переполнения при умножении"""
        max_val = 2**31 - 1
        result_bin, overflow = direct_arith.multiply(
            direct_arith.converter.to_direct(max_val),
            direct_arith.converter.to_direct(2)
        )
        assert overflow == True
    
    def test_divide_positive(self, direct_arith):
        """Тест деления положительных чисел"""
        test_cases = [(10, 2, 5.0), (7, 2, 3.5), (1, 2, 0.5)]
        for dividend, divisor, expected in test_cases:
            result_bin, overflow = direct_arith.divide(
                direct_arith.converter.to_direct(dividend),
                direct_arith.converter.to_direct(divisor)
            )
            # Проверяем результат через десятичное представление
            sign = result_bin.bits[0]
            magnitude_bits = result_bin.bits[1:]
            
            integer_bits = magnitude_bits[:direct_arith.INTEGER_BITS]
            integer_part = 0
            for bit in integer_bits:
                integer_part = integer_part * 2 + bit
            
            fractional_bits = magnitude_bits[direct_arith.INTEGER_BITS:direct_arith.INTEGER_BITS + direct_arith.FRACTIONAL_BITS]
            fractional_part = 0.0
            power = 0.5
            for bit in fractional_bits:
                if bit == 1:
                    fractional_part = fractional_part + power
                power = power / 2.0
            
            result = integer_part + fractional_part
            if sign == 1:
                result = -result
            
            assert abs(result - expected) < 0.0001
            assert overflow == False
    
    def test_divide_negative(self, direct_arith):
        """Тест деления отрицательных чисел"""
        test_cases = [(-10, 2, -5.0), (10, -2, -5.0), (-10, -2, 5.0)]
        for dividend, divisor, expected in test_cases:
            result_bin, overflow = direct_arith.divide(
                direct_arith.converter.to_direct(dividend),
                direct_arith.converter.to_direct(divisor)
            )
            # Проверяем знак
            sign = result_bin.bits[0]
            expected_sign = 1 if expected < 0 else 0
            assert sign == expected_sign
    
    def test_divide_by_zero(self, direct_arith):
        """Тест деления на ноль"""
        with pytest.raises(ValueError, match="Деление на ноль"):
            direct_arith.divide(
                direct_arith.converter.to_direct(10),
                direct_arith.converter.to_direct(0)
            )
    
    def test_multiply_dec(self, direct_arith):
        """Тест умножения десятичных чисел"""
        result_bin, result_dec, overflow = direct_arith.multiply_dec(10, 20)
        assert result_dec == 200
        assert overflow == False
    
    def test_divide_dec(self, direct_arith):
        """Тест деления десятичных чисел"""
        result_bin, result_dec, overflow = direct_arith.divide_dec(10, 2)
        assert abs(result_dec - 5.0) < 0.0001
        assert overflow == False
        
        result_bin, result_dec, overflow = direct_arith.divide_dec(7, 2)
        assert abs(result_dec - 3.5) < 0.0001
    
    def test_int_to_bits(self, direct_arith):
        """Тест внутреннего метода преобразования"""
        bits = direct_arith._int_to_bits(5, 4)
        assert bits == [0, 1, 0, 1]
        
        bits = direct_arith._int_to_bits(0, 8)
        assert bits == [0] * 8
    
    def test_bits_to_int(self, direct_arith):
        """Тест внутреннего метода обратного преобразования"""
        value = direct_arith._bits_to_int([0, 1, 0, 1])
        assert value == 5


# ==================== TESTS FOR IEEE754_ARITHMETIC ====================

class TestIeee754Arithmetic:
    """Тесты для арифметики IEEE-754"""
    
    @pytest.fixture
    def ieee_arith(self):
        return Ieee754Arithmetic()
    
    def test_add_positive_numbers(self, ieee_arith):
        """Тест сложения положительных чисел"""
        test_cases = [
            (1.0, 2.0, 3.0),
            (0.1, 0.2, 0.3),
            (1.5, 2.5, 4.0),
            (0.001, 0.002, 0.003)
        ]
        for a, b, expected in test_cases:
            result_bin, result_dec, flags = ieee_arith.add_dec(a, b)
            assert abs(result_dec - expected) < 0.001, f"Failed for {a} + {b} = {result_dec}, expected {expected}"
            assert flags == ieee_arith.FLAG_NONE or flags == ieee_arith.FLAG_INEXACT
    
    def test_add_negative_numbers(self, ieee_arith):
        """Тест сложения отрицательных чисел"""
        test_cases = [(-1.0, -2.0, -3.0), (-0.5, -0.5, -1.0), (-0.1, -0.2, -0.3)]
        for a, b, expected in test_cases:
            result_bin, result_dec, flags = ieee_arith.add_dec(a, b)
            assert abs(result_dec - expected) < 0.001
    
    def test_add_mixed_signs(self, ieee_arith):
        """Тест сложения чисел с разными знаками"""
        test_cases = [(5.0, -3.0, 2.0), (-5.0, 3.0, -2.0), (1.0, -1.0, 0.0)]
        for a, b, expected in test_cases:
            result_bin, result_dec, flags = ieee_arith.add_dec(a, b)
            assert abs(result_dec - expected) < 0.001
    
    def test_add_infinity(self, ieee_arith):
        """Тест сложения с бесконечностью"""
        result_bin, result_dec, flags = ieee_arith.add_dec(float('inf'), 1.0)
        assert result_dec == float('inf')
        
        result_bin, result_dec, flags = ieee_arith.add_dec(float('-inf'), 1.0)
        assert result_dec == float('-inf')
        
        result_bin, result_dec, flags = ieee_arith.add_dec(float('inf'), float('-inf'))
        assert str(result_dec) == 'nan'
        assert flags == ieee_arith.FLAG_INVALID
    
    def test_add_nan(self, ieee_arith):
        """Тест сложения с NaN"""
        result_bin, result_dec, flags = ieee_arith.add_dec(float('nan'), 1.0)
        assert str(result_dec) == 'nan'
        assert flags == ieee_arith.FLAG_INVALID
    
    def test_subtract_dec(self, ieee_arith):
        """Тест вычитания"""
        test_cases = [(10.0, 3.0, 7.0), (5.0, 10.0, -5.0), (2.5, 1.5, 1.0)]
        for a, b, expected in test_cases:
            result_bin, result_dec, flags = ieee_arith.subtract_dec(a, b)
            assert abs(result_dec - expected) < 0.001
    
    def test_multiply_dec(self, ieee_arith):
        """Тест умножения"""
        test_cases = [(2.0, 3.0, 6.0), (-2.0, 3.0, -6.0), (2.5, 2.0, 5.0), (0.5, 0.5, 0.25)]
        for a, b, expected in test_cases:
            result_bin, result_dec, flags = ieee_arith.multiply_dec(a, b)
            assert abs(result_dec - expected) < 0.001
    
    def test_multiply_infinity(self, ieee_arith):
        """Тест умножения с бесконечностью"""
        result_bin, result_dec, flags = ieee_arith.multiply_dec(float('inf'), 2.0)
        assert result_dec == float('inf')
        
        result_bin, result_dec, flags = ieee_arith.multiply_dec(float('inf'), 0.0)
        assert str(result_dec) == 'nan'
        assert flags == ieee_arith.FLAG_INVALID
    
    def test_divide_dec(self, ieee_arith):
        """Тест деления"""
        test_cases = [(10.0, 2.0, 5.0), (7.0, 2.0, 3.5), (1.0, 2.0, 0.5)]
        for a, b, expected in test_cases:
            result_bin, result_dec, flags = ieee_arith.divide_dec(a, b)
            assert abs(result_dec - expected) < 0.001
    
    def test_divide_by_zero(self, ieee_arith):
        """Тест деления на ноль"""
        with pytest.raises(ValueError, match="Деление на ноль"):
            ieee_arith.divide_dec(10.0, 0.0)

    def test_is_nan_infinity_methods(self, ieee_arith):
        """Тест внутренних методов проверки NaN и Infinity"""
        nan_bin = ieee_arith.converter._get_nan()
        assert ieee_arith._is_nan(nan_bin) == True
        assert ieee_arith._is_infinity(nan_bin) == False
        
        inf_bin = ieee_arith._get_infinity(0)
        assert ieee_arith._is_nan(inf_bin) == False
        assert ieee_arith._is_infinity(inf_bin) == True

# ==================== INTEGRATION TESTS FOR ALL MODULES ====================

class TestAllModulesIntegration:
    """Интеграционные тесты для всех модулей"""
    
    def test_complement_and_direct_consistency(self):
        """Тест согласованности дополнительного и прямого кода"""
        comp_arith = ComplementArithmetic()
        direct_arith = DirectArithmetic()
        
        # Проверяем, что сложение через дополнительный код дает тот же результат
        for a, b in [(5, 3), (10, -4), (-7, -2)]:
            comp_result, comp_dec, _ = comp_arith.add_dec(a, b)
            assert comp_dec == a + b
    
    def test_ieee754_and_binary32_integration(self):
        """Тест интеграции IEEE754 и Binary32"""
        ieee_arith = Ieee754Arithmetic()
        
        # Проверяем, что результат операции - это Binary32
        result_bin, result_dec, flags = ieee_arith.add_dec(1.5, 2.5)
        assert isinstance(result_bin, Binary32)
        assert isinstance(result_dec, float)
        assert isinstance(flags, int)
        assert abs(result_dec - 4.0) < 0.001
    
    def test_gray_bcd_and_binary32_integration(self):
        """Тест интеграции Gray BCD и Binary32"""
        gray_bcd = GrayBCD()
        
        # Проверяем, что результат - Binary32
        result_bin = gray_bcd.to_gray_bcd(123)
        assert isinstance(result_bin, Binary32)
        
        decoded = gray_bcd.from_gray_bcd(result_bin)
        assert decoded == 123
    
    def test_all_arithmetic_operations_consistency(self):
        """Тест согласованности всех арифметических операций"""
        comp_arith = ComplementArithmetic()
        ieee_arith = Ieee754Arithmetic()
        
        # Для целых чисел результаты должны совпадать
        a, b = 10, 3
        
        comp_result, comp_dec, _ = comp_arith.add_dec(a, b)
        ieee_result, ieee_dec, _ = ieee_arith.add_dec(float(a), float(b))
        
        assert comp_dec == a + b
        assert abs(ieee_dec - (a + b)) < 0.001

# ==================== MAIN ====================

if __name__ == "__main__":
    pytest.main([
        __file__,
        '-v',
        '--cov=src',
        '--cov-report=term-missing',
        '--cov-report=html'
    ])
