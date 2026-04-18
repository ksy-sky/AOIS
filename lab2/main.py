from src.parser import ExpressionParser, ParserError
from src.truth_table import TruthTable
from src.forms import NormalFormBuilder
from src.post_classes import PostClassesChecker
from src.zhegalkin import ZhegalkinPolynomial
from src.variables import FictitiousVariablesFinder
from src.derivatives import BooleanDerivative
from src.minimization import MinimizationCalculator
import sys


def get_variables_from_expression(expression: str) -> list:
    """Автоматическое определение переменных a-e"""
    variables = set()
    for char in expression:
        if char in 'abcde':
            variables.add(char)
    return sorted(variables)


def print_section(title: str) -> None:
    print(f" {title} ".center(70, "="))


def main():
    print("=" * 70)
    print(" ЛАБОРАТОРНАЯ РАБОТА 2: ЛОГИЧЕСКИЕ ФУНКЦИИ ".center(70, "="))
    print("=" * 70)

    expression_str = input("\nВведите логическую функцию: ").strip()

    try:
        parser = ExpressionParser(expression_str)
        expression = parser.parse()
        print("\n✓ Функция успешно распарсена")
    except ParserError as e:
        print(f"\n✗ Ошибка парсинга: {e}")
        return

    variables = get_variables_from_expression(expression_str)
    if not variables:
        print("\n✗ Не найдено переменных (a, b, c, d, e)")
        return

    print(f"Обнаруженные переменные: {', '.join(variables)}")

    # === ТАБЛИЦА ИСТИННОСТИ ===
    truth_table = TruthTable(expression, variables)
    truth_table.build()

    print_section("ТАБЛИЦА ИСТИННОСТИ")
    print(truth_table.print_table())

    # === НОРМАЛЬНЫЕ ФОРМЫ ===
    builder = NormalFormBuilder(truth_table)

    print_section("СДНФ И СКНФ")
    print(f"СДНФ: {builder.build_sdnf()}")
    print(f"Числовая форма СДНФ: {builder.get_sdnf_numeric()}")
    print(f"\nСКНФ: {builder.build_sknf()}")
    print(f"Числовая форма СКНФ: {builder.get_sknf_numeric()}")
    print(f"\n{builder.get_index_form()}")

    # === КЛАССЫ ПОСТА ===
    print_section("КЛАССЫ ПОСТА")
    checker = PostClassesChecker(truth_table)
    classes = checker.get_all_classes()
    for name, value in classes.items():
        status = "✓" if value else "✗"
        print(f"{status} {name}")

    # === ПОЛИНОМ ЖЕГАЛКИНА ===
    print_section("ПОЛИНОМ ЖЕГАЛКИНА")
    zhegalkin = ZhegalkinPolynomial(truth_table)
    zhegalkin.build()
    print(f"Полином Жегалкина: {zhegalkin.to_string()}")
    print(f"Линейная функция: {zhegalkin.is_linear()}")

    # === ФИКТИВНЫЕ ПЕРЕМЕННЫЕ ===
    print_section("ФИКТИВНЫЕ И СУЩЕСТВЕННЫЕ ПЕРЕМЕННЫЕ")
    finder = FictitiousVariablesFinder(truth_table)
    fictitious = finder.find_fictitious()
    essential = finder.get_essential_variables()
    print(f"Фиктивные переменные: {fictitious if fictitious else 'нет'}")
    print(f"Существенные переменные: {essential}")

    # === БУЛЕВЫ ПРОИЗВОДНЫЕ ===
    print_section("БУЛЕВЫ ПРОИЗВОДНЫЕ")
    derivative = BooleanDerivative(expression, variables)

    print("Частные производные:")
    for var in variables:
        print(f"   ∂f/∂{var} = {derivative.partial_derivative(var)}")

    if len(variables) >= 2:
        print("\nСмешанные производные 2-го порядка:")
        from itertools import combinations
        for var1, var2 in combinations(variables, 2):
            result = derivative.mixed_derivative([var1, var2])
            print(f"   ∂²f/∂{var1}∂{var2} = {result}")

    if len(variables) >= 3:
        print("\nСмешанные производные 3-го порядка:")
        from itertools import combinations
        for var1, var2, var3 in combinations(variables, 3):
            result = derivative.mixed_derivative([var1, var2, var3])
            print(f"   ∂³f/∂{var1}∂{var2}∂{var3} = {result}")

    if len(variables) >= 4:
        print("\nСмешанные производные 4-го порядка:")
        from itertools import combinations
        for vars_tuple in combinations(variables, 4):
            result = derivative.mixed_derivative(list(vars_tuple))
            print(f"   ∂⁴f/∂{vars_tuple[0]}∂{vars_tuple[1]}∂{vars_tuple[2]}∂{vars_tuple[3]} = {result}")

    # === МИНИМИЗАЦИЯ ===
    minimizer = MinimizationCalculator(truth_table)
    
    # ДНФ - Расчётный метод
    print_section("МИНИМИЗАЦИЯ ДНФ: РАСЧЁТНЫЙ МЕТОД")
    stages, result_terms = minimizer.minimize_calculation_method_dnf()
    for i, stage in enumerate(stages, 1):
        print(f"{stage}\n")
    print(f"Минимизированная ДНФ: {minimizer.get_minimized_dnf_expression(result_terms)}")
    
    # ДНФ - Расчётно-табличный метод
    print_section("МИНИМИЗАЦИЯ ДНФ: РАСЧЁТНО-ТАБЛИЧНЫЙ МЕТОД")
    stages, result_terms, coverage_table = minimizer.minimize_table_method_dnf()
    print(coverage_table)
    print(f"\nМинимизированная ДНФ: {minimizer.get_minimized_dnf_expression(result_terms)}")
    
    # ДНФ - Карта Карно
    print_section("МИНИМИЗАЦИЯ ДНФ: КАРТА КАРНО")
    karnaugh_terms, karnaugh_viz = minimizer.minimize_karnaugh_dnf()
    print(karnaugh_viz)
    print(f"\nМинимизированная ДНФ: {minimizer.get_minimized_dnf_expression(karnaugh_terms)}")
    
    # === МИНИМИЗАЦИЯ КНФ ===
    
    # КНФ - Расчётный метод
    print_section("МИНИМИЗАЦИЯ КНФ: РАСЧЁТНЫЙ МЕТОД")
    cnf_terms = minimizer.get_sknf_terms()
    
    cnf_stages, cnf_result_terms = minimizer.minimize_calculation_method_cnf()
    for i, stage in enumerate(cnf_stages, 1):
        print(f"\n{stage}")
    print(f"\nМинимизированная КНФ: {minimizer.get_minimized_cnf_expression(cnf_result_terms)}")
    
    # КНФ - Расчётно-табличный метод
    print_section("МИНИМИЗАЦИЯ КНФ: РАСЧЁТНО-ТАБЛИЧНЫЙ МЕТОД")
    cnf_stages, cnf_result_terms, cnf_coverage_table = minimizer.minimize_table_method_cnf()
    print(cnf_coverage_table)
    print(f"\nМинимизированная КНФ: {minimizer.get_minimized_cnf_expression(cnf_result_terms)}")
    
    # КНФ - Карта Карно
    print_section("МИНИМИЗАЦИЯ КНФ: КАРТА КАРНО")
    karnaugh_cnf_terms, karnaugh_cnf_viz = minimizer.minimize_karnaugh_cnf()
    print(karnaugh_cnf_viz)
    print(f"\nМинимизированная КНФ: {minimizer.get_minimized_cnf_expression(karnaugh_cnf_terms)}")

    print_section("ГОТОВО!")
    print("Все пункты лабораторной работы выполнены ")


if __name__ == "__main__":
    main()
