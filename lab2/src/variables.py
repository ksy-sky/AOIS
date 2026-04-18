from typing import List, Dict
from src.truth_table import TruthTable
from src.models import ExpressionNode


class FictitiousVariablesFinder:
    """Поиск фиктивных переменных"""

    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables

    def find_fictitious(self) -> List[str]:
        """Найти все фиктивные переменные"""
        fictitious = []
        for var in self.variables:
            if self._is_fictitious(var):
                fictitious.append(var)
        return fictitious

    def _is_fictitious(self, variable: str) -> bool:
        """Проверка переменной на фиктивность"""
        var_index = self.variables.index(variable)
        num_rows = len(self.truth_table.rows)
        num_vars = len(self.variables)
        
        # Шаг для сравнения зависит от позиции переменной
        # Для последней переменной шаг = 1, для предпоследней = 2, и т.д.
        step = 1 << (num_vars - 1 - var_index)
        
        for i in range(0, num_rows, step * 2):
            for j in range(i, i + step):
                row1_idx = j
                row2_idx = j + step
                
                if row2_idx >= num_rows:
                    continue
                    
                row1 = self.truth_table.rows[row1_idx]
                row2 = self.truth_table.rows[row2_idx]
                
                # Если результаты различаются - переменная существенная
                if row1.result != row2.result:
                    return False
        
        return True

    def _rows_differ_only_at(
        self, idx1: int, idx2: int, var_idx: int
    ) -> bool:
        row1 = self.truth_table.rows[idx1]
        row2 = self.truth_table.rows[idx2]
        vals1 = row1.get_variable_values()
        vals2 = row2.get_variable_values()
        for i, (v1, v2) in enumerate(zip(vals1, vals2)):
            if i == var_idx:
                if v1 == v2:
                    return False
            else:
                if v1 != v2:
                    return False
        return True

    def get_essential_variables(self) -> List[str]:
        """Получить существенные переменные"""
        all_vars = set(self.variables)
        fictitious = set(self.find_fictitious())
        return list(all_vars - fictitious)