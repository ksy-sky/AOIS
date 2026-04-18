# src/derivatives.py
from typing import List
import itertools
from src.truth_table import TruthTable


class BooleanDerivative:
    """Булевы производные — с правильным упрощением"""
    
    def __init__(self, expression, variables: List[str]):
        self.expression = expression
        self.variables = variables
    
    def partial_derivative(self, var: str) -> str:
        return self._derivative_to_string([var])
    
    def mixed_derivative(self, vars_list: List[str]) -> str:
        return self._derivative_to_string(vars_list)
    
    def _derivative_to_string(self, vars_list: List[str]) -> str:
        values = self._compute_derivative_values(vars_list)
        remaining_vars = [v for v in self.variables if v not in vars_list]
        return self._simplify_expression(values, remaining_vars)
    
    def _compute_derivative_values(self, vars_list: List[str]) -> List[bool]:
        n = len(self.variables)
        tt = TruthTable(self.expression, self.variables)
        tt.build()
        tt_vec = [row.result for row in tt.rows]
        
        remaining = [v for v in self.variables if v not in vars_list]
        result = []
        
        # Перебираем только комбинации ОСТАВШИХСЯ переменных
        for rem_combo in itertools.product([False, True], repeat=len(remaining)):
            fixed = dict(zip(remaining, rem_combo))
            xor_val = False
            
            # XOR по всем 2^k комбинациям дифференцируемых переменных
            for diff_combo in itertools.product([False, True], repeat=len(vars_list)):
                values = {**fixed, **dict(zip(vars_list, diff_combo))}
                idx = 0
                for j, var in enumerate(self.variables):
                    if values[var]:
                        idx |= (1 << (n - 1 - j))
                xor_val ^= tt_vec[idx]
            result.append(xor_val)
        return result

    def _simplify_expression(self, values: List[bool], variables: List[str]) -> str:
        if not variables:
            return "1" if values[0] else "0"
        
        num_vars = len(variables)
        num_rows = 1 << num_vars
        ones = [i for i, v in enumerate(values) if v]
        
        # Константы
        if len(ones) == 0:
            return "0"
        if len(ones) == num_rows:
            return "1"
        
        # Проверка: одна переменная
        for i, var in enumerate(variables):
            match = True
            for idx in range(num_rows):
                bit = (idx >> (num_vars - 1 - i)) & 1
                if values[idx] != (bit == 1):
                    match = False
                    break
            if match:
                return var
            
            match = True
            for idx in range(num_rows):
                bit = (idx >> (num_vars - 1 - i)) & 1
                if values[idx] != (bit == 0):
                    match = False
                    break
            if match:
                return f"¬{var}"
        
        # Проверка: конъюнкция (AND)
        for pattern in range(1 << num_vars):
            is_and = True
            for idx in range(num_rows):
                matches_pattern = True
                for j in range(num_vars):
                    bit = (idx >> (num_vars - 1 - j)) & 1
                    pattern_bit = (pattern >> (num_vars - 1 - j)) & 1
                    if pattern_bit == 1 and bit != 1:
                        matches_pattern = False
                        break
                    if pattern_bit == 0 and bit != 0:
                        matches_pattern = False
                        break
                
                if matches_pattern:
                    if not values[idx]:
                        is_and = False
                        break
                else:
                    if values[idx]:
                        is_and = False
                        break
            
            if is_and:
                parts = []
                for j, var in enumerate(variables):
                    bit = (pattern >> (num_vars - 1 - j)) & 1
                    if bit == 1:
                        parts.append(var)
                    else:
                        parts.append(f"¬{var}")
                return "".join(parts)
        
        # Собираем все термы
        terms = []
        for idx in ones:
            term = []
            for i, var in enumerate(variables):
                bit = (idx >> (num_vars - 1 - i)) & 1
                term.append(var if bit else f"¬{var}")
            terms.append("".join(term))
        
        # Убираем дубликаты
        unique_terms = []
        for t in terms:
            if t not in unique_terms:
                unique_terms.append(t)
        
        # Пытаемся упростить дизъюнкцию
        simplified = self._simplify_disjunction(unique_terms, variables)
        if simplified:
            return simplified
        
        return " ∨ ".join(unique_terms)
    
    def _simplify_disjunction(self, terms: List[str], variables: List[str]) -> str:
        """Упрощает дизъюнкцию термов"""
        if not terms:
            return None
        
        num_vars = len(variables)
        
        # Для 1 переменной
        if num_vars == 1:
            var = variables[0]
            if len(terms) == 2:
                if f"{var}" in terms and f"¬{var}" in terms:
                    return "1"
            return None
        
        # Для 2 переменных
        if num_vars == 2:
            var1, var2 = variables[0], variables[1]
            
            # Все возможные термы
            term_map = {
                f"{var1}{var2}": (1, 1),
                f"{var1}¬{var2}": (1, 0),
                f"¬{var1}{var2}": (0, 1),
                f"¬{var1}¬{var2}": (0, 0)
            }
            
            # Преобразуем в наборы битов
            term_bits = []
            for term in terms:
                if term in term_map:
                    term_bits.append(term_map[term])
            
            # Проверяем, покрывают ли термы все комбинации по одной переменной
            # Например: ¬var1var2 ∨ ¬var1¬var2 = ¬var1
            bits0 = [b[0] for b in term_bits]  # значения var1
            bits1 = [b[1] for b in term_bits]  # значения var2
            
            # Все значения var1 одинаковые? → результат зависит только от var1
            if len(set(bits0)) == 1:
                val = bits0[0]
                # Проверяем, что покрыты все комбинации var2
                expected = [(val, 0), (val, 1)]
                if all(e in term_bits for e in expected):
                    return var1 if val == 1 else f"¬{var1}"
            
            # Все значения var2 одинаковые? → результат зависит только от var2
            if len(set(bits1)) == 1:
                val = bits1[0]
                expected = [(0, val), (1, val)]
                if all(e in term_bits for e in expected):
                    return var2 if val == 1 else f"¬{var2}"
            
            # Проверка на тавтологию (все 4 комбинации)
            if len(term_bits) == 4:
                return "1"
        
        # Для 3 переменных - проверяем на тавтологию по одной переменной
        if num_vars == 3:
            # Проверяем, не равна ли функция 1 (все 8 комбинаций)
            if len(terms) == 8:
                return "1"
            
            # Проверяем, не равна ли функция одной переменной
            for i, var in enumerate(variables):
                # Собираем все комбинации, где эта переменная = 0 и = 1
                zero_terms = []
                one_terms = []
                for term in terms:
                    # Определяем значение переменной в терме
                    if f"{var}" in term:
                        one_terms.append(term)
                    elif f"¬{var}" in term:
                        zero_terms.append(term)
                    else:
                        # Переменная отсутствует - значит, она может быть любой
                        # Такое возможно только если терм уже упрощен
                        pass
                
                # Если все термы содержат переменную в одном состоянии
                if len(zero_terms) == 0 and len(one_terms) > 0:
                    # Все термы с var=1, проверяем полноту по остальным
                    if len(one_terms) == 4:  # 2^(n-1) = 4 для n=3
                        return var
                if len(one_terms) == 0 and len(zero_terms) > 0:
                    if len(zero_terms) == 4:
                        return f"¬{var}"
        
        return None
    
    def _idx_to_vals(self, idx: int, num_vars: int) -> List[bool]:
        vals = []
        for i in range(num_vars):
            bit = (idx >> (num_vars - 1 - i)) & 1
            vals.append(bit == 1)
        return vals
    
    def _vals_to_idx(self, vals: List[bool]) -> int:
        idx = 0
        for i, v in enumerate(vals):
            if v:
                idx |= 1 << (len(vals) - 1 - i)
        return idx