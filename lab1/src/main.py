"""
Главный модуль для выполнения всех операций:
- Преобразование чисел в прямой, обратный и дополнительный коды
- Арифметика в дополнительном коде (сложение, вычитание)
- Арифметика в прямом коде (умножение, деление)
- Арифметика IEEE-754 (сложение, вычитание, умножение, деление)
- Арифметика Gray BCD (сложение)
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.converters.integer_converter import IntegerConverter
from src.converters.ieee754_converter import Ieee754Converter
from src.bcd.gray_bcd import GrayBCD
from src.arithmetic.complement_arithmetic import ComplementArithmetic
from src.arithmetic.direct_arithmetic import DirectArithmetic
from src.arithmetic.ieee754_arithmetic import Ieee754Arithmetic


def print_separator(char="=", length=80):
    """Печать разделителя"""
    print(char * length)


def print_header(text):
    """Печать заголовка"""
    print_separator()
    print(f" {text}")
    print_separator()


def print_binary_grouped(bits, group_size=4):
    """Печать битов с группировкой"""
    bits_str = ''.join(str(b) for b in bits)
    groups = [bits_str[i:i+group_size] for i in range(0, len(bits_str), group_size)]
    return ' '.join(groups)


def get_int_input(prompt):
    """Получение целого числа с обработкой ошибок"""
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Ошибка: Введите целое число!")


def get_float_input(prompt):
    """Получение числа с плавающей точкой с обработкой ошибок"""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Ошибка: Введите число!")


def task1_number_conversion():
    """Задание 1: Перевод числа в прямой, обратный и дополнительный коды"""
    print_header("ЗАДАНИЕ 1: ПЕРЕВОД ЧИСЛА В РАЗЛИЧНЫЕ КОДЫ")
    
    converter = IntegerConverter()
    
    while True:
        print("\n" + "-" * 60)
        value = get_int_input("Введите целое число (0 для выхода из задания): ")
        
        if value == 0:
            print("Возврат в главное меню...")
            break
        
        try:
            # Получаем все коды
            codes = converter.to_all_codes(value)
            
            print(f"\nИсходное число: {value}")
            print_separator("-")
            
            # Прямой код
            print(f"\nПРЯМОЙ КОД:")
            print(f"   {codes['direct']}")
            
            # Обратный код
            print(f"\nОБРАТНЫЙ КОД:")
            print(f"   {codes['inverse']}")
            
            # Дополнительный код
            print(f"\nДОПОЛНИТЕЛЬНЫЙ КОД:")
            print(f"   {codes['complement']}")
            
            # Проверка обратного преобразования
            print(f"\nПРОВЕРКА:")
            check_direct = converter.from_direct(codes['direct'])
            check_inverse = converter.from_inverse(codes['inverse'])
            check_complement = converter.from_complement(codes['complement'])
            print(f"   Из прямого кода: {check_direct}")
            print(f"   Из обратного кода: {check_inverse}")
            print(f"   Из дополнительного кода: {check_complement}")
            
        except ValueError as e:
            print(f"Ошибка: {e}")
        
        print_separator()



def task2_complement_addition():
    """Задание 2: Сложение в дополнительном коде"""
    print_header("ЗАДАНИЕ 2: СЛОЖЕНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ")
    
    comp_arith = ComplementArithmetic()
    converter = IntegerConverter()
    
    while True:
        print("\n" + "-" * 60)
        a = get_int_input("Введите первое число (0 для выхода): ")
        
        if a == 0:
            print("Возврат в главное меню...")
            break
            
        b = get_int_input("Введите второе число: ")
        
        print(f"\nИсходные числа: {a} и {b}")
        print_separator("-")
        
        # Получаем дополнительные коды
        print(f"\nПРЕДСТАВЛЕНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ:")
        a_comp = converter.to_complement(a)
        b_comp = converter.to_complement(b)
        print(f"   {a} → {a_comp}")
        print(f"   {b} → {b_comp}")
        
        # Выполняем сложение
        print(f"\nСЛОЖЕНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ:")
        result_bin, overflow = comp_arith.add(a_comp, b_comp)
        result_dec = converter.from_complement(result_bin)
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"   Двоичный (доп. код): {result_bin}")
        print(f"   Десятичный: {result_dec}")
        print(f"   Ожидаемый: {a + b}")
        
        if overflow:
            print(f"\n   ⚠ ВНИМАНИЕ: ОБНАРУЖЕНО ПЕРЕПОЛНЕНИЕ!")
        
        print_separator()

def task3_complement_subtraction():
    """Задание 3: Вычитание в дополнительном коде"""
    print_header("ЗАДАНИЕ 3: ВЫЧИТАНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ")
    
    comp_arith = ComplementArithmetic()
    converter = IntegerConverter()
    
    while True:
        print("\n" + "-" * 60)
        a = get_int_input("Введите уменьшаемое (0 для выхода): ")
        
        if a == 0:
            print("Возврат в главное меню...")
            break
            
        b = get_int_input("Введите вычитаемое: ")
        
        print(f"\nИсходные числа: {a} - {b}")
        print_separator("-")
        
        # Получаем дополнительные коды
        print(f"\nПРЕДСТАВЛЕНИЕ В ДОПОЛНИТЕЛЬНОМ КОДЕ:")
        a_comp = converter.to_complement(a)
        b_comp = converter.to_complement(b)
        print(f"   {a} → {a_comp}")
        print(f"   {b} → {b_comp}")
        
        # Выполняем вычитание
        result_bin, overflow = comp_arith.subtract(a_comp, b_comp)
        result_dec = converter.from_complement(result_bin)
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"   Двоичный (доп. код): {result_bin}")
        print(f"   Десятичный: {result_dec}")
        print(f"   Ожидаемый: {a - b}")
        
        if overflow:
            print(f"\n   ⚠ ВНИМАНИЕ: ОБНАРУЖЕНО ПЕРЕПОЛНЕНИЕ!")
        
        print_separator()


def task4_direct_multiplication():
    """Задание 4: Умножение в прямом коде"""
    print_header("ЗАДАНИЕ 4: УМНОЖЕНИЕ В ПРЯМОМ КОДЕ")
    
    direct_arith = DirectArithmetic()
    converter = IntegerConverter()
    
    while True:
        print("\n" + "-" * 60)
        a = get_int_input("Введите первое число (0 для выхода): ")
        
        if a == 0:
            print("Возврат в главное меню...")
            break
            
        b = get_int_input("Введите второе число: ")
        
        print(f"\nИсходные числа: {a} × {b}")
        print_separator("-")
        
        # Получаем прямые коды
        print(f"\nПРЕДСТАВЛЕНИЕ В ПРЯМОМ КОДЕ:")
        a_direct = converter.to_direct(a)
        b_direct = converter.to_direct(b)
        print(f"   {a} → {a_direct}")
        print(f"   {b} → {b_direct}")
        
        # Выполняем умножение
        result_bin, overflow = direct_arith.multiply(a_direct, b_direct)
        result_dec = converter.from_direct(result_bin)
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"   Двоичный (прямой код): {result_bin}")
        print(f"   Десятичный: {result_dec}")
        print(f"   Ожидаемый: {a * b}")
        
        if overflow:
            print(f"\n   ⚠ ВНИМАНИЕ: ОБНАРУЖЕНО ПЕРЕПОЛНЕНИЕ!")
        
        print_separator()


def task5_direct_division():
    """Задание 5: Деление в прямом коде с точностью до 5 знаков"""
    print_header("ЗАДАНИЕ 5: ДЕЛЕНИЕ В ПРЯМОМ КОДЕ (16.16 FIXED-POINT)")
    
    direct_arith = DirectArithmetic()
    converter = IntegerConverter()
    
    while True:
        print("\n" + "-" * 60)
        a = get_int_input("Введите делимое (0 для выхода): ")
        
        if a == 0:
            print("Возврат в главное меню...")
            break
            
        b = get_int_input("Введите делитель: ")
        
        if b == 0:
            print("Ошибка: Деление на ноль!")
            continue
        
        print(f"\nИсходные числа: {a} / {b}")
        print_separator("-")
        
        # Получаем прямые коды
        print(f"\nПРЕДСТАВЛЕНИЕ В ПРЯМОМ КОДЕ:")
        a_direct = converter.to_direct(a)
        b_direct = converter.to_direct(b)
        print(f"   {a} → {a_direct}")
        print(f"   {b} → {b_direct}")
        
        # Выполняем деление с fixed-point
        result_bin, overflow = direct_arith.divide(a_direct, b_direct)
        
        # Извлекаем результат из fixed-point
        magnitude_bits = result_bin.bits[1:]
        integer_bits = magnitude_bits[:16]
        fractional_bits = magnitude_bits[16:32]
        
        integer_part = 0
        for bit in integer_bits:
            integer_part = integer_part * 2 + bit
        
        fractional_part = 0.0
        power = 0.5
        for bit in fractional_bits:
            if bit == 1:
                fractional_part += power
            power /= 2.0
        
        sign = result_bin.bits[0]
        result = integer_part + fractional_part
        if sign == 1:
            result = -result
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"   Двоичный (прямой код 16.16): {result_bin}")
        print(f"   Десятичный: {result:.5f}")
        print(f"   Ожидаемый: {a / b:.5f}")
        
        if overflow:
            print(f"\n   ⚠ ВНИМАНИЕ: ПЕРЕПОЛНЕНИЕ ЦЕЛОЙ ЧАСТИ!")
        
        print_separator()


def task6_ieee754_arithmetic():
    """Задание 6: Арифметика IEEE-754"""
    print_header("ЗАДАНИЕ 6: АРИФМЕТИКА IEEE-754 (32 БИТА)")
    
    ieee_arith = Ieee754Arithmetic()
    converter = Ieee754Converter()
    
    while True:
        print("\n" + "-" * 60)
        print("Выберите операцию:")
        print("  1. Сложение (a + b)")
        print("  2. Вычитание (a - b)")
        print("  3. Умножение (a × b)")
        print("  4. Деление (a / b)")
        print("  5. Выход из задания")
        
        op_choice = input("\nВаш выбор (1-5): ")
        
        if op_choice == '5':
            break
        
        if op_choice not in ['1', '2', '3', '4']:
            print("Неверный выбор!")
            continue
        
        a = get_float_input("Введите первое число: ")
        b = get_float_input("Введите второе число: ")
        
        if op_choice == '4' and b == 0.0:
            print("Ошибка: Деление на ноль!")
            continue
        
        print(f"\nИсходные числа: {a} и {b}")
        print_separator("-")
        
        # Получаем IEEE-754 представления
        print(f"\nПРЕДСТАВЛЕНИЕ В IEEE-754:")
        a_bin = converter.to_ieee754(a)
        b_bin = converter.to_ieee754(b)
        print(f"   {a} → {a_bin}")
        print(f"   {b} → {b_bin}")
        
        # Выполняем операцию
        if op_choice == '1':
            result_bin, result_dec, flags = ieee_arith.add_dec(a, b)
            expected = a + b
            op_name = "Сложение"
        elif op_choice == '2':
            result_bin, result_dec, flags = ieee_arith.subtract_dec(a, b)
            expected = a - b
            op_name = "Вычитание"
        elif op_choice == '3':
            result_bin, result_dec, flags = ieee_arith.multiply_dec(a, b)
            expected = a * b
            op_name = "Умножение"
        else:
            result_bin, result_dec, flags = ieee_arith.divide_dec(a, b)
            expected = a / b
            op_name = "Деление"
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"   Двоичный (IEEE-754): {result_bin}")
        print(f"   Десятичный: {result_dec}")
        print(f"   Ожидаемый: {expected}")
        
        print_separator()

def task7_gray_bcd_addition():
    """Задание 7: Сложение в Gray BCD"""
    print_header("ЗАДАНИЕ 7: СЛОЖЕНИЕ В GRAY BCD")
    
    gray_bcd = GrayBCD()
    
    while True:
        print("\n" + "-" * 60)
        print("Диапазон чисел: 0 - 99,999,999 (8 десятичных цифр)")
        a = get_int_input("Введите первое число (0 для выхода): ")
        
        if a == 0:
            print("Возврат в главное меню...")
            break
            
        b = get_int_input("Введите второе число: ")
        
        if a < 0 or a > 99999999 or b < 0 or b > 99999999:
            print("Ошибка: Числа должны быть в диапазоне 0-99999999!")
            continue
        
        print(f"\nИсходные числа: {a} и {b}")
        print_separator("-")
        
        # Получаем Gray BCD представления
        print(f"\n1. ПРЕДСТАВЛЕНИЕ В GRAY BCD:")
        a_bin = gray_bcd.to_gray_bcd(a)
        b_bin = gray_bcd.to_gray_bcd(b)
        print(f"   {a} → {a_bin}")
        print(f"   {b} → {b_bin}")
        
        # Разбор на цифры
        print(f"\n2. РАЗБОР НА ДЕСЯТИЧНЫЕ ЦИФРЫ:")
        a_digits = gray_bcd._gray_to_digits(a_bin)
        b_digits = gray_bcd._gray_to_digits(b_bin)
        print(f"   Цифры {a}: {a_digits}")
        print(f"   Цифры {b}: {b_digits}")
        
        # Сложение
        print(f"\n3. ПОРАЗРЯДНОЕ СЛОЖЕНИЕ С ПЕРЕНОСОМ:")
        print("   Разряд | Цифра a | Цифра b | Перенос | Сумма | Результат | Новый перенос")
        print("   " + "-" * 65)
        
        result_bin, overflow = gray_bcd.add(a_bin, b_bin)
        result = gray_bcd.from_gray_bcd(result_bin)
        
        # Показываем поразрядно
        carry = 0
        for i in range(7, -1, -1):
            total = a_digits[i] + b_digits[i] + carry
            if total >= 10:
                digit = total - 10
                new_carry = 1
            else:
                digit = total
                new_carry = 0
            
            # Форматируем строку
            carry_str = str(carry) if i < 7 else "0"
            print(f"   {i+1:2d}      | {a_digits[i]:8d} | {b_digits[i]:8d} | {carry_str:7s} | {total:4d} | {digit:8d} | {new_carry:10d}")
            carry = new_carry
        
        print(f"\n4. РЕЗУЛЬТАТ:")
        print(f"   Двоичный (Gray BCD): {result_bin}")
        print(f"   Десятичный: {result}")
        print(f"   Ожидаемый: {a + b}")
        
        if overflow:
            print(f"\n   ⚠ ПЕРЕПОЛНЕНИЕ! Результат превышает 8 десятичных цифр")
            print(f"   Результат обнулен (0)")
        
        print_separator()




def main():
    """Главное меню"""
    print_header("ЛАБОРАТОРНАЯ РАБОТА №1")
    print("Представление чисел и арифметика в компьютере")
    print("\nВыполненные операции:")
    print("  1. Перевод числа в прямой, обратный и дополнительный коды")
    print("  2. Сложение в дополнительном коде")
    print("  3. Вычитание в дополнительном коде (a - b = a + (-b))")
    print("  4. Умножение в прямом коде")
    print("  5. Деление в прямом коде (точность 5 знаков, формат 16.16)")
    print("  6. Арифметика IEEE-754 (сложение, вычитание, умножение, деление)")
    print("  7. Сложение в Gray BCD")
    
    while True:
        print("\n" + "=" * 80)
        print("\nГЛАВНОЕ МЕНЮ:")
        print("  1. Перевод числа в коды (прямой, обратный, дополнительный)")
        print("  2. Сложение в дополнительном коде")
        print("  3. Вычитание в дополнительном коде")
        print("  4. Умножение в прямом коде")
        print("  5. Деление в прямом коде (с точностью до 5 знаков)")
        print("  6. Арифметика IEEE-754")
        print("  7. Сложение в Gray BCD")
        print("  0. Выход")
        
        choice = input("\nВаш выбор (0-7): ")
        
        if choice == '0':
            print("\nДо свидания!")
            break
        elif choice == '1':
            task1_number_conversion()
        elif choice == '2':
            task2_complement_addition()
        elif choice == '3':
            task3_complement_subtraction()
        elif choice == '4':
            task4_direct_multiplication()
        elif choice == '5':
            task5_direct_division()
        elif choice == '6':
            task6_ieee754_arithmetic()
        elif choice == '7':
            task7_gray_bcd_addition()
        else:
            print("Неверный выбор! Попробуйте снова.")


if __name__ == "__main__":
    main()