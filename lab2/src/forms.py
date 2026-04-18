from typing import List, Dict
from src.truth_table import TruthTable


class NormalFormBuilder:
    """Построитель нормальных форм"""

    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table

    def build_sdnf(self) -> str:
        """Построить СДНФ"""
        indices = self.truth_table.get_ones_indices()
        if not indices:
            return "0"
        terms = []
        for row in self.truth_table.rows:
            if row.result:
                term = self._build_conjunct(row.variables)
                terms.append(term)
        return " ∨ ".join(terms)

    def build_sknf(self) -> str:
        """Построить СКНФ"""
        indices = self.truth_table.get_zeros_indices()
        if not indices:
            return "1"
        clauses = []
        for row in self.truth_table.rows:
            if not row.result:
                clause = self._build_disjunct(row.variables)
                clauses.append(clause)
        return " ∧ ".join(clauses)

    def _build_conjunct(self, variables: Dict[str, bool]) -> str:
        parts = []
        for var, value in variables.items():
            if value:
                parts.append(var)
            else:
                parts.append(f"¬{var}")
        return "(" + "".join(parts) + ")"

    def _build_disjunct(self, variables: Dict[str, bool]) -> str:
        parts = []
        for var, value in variables.items():
            if value:
                parts.append(f"¬{var}")
            else:
                parts.append(var)
        return "(" + "|".join(parts) + ")"

    def get_sdnf_numeric(self) -> str:
        indices = self.truth_table.get_ones_indices()
        return f"Σ({', '.join(map(str, indices))})"

    def get_sknf_numeric(self) -> str:
        indices = self.truth_table.get_zeros_indices()
        return f"Π({', '.join(map(str, indices))})"

    def get_index_form(self) -> str:
        ones = self.truth_table.get_ones_indices()
        binary = "".join(str(int(row.result)) for row in self.truth_table.rows)
        return f"Индексы: {ones}\nДвоичный код: {binary}"
