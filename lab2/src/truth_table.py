from typing import List, Dict, Tuple
from src.models import ExpressionNode


class TruthTableRow:
    """Строка таблицы истинности"""

    def __init__(self, variables: Dict[str, bool], result: bool):
        self.variables = variables
        self.result = result

    def get_variable_values(self) -> List[bool]:
        return list(self.variables.values())

    def get_index(self) -> int:
        values = self.get_variable_values()
        index = 0
        for i, value in enumerate(reversed(values)):
            if value:
                index += (1 << i)
        return index


class TruthTable:
    """Таблица истинности"""

    def __init__(self, expression: ExpressionNode, variables: List[str]):
        self.expression = expression
        self.variables = variables
        self.rows: List[TruthTableRow] = []

    def build(self) -> None:
        """Построить таблицу истинности"""
        num_vars = len(self.variables)
        num_rows = 1 << num_vars
        for i in range(num_rows):
            values = self._get_variable_values(i, num_vars)
            var_dict = dict(zip(self.variables, values))
            result = self.expression.evaluate(var_dict)
            row = TruthTableRow(var_dict, result)
            self.rows.append(row)

    def _get_variable_values(self, index: int, num_vars: int) -> List[bool]:
        values = []
        for i in range(num_vars):
            bit = (index >> (num_vars - 1 - i)) & 1
            values.append(bool(bit))
        return values

    def get_ones_indices(self) -> List[int]:
        return [row.get_index() for row in self.rows if row.result]

    def get_zeros_indices(self) -> List[int]:
        return [row.get_index() for row in self.rows if not row.result]

    def print_table(self) -> str:
        lines = []
        header = " | ".join(self.variables) + " | F"
        lines.append(header)
        lines.append("-" * len(header))
        for row in self.rows:
            values = " | ".join(str(int(v)) for v in row.get_variable_values())
            result = str(int(row.result))
            lines.append(f"{values} | {result}")
        return "\n".join(lines)