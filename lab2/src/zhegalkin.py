# src/zhegalkin.py
from typing import List, Tuple
from src.truth_table import TruthTable


class ZhegalkinPolynomial:
    """Построение полинома Жегалкина"""

    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.terms: List[Tuple[int, List[str]]] = []
        self.variables = truth_table.variables

    def build(self) -> None:
        """Построить полином методом неопределённых коэффициентов"""
        num_vars = len(self.variables)
        num_rows = len(self.truth_table.rows)
        coefficients = [False] * num_rows

        for i in range(num_rows):
            value = self.truth_table.rows[i].result
            for j in range(i):
                if (j & i) == j:  # j - подмножество i
                    value ^= coefficients[j]
            coefficients[i] = value

        self.terms = []
        for i, coeff in enumerate(coefficients):
            if coeff:
                term_vars = self._get_term_variables(i, num_vars)
                self.terms.append((i, term_vars))

    def _get_term_variables(self, index: int, num_vars: int) -> List[str]:
        """Получить переменные для терма по индексу"""
        vars_list = []
        for i in range(num_vars):
            if (index >> i) & 1:
                vars_list.append(self.variables[num_vars - 1 - i])
        return vars_list

    def is_linear(self) -> bool:
        """Проверка на линейность (нет конъюнкций > 1 переменной)"""
        for _, term_vars in self.terms:
            if len(term_vars) > 1:
                return False
        return True

    def to_string(self) -> str:
        """Представление полинома в виде строки"""
        if not self.terms:
            return "0"
        parts = []
        for _, term_vars in self.terms:
            if not term_vars:
                parts.append("1")
            elif len(term_vars) == 1:
                parts.append(term_vars[0])
            else:
                parts.append("(" + " ∧ ".join(term_vars) + ")")
        return " ⊕ ".join(parts)

    def get_terms_count(self) -> int:
        """Количество термов в полиноме"""
        return len(self.terms)