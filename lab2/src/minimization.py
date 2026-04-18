# src/minimization.py
from typing import List, Dict, Tuple, Set, Optional
from src.truth_table import TruthTable

class Term:
    """Терм (конъюнкция для ДНФ или дизъюнкт для КНФ) для минимизации"""
    def __init__(self, variables: List[str], mask: List[Optional[bool]], is_cnf: bool = False):
        self.variables = variables
        self.mask = mask
        self.covered_indices: Set[int] = set()
        self.is_cnf = is_cnf

    def __str__(self) -> str:
        if self.is_cnf:
            parts = []
            for var, value in zip(self.variables, self.mask):
                if value is None:
                    continue
                parts.append(var if value else f"¬{var}")
            return "(" + " ∨ ".join(parts) + ")" if parts else "(0)"
        else:
            parts = []
            for var, value in zip(self.variables, self.mask):
                if value is None:
                    continue
                parts.append(var if value else f"¬{var}")
            return "(" + " ∧ ".join(parts) + ")" if parts else "(1)"

    def __eq__(self, other) -> bool:
        return isinstance(other, Term) and self.mask == other.mask

    def __hash__(self) -> int:
        return hash(tuple(self.mask))

    def can_glue_with(self, other: 'Term') -> bool:
        diff_count = 0
        for m1, m2 in zip(self.mask, other.mask):
            if m1 != m2:
                if m1 is None or m2 is None:
                    return False
                diff_count += 1
        return diff_count == 1

    def glue_with(self, other: 'Term') -> Optional['Term']:
        if not self.can_glue_with(other):
            return None
        new_mask = []
        for m1, m2 in zip(self.mask, other.mask):
            if m1 != m2:
                new_mask.append(None)
            else:
                new_mask.append(m1)
        return Term(self.variables, new_mask, self.is_cnf)

    def covers_index(self, index: int) -> bool:
        """Проверяет, покрывает ли терм заданный индекс таблицы истинности"""
        num_vars = len(self.variables)
        for i, mask_val in enumerate(self.mask):
            if mask_val is None:
                continue
            bit = bool((index >> (num_vars - 1 - i)) & 1)
            
            if self.is_cnf:
                # Для КНФ дизъюнкт покрывает ноль, если все его литералы = 0.
                # mask_val=True => литерал x => требует x=0 (bit=False)
                # mask_val=False => литерал ¬x => требует ¬x=0 => x=1 (bit=True)
                if bit == mask_val:
                    return False
            else:
                # Для ДНФ конъюнкт покрывает единицу при совпадении битов
                if bit != mask_val:
                    return False
        return True


class MinimizationCalculator:
    """Минимизация логических функций (ДНФ и КНФ)"""
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables
        self.num_vars = len(self.variables)

    # ==================== ДНФ МЕТОДЫ ====================

    def get_sdnf_terms(self) -> List[Term]:
        terms = []
        for row in self.truth_table.rows:
            if row.result:
                mask = list(row.variables.values())
                term = Term(self.variables, mask, is_cnf=False)
                term.covered_indices.add(row.get_index())
                terms.append(term)
        return terms

    def minimize_calculation_method_dnf(self) -> Tuple[List[str], List[Term]]:
        stages = []
        terms = self.get_sdnf_terms()
        stage_num = 1

        while True:
            new_terms = []
            used = set()
            stage_log = []

            for i, term1 in enumerate(terms):
                for j, term2 in enumerate(terms):
                    if i >= j: continue
                    if term1.can_glue_with(term2):
                        glued = term1.glue_with(term2)
                        if glued:
                            new_terms.append(glued)
                            used.add(i)
                            used.add(j)
                            stage_log.append(f"{term1} ∨ {term2} ⇒ {glued}")

            if not new_terms:
                break

            prime_implicants = [terms[i] for i in range(len(terms)) if i not in used]
            new_terms = self._remove_duplicates(new_terms)
            terms = prime_implicants + new_terms
            
            if stage_log:
                stages.append(f"Этап {stage_num} (ДНФ):\n" + "\n".join(stage_log))
            stage_num += 1
            if stage_num > 10: break

        result_terms = self._minimal_cover_dnf(terms)
        return stages, result_terms

    def minimize_table_method_dnf(self) -> Tuple[List[str], List[Term], str]:
        stages, terms = self.minimize_calculation_method_dnf()
        coverage_table = self._build_coverage_table_dnf(terms)
        return stages, terms, coverage_table

    def minimize_karnaugh_dnf(self) -> Tuple[List[Term], str]:
        ones_indices = set(self.truth_table.get_ones_indices())
        if not ones_indices: return [], "Функция тождественно равна 0"
        if self.num_vars < 2 or self.num_vars > 5:
            return [], f"Карта Карно поддерживает 2-5 переменные, а у вас {self.num_vars}"
        
        gray_code = [0, 1, 3, 2]
        if self.num_vars == 5:
            return self._karnaugh_5var_dnf(ones_indices, gray_code)
        else:
            # Ваш существующий код для 3-4 переменных
            karnaugh_map = self._build_karnaugh_map(gray_code)
            groups = self._find_groups(karnaugh_map, ones_indices, gray_code)
            terms = self._groups_to_terms_dnf(groups, gray_code)
            visualization = self._visualize_karnaugh_dnf(karnaugh_map, groups, gray_code, ones_indices)
            return terms, visualization

    def minimize_karnaugh_cnf(self) -> Tuple[List[Term], str]:
        zeros_indices = set(self.truth_table.get_zeros_indices())
        if not zeros_indices: return [], "Функция тождественно равна 1"
        if self.num_vars < 2 or self.num_vars > 5:
            return [], f"Карта Карно поддерживает 2-5 переменные, а у вас {self.num_vars}"
        
        gray_code = [0, 1, 3, 2]
        if self.num_vars == 5:
            return self._karnaugh_5var_cnf(zeros_indices, gray_code)
        else:
            # Ваш существующий код для 3-4 переменных
            karnaugh_map = self._build_karnaugh_map(gray_code)
            groups = self._find_groups(karnaugh_map, zeros_indices, gray_code)
            terms = self._groups_to_terms_cnf(groups, gray_code)
            visualization = self._visualize_karnaugh_cnf(karnaugh_map, groups, gray_code, zeros_indices)
            return terms, visualization

    # ==================== 5-ПЕРЕМЕННЫЕ ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _karnaugh_5var_dnf(self, target_indices: Set[int], gray_code: List[int]) -> Tuple[List[Term], str]:
        map_5 = [[[0]*4 for _ in range(4)] for _ in range(2)]
        for a in range(2):
            for r in range(4):
                for c in range(4):
                    idx = (a << 4) | (gray_code[r] << 2) | gray_code[c]
                    map_5[a][r][c] = idx

        matrix = [[[1 if map_5[a][r][c] in target_indices else 0 for c in range(4)] for r in range(4)] for a in range(2)]
        groups = self._find_groups_5var(matrix)
        terms = self._groups_to_terms_5var(groups, map_5, is_cnf=False)
        viz = self._visualize_karnaugh_5var(map_5, groups, target_indices, is_cnf=False)
        return terms, viz

    def _karnaugh_5var_cnf(self, target_indices: Set[int], gray_code: List[int]) -> Tuple[List[Term], str]:
        map_5 = [[[0]*4 for _ in range(4)] for _ in range(2)]
        for a in range(2):
            for r in range(4):
                for c in range(4):
                    idx = (a << 4) | (gray_code[r] << 2) | gray_code[c]
                    map_5[a][r][c] = idx

        matrix = [[[1 if map_5[a][r][c] in target_indices else 0 for c in range(4)] for r in range(4)] for a in range(2)]
        groups = self._find_groups_5var(matrix)
        terms = self._groups_to_terms_5var(groups, map_5, is_cnf=True)
        viz = self._visualize_karnaugh_5var(map_5, groups, target_indices, is_cnf=True)
        return terms, viz

    def _find_groups_5var(self, matrix: List[List[List[int]]]) -> List[List[Tuple[int, int, int]]]:
        groups = []
        # Все возможные размеры прямоугольных параллелепипедов (depth, height, width)
        dims = [(2,4,4), (2,4,2), (2,2,4), (2,2,2), (1,4,4), (1,4,2), (1,2,4), (1,2,2), (2,4,1), (2,2,1), (1,4,1), (1,2,1), (2,1,1), (1,1,1)]
        
        for d, h, w in dims:
            for a0 in range(2 - d + 1):
                for r0 in range(4):
                    for c0 in range(4):
                        group = []
                        valid = True
                        for da in range(d):
                            for dh in range(h):
                                for dw in range(w):
                                    r = (r0 + dh) % 4
                                    c = (c0 + dw) % 4
                                    if matrix[(a0 + da) % 2][r][c] == 1:
                                        group.append(((a0 + da) % 2, r, c))
                                    else:
                                        valid = False
                                        break
                                if not valid: break
                            if not valid: break
                        if valid and group:
                            if not any(set(group).issubset(set(g)) for g in groups):
                                groups.append(group)
        groups.sort(key=len, reverse=True)
        return groups

    def _groups_to_terms_5var(self, groups: List[List[Tuple[int, int, int]]], 
                              map_5: List[List[List[int]]], is_cnf: bool) -> List[Term]:
        terms = []
        for group in groups:
            masks = [set() for _ in range(5)] # a, b, c, d, e
            for a, r, c in group:
                idx = map_5[a][r][c]
                masks[0].add(bool((idx >> 4) & 1))
                masks[1].add(bool((idx >> 3) & 1))
                masks[2].add(bool((idx >> 2) & 1))
                masks[3].add(bool((idx >> 1) & 1))
                masks[4].add(bool(idx & 1))

            mask = [None]*5
            for i, s in enumerate(masks):
                if len(s) == 1: mask[i] = s.pop()
            
            if is_cnf:
                mask = [None if m is None else not m for m in mask]
                
            if any(m is not None for m in mask):
                terms.append(Term(self.variables, mask, is_cnf=is_cnf))
        return self._remove_duplicates(terms)

    def _visualize_karnaugh_5var(self, map_5: List[List[List[int]]], 
                                 groups: List[List[Tuple[int, int, int]]], 
                                 target_indices: Set[int], is_cnf: bool) -> str:
        lines = [f"Карта Карно (5 переменных, {'по нулям' if is_cnf else 'по единицам'})", ""]
        gray = [0, 1, 3, 2]
        
        lines.append("         de")
        lines.append("         00  01  11  10          00  01  11  10")
        lines.append("       bc +---------------      bc +---------------")
        
        for r in range(4):
            r_label = f"{gray[r]:02b}"
            line0 = f"a=0 {r_label} | "
            line1 = f"a=1 {r_label} | "
            for c in range(4):
                idx0 = map_5[0][r][c]
                idx1 = map_5[1][r][c]
                val0 = 1 if idx0 in target_indices else 0
                val1 = 1 if idx1 in target_indices else 0
                line0 += f" {val0}  "
                line1 += f" {val1}  "
            lines.append(line0 + "    " + line1)
            
        lines.append("\nГруппы:")
        for i, g in enumerate(groups, 1):
            # Форматируем координаты для читаемости: a=0, row=01, col=10
            coords = []
            for a, r, c in g:
                coords.append(f"(a={a}, bc={gray[r]:02b}, de={gray[c]:02b})")
            lines.append(f"Группа {i}: {coords[0]} ... ({len(g)} ячеек)")
        return "\n".join(lines)
    # ==================== КНФ МЕТОДЫ ====================

    def get_sknf_terms(self) -> List[Term]:
        terms = []
        for row in self.truth_table.rows:
            if not row.result:
                # Для КНФ маска инвертируется: 0 -> True (x), 1 -> False (¬x)
                mask = [not m for m in row.variables.values()]
                term = Term(self.variables, mask, is_cnf=True)
                term.covered_indices.add(row.get_index())
                terms.append(term)
        return terms

    def minimize_calculation_method_cnf(self) -> Tuple[List[str], List[Term]]:
        stages = []
        terms = self.get_sknf_terms()
        if len(terms) <= 1: return stages, terms
        
        stage_num = 1
        while True:
            new_terms = []
            used = set()
            stage_log = []

            for i, term1 in enumerate(terms):
                for j, term2 in enumerate(terms):
                    if i >= j: continue
                    if term1.can_glue_with(term2):
                        glued = term1.glue_with(term2)
                        if glued:
                            if not any(self._terms_equal(g, glued) for g in new_terms):
                                new_terms.append(glued)
                                used.add(i)
                                used.add(j)
                                stage_log.append(f"{self._term_to_str_cnf(term1)} ∧ {self._term_to_str_cnf(term2)} ⇒ {self._term_to_str_cnf(glued)}")

            if not new_terms:
                break

            prime_implicants = [terms[i] for i in range(len(terms)) if i not in used]
            terms = self._remove_duplicates(prime_implicants + new_terms)
            
            if stage_log:
                stages.append(f"Этап {stage_num} (КНФ):\n" + "\n".join(stage_log))
            stage_num += 1
            if stage_num > 10: break

        result_terms = self._minimal_cover_cnf(terms)
        return stages, result_terms

    def minimize_table_method_cnf(self) -> Tuple[List[str], List[Term], str]:
        stages, terms = self.minimize_calculation_method_cnf()
        coverage_table = self._build_coverage_table_cnf(terms)
        return stages, terms, coverage_table


    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _remove_duplicates(self, terms: List[Term]) -> List[Term]:
        unique = []
        seen = set()
        for term in terms:
            key = tuple(term.mask)
            if key not in seen:
                seen.add(key)
                unique.append(term)
        return unique

    def _terms_equal(self, t1: Term, t2: Term) -> bool:
        return t1.mask == t2.mask

    def _term_to_str_cnf(self, term: Term) -> str:
        parts = []
        for var, value in zip(term.variables, term.mask):
            if value is None: continue
            parts.append(var if value else f"¬{var}")
        return "(" + " ∨ ".join(parts) + ")" if parts else "(0)"

    def _minimal_cover_dnf(self, implicants: List[Term]) -> List[Term]:
        ones_indices = self.truth_table.get_ones_indices()
        if not ones_indices: return []
        
        unique_implicants = self._remove_duplicates(implicants)
        selected = []
        uncovered = set(ones_indices)
        
        while uncovered and unique_implicants:
            best_imp = None
            best_count = -1
            for imp in unique_implicants:
                count = sum(1 for idx in uncovered if imp.covers_index(idx))
                if count > best_count:
                    best_count = count
                    best_imp = imp
            if best_imp is None or best_count == 0: break
            selected.append(best_imp)
            uncovered -= {idx for idx in uncovered if best_imp.covers_index(idx)}
            unique_implicants.remove(best_imp)
        return selected

    def _minimal_cover_cnf(self, implicants: List[Term]) -> List[Term]:
        zeros_indices = self.truth_table.get_zeros_indices()
        if not zeros_indices: return []
        
        unique_implicants = self._remove_duplicates(implicants)
        selected = []
        uncovered = set(zeros_indices)
        
        while uncovered and unique_implicants:
            best_imp = None
            best_count = -1
            for imp in unique_implicants:
                count = sum(1 for idx in uncovered if imp.covers_index(idx))
                if count > best_count:
                    best_count = count
                    best_imp = imp
            if best_imp is None or best_count == 0: break
            selected.append(best_imp)
            uncovered -= {idx for idx in uncovered if best_imp.covers_index(idx)}
            unique_implicants.remove(best_imp)
            
        # Фоллбэк для непокрытых нулей (теоретически не должен срабатывать при корректном склеивании)
        for idx in uncovered:
            for row in self.truth_table.rows:
                if row.get_index() == idx:
                    mask = [not m for m in row.variables.values()]
                    selected.append(Term(self.variables, mask, is_cnf=True))
                    break
        return selected

    def _build_coverage_table_dnf(self, terms: List[Term]) -> str:
        ones_indices = self.truth_table.get_ones_indices()
        if not ones_indices: return "Таблица покрытий (ДНФ): Нет единиц в функции"
        
        lines = ["Таблица покрытий (ДНФ)", ""]
        header = "Терм" + " " * 15 + " | " + " | ".join(str(i) for i in ones_indices)
        lines.append(header)
        lines.append("-" * len(header))
        
        for term in terms:
            row = f"{str(term):20} | "
            for idx in ones_indices:
                row += " X | " if term.covers_index(idx) else "   | "
            lines.append(row)
        return "\n".join(lines)

    def _build_coverage_table_cnf(self, terms: List[Term]) -> str:
        zeros_indices = self.truth_table.get_zeros_indices()
        if not zeros_indices: return "Таблица покрытий (КНФ): Нет нулей в функции"
        
        lines = ["Таблица покрытий (КНФ)", ""]
        header = "Терм" + " " * 15 + " | " + " | ".join(str(i) for i in zeros_indices)
        lines.append(header)
        lines.append("-" * len(header))
        
        for term in terms:
            term_str = self._term_to_str_cnf(term)
            row = f"{term_str:20} | "
            for idx in zeros_indices:
                row += " X | " if term.covers_index(idx) else "   | "
            lines.append(row)
        return "\n".join(lines)

    def _build_karnaugh_map(self, gray_code: List[int]) -> Dict[Tuple[int, int], int]:
        k_map = {}
        for idx in range(1 << self.num_vars):
            if self.num_vars == 3:
                row = idx >> 2
                col = idx & 0b11
                gray_col = gray_code.index(col) if col in gray_code else col
                k_map[(row, gray_col)] = idx
            elif self.num_vars == 4:
                row_bits = idx >> 2
                col_bits = idx & 0b11
                gray_row = gray_code.index(row_bits) if row_bits in gray_code else row_bits
                gray_col = gray_code.index(col_bits) if col_bits in gray_code else col_bits
                k_map[(gray_row, gray_col)] = idx
        return k_map

    def _find_groups(self, k_map: Dict[Tuple[int, int], int], target_indices: Set[int], gray_code: List[int]) -> List[List[Tuple[int, int]]]:
        groups = []
        rows = 4 if self.num_vars == 4 else 2
        cols = 4
        
        matrix = [[0] * cols for _ in range(rows)]
        for (r, c), idx in k_map.items():
            if idx in target_indices:
                matrix[r][c] = 1
        
        for size in [16, 8, 4, 2, 1]:
            if size > rows * cols: continue
            for height in [1, 2, 4]:
                if height > rows: continue
                width = size // height
                if width > cols or width * height != size: continue
                
                for start_row in range(rows):
                    for start_col in range(cols):
                        group = []
                        valid = True
                        for dr in range(height):
                            r = (start_row + dr) % rows
                            for dc in range(width):
                                c = (start_col + dc) % cols
                                if matrix[r][c] == 1:
                                    group.append((r, c))
                                else:
                                    valid = False
                                    break
                            if not valid: break
                        if valid and group:
                            is_subset = any(set(group).issubset(set(existing)) for existing in groups)
                            if not is_subset:
                                groups.append(group)
        
        groups.sort(key=len, reverse=True)
        return groups

    def _groups_to_terms_dnf(self, groups: List[List[Tuple[int, int]]], gray_code: List[int]) -> List[Term]:
        terms = []
        for group in groups:
            mask = [None] * self.num_vars
            if self.num_vars == 3:
                var_values = [set() for _ in range(3)]
                for r, c in group:
                    col_val = gray_code[c] if c < len(gray_code) else c
                    idx = (r << 2) | col_val
                    for i in range(3):
                        var_values[i].add(bool((idx >> (2 - i)) & 1))
                for i in range(3):
                    if len(var_values[i]) == 1: mask[i] = var_values[i].pop()
            elif self.num_vars == 4:
                var_values = [set() for _ in range(4)]
                for r, c in group:
                    row_val = gray_code[r] if r < len(gray_code) else r
                    col_val = gray_code[c] if c < len(gray_code) else c
                    idx = (row_val << 2) | col_val
                    for i in range(4):
                        var_values[i].add(bool((idx >> (3 - i)) & 1))
                for i in range(4):
                    if len(var_values[i]) == 1: mask[i] = var_values[i].pop()
            if any(m is not None for m in mask):
                terms.append(Term(self.variables, mask, is_cnf=False))
        return self._remove_duplicates(terms)

    def _groups_to_terms_cnf(self, groups: List[List[Tuple[int, int]]], gray_code: List[int]) -> List[Term]:
        terms = []
        for group in groups:
            mask = [None] * self.num_vars
            if self.num_vars == 3:
                var_values = [set() for _ in range(3)]
                for r, c in group:
                    col_val = gray_code[c] if c < len(gray_code) else c
                    idx = (r << 2) | col_val
                    for i in range(3):
                        var_values[i].add(bool((idx >> (2 - i)) & 1))
                for i in range(3):
                    if len(var_values[i]) == 1: mask[i] = var_values[i].pop()
            elif self.num_vars == 4:
                var_values = [set() for _ in range(4)]
                for r, c in group:
                    row_val = gray_code[r] if r < len(gray_code) else r
                    col_val = gray_code[c] if c < len(gray_code) else c
                    idx = (row_val << 2) | col_val
                    for i in range(4):
                        var_values[i].add(bool((idx >> (3 - i)) & 1))
                for i in range(4):
                    if len(var_values[i]) == 1: mask[i] = var_values[i].pop()
            if any(m is not None for m in mask):
                # Для КНФ инвертируем маску относительно ДНФ
                mask = [None if m is None else not m for m in mask]
                terms.append(Term(self.variables, mask, is_cnf=True))
        return self._remove_duplicates(terms)

    def _visualize_karnaugh_dnf(self, k_map: Dict[Tuple[int, int], int], groups: List[List[Tuple[int, int]]], 
                                 gray_code: List[int], ones_indices: Set[int]) -> str:
        lines = ["Карта Карно (ДНФ, по единицам)", ""]
        if self.num_vars == 3:
            lines.append("     bc")
            lines.append("     00  01  11  10")
            lines.append("   +----------------")
            for row in range(2):
                line = f"a={row} | "
                for col in range(4):
                    col_val = gray_code[col] if col < len(gray_code) else col
                    idx = (row << 2) | col_val
                    val = 1 if idx in ones_indices else 0
                    line += f" {val}    "
                lines.append(line)
        elif self.num_vars == 4:
            lines.append("      cd")
            lines.append("      00  01  11  10")
            lines.append("    +----------------")
            for row in range(4):
                row_val = gray_code[row] if row < len(gray_code) else row
                line = f"ab={row_val:02b} | "
                for col in range(4):
                    col_val = gray_code[col] if col < len(gray_code) else col
                    idx = (row_val << 2) | col_val
                    val = 1 if idx in ones_indices else 0
                    line += f" {val}    "
                lines.append(line)
        lines.append("\nГруппы:")
        for i, group in enumerate(groups):
            lines.append(f"Группа {i + 1}: {group}")
        return "\n".join(lines)

    def _visualize_karnaugh_cnf(self, k_map: Dict[Tuple[int, int], int], groups: List[List[Tuple[int, int]]], 
                                gray_code: List[int], zeros_indices: Set[int]) -> str:
        lines = ["Карта Карно (КНФ, по нулям)", ""]
        if self.num_vars == 3:
            lines.append("     bc")
            lines.append("     00  01  11  10")
            lines.append("   +----------------")
            for row in range(2):
                line = f"a={row} | "
                for col in range(4):
                    col_val = gray_code[col] if col < len(gray_code) else col
                    idx = (row << 2) | col_val
                    val = 1 if idx in zeros_indices else 0
                    line += f" {val}    "
                lines.append(line)
        elif self.num_vars == 4:
            lines.append("      cd")
            lines.append("      00  01  11  10")
            lines.append("    +----------------")
            for row in range(4):
                row_val = gray_code[row] if row < len(gray_code) else row
                line = f"ab={row_val:02b} | "
                for col in range(4):
                    col_val = gray_code[col] if col < len(gray_code) else col
                    idx = (row_val << 2) | col_val
                    val = 1 if idx in zeros_indices else 0
                    line += f" {val}    "
                lines.append(line)
        lines.append("\nГруппы нулей (для КНФ):")
        for i, group in enumerate(groups):
            lines.append(f"Группа {i + 1}: {group}")
        return "\n".join(lines)

    def get_minimized_dnf_expression(self, terms: List[Term]) -> str:
        if not terms: return "0"
        return " ∨ ".join(str(term) for term in terms)

    def get_minimized_cnf_expression(self, terms: List[Term]) -> str:
        if not terms: return "1"
        cnf_parts = []
        for term in terms:
            parts = []
            for var, value in zip(term.variables, term.mask):
                if value is None: continue
                parts.append(var if value else f"¬{var}")
            if parts: cnf_parts.append("(" + " ∨ ".join(parts) + ")")
            else: cnf_parts.append("(0)")
        return " ∧ ".join(cnf_parts)
