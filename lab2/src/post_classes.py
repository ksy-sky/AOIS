from typing import List, Dict
from src.truth_table import TruthTable


class PostClassesChecker:
    """Проверка принадлежности функции классам Поста"""

    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table

    def check_t0(self) -> bool:
        """Класс T0: сохраняет ноль (f(0,0,...,0) = 0)"""
        first_row = self.truth_table.rows[0]
        return not first_row.result

    def check_t1(self) -> bool:
        """Класс T1: сохраняет единицу (f(1,1,...,1) = 1)"""
        last_row = self.truth_table.rows[-1]
        return last_row.result

    def check_s(self) -> bool:
        """Класс S: самодвойственная функция"""
        num_rows = len(self.truth_table.rows)
        for i in range(num_rows // 2):
            j = num_rows - 1 - i
            if self.truth_table.rows[i].result == self.truth_table.rows[j].result:
                return False
        return True

    def check_m(self) -> bool:
        """Класс M: монотонная функция"""
        num_rows = len(self.truth_table.rows)
        for i in range(num_rows):
            for j in range(i + 1, num_rows):
                if self._is_less_or_equal(i, j):
                    if self.truth_table.rows[i].result:
                        if not self.truth_table.rows[j].result:
                            return False
        return True

    def _is_less_or_equal(self, idx1: int, idx2: int) -> bool:
        row1 = self.truth_table.rows[idx1]
        row2 = self.truth_table.rows[idx2]
        vars1 = row1.get_variable_values()
        vars2 = row2.get_variable_values()
        for v1, v2 in zip(vars1, vars2):
            if v1 and not v2:
                return False
        return True

    def check_l(self) -> bool:
        """Класс L: линейная функция (полином Жегалкина без конъюнкций)"""
        from src.zhegalkin import ZhegalkinPolynomial
        zhegalkin = ZhegalkinPolynomial(self.truth_table)
        zhegalkin.build()
        return zhegalkin.is_linear()

    def get_all_classes(self) -> Dict[str, bool]:
        return {
            "T0 (сохраняет 0)": self.check_t0(),
            "T1 (сохраняет 1)": self.check_t1(),
            "S (самодвойственная)": self.check_s(),
            "M (монотонная)": self.check_m(),
            "L (линейная)": self.check_l()
        }

    def is_complete(self) -> bool:
        """Проверка полноты системы по теореме Поста"""
        classes = self.get_all_classes()
        return not any(classes.values())