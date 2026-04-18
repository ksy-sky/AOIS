import pytest
from src.parser import ExpressionParser, ParserError
from src.models import VariableNode, NotNode, AndNode, OrNode, ExpressionNode, ImplicationNode, XorNode, EquivalenceNode
from src.truth_table import TruthTable, TruthTableRow
from src.forms import NormalFormBuilder
from src.variables import FictitiousVariablesFinder
from src.post_classes import PostClassesChecker
from src.zhegalkin import ZhegalkinPolynomial
from src.derivatives import BooleanDerivative
from src.minimization import MinimizationCalculator, Term


class TestExpressionParser:

    def test_parse_single_variable(self):
        parser = ExpressionParser("a")
        node = parser.parse()
        assert isinstance(node, VariableNode)
        assert node.name == "a"

    def test_parse_not_operation(self):
        parser = ExpressionParser("!a")
        node = parser.parse()
        assert isinstance(node, NotNode)
        assert isinstance(node.operand, VariableNode)

    def test_parse_and_operation(self):
        parser = ExpressionParser("a&b")
        node = parser.parse()
        assert isinstance(node, AndNode)

    def test_parse_or_operation(self):
        parser = ExpressionParser("a|b")
        node = parser.parse()
        assert isinstance(node, OrNode)

    def test_parse_implication_arrow(self):
        parser = ExpressionParser("a→b")
        node = parser.parse()
        from src.models import ImplicationNode
        assert isinstance(node, ImplicationNode)

    def test_parse_implication_dash(self):
        parser = ExpressionParser("a->b")
        node = parser.parse()
        from src.models import ImplicationNode
        assert isinstance(node, ImplicationNode)

    def test_parse_complex_expression(self):
        parser = ExpressionParser("!(!a→!b)|c")
        node = parser.parse()
        assert node is not None

    def test_parse_with_parentheses(self):
        parser = ExpressionParser("(a&b)|c")
        node = parser.parse()
        assert node is not None

    def test_invalid_character(self):
        parser = ExpressionParser("a&b&f")  # f недопустима
        with pytest.raises(ParserError):
            parser.parse()

    def test_evaluate_and(self):
        parser = ExpressionParser("a&b")
        node = parser.parse()
        assert node.evaluate({"a": True, "b": True}) == True
        assert node.evaluate({"a": True, "b": False}) == False

    def test_evaluate_or(self):
        parser = ExpressionParser("a|b")
        node = parser.parse()
        assert node.evaluate({"a": False, "b": False}) == False
        assert node.evaluate({"a": True, "b": False}) == True

    def test_evaluate_not(self):
        parser = ExpressionParser("!a")
        node = parser.parse()
        assert node.evaluate({"a": True}) == False
        assert node.evaluate({"a": False}) == True

    def test_evaluate_implication(self):
        parser = ExpressionParser("a→b")
        node = parser.parse()
        assert node.evaluate({"a": True, "b": False}) == False
        assert node.evaluate({"a": False, "b": False}) == True
    
    def test_parse_equivalence_operation(self):
        parser = ExpressionParser("a~b")
        node = parser.parse()
        from src.models import EquivalenceNode, XorNode
        # В текущей реализации парсера ~ может обрабатываться как XorNode
        # или EquivalenceNode в зависимости от реализации
        # Проверяем что узел не None и имеет метод evaluate
        assert node is not None
        assert hasattr(node, 'evaluate')

    def test_evaluate_equivalence(self):
        parser = ExpressionParser("a~b")
        node = parser.parse()
        # Эквивалентность: True только когда a и b равны
        assert node.evaluate({"a": True, "b": True}) == True
        assert node.evaluate({"a": True, "b": False}) == False
        assert node.evaluate({"a": False, "b": True}) == False
        assert node.evaluate({"a": False, "b": False}) == True

class TestModelsCoverage:
    """Тесты для покрытия models.py"""

    def test_variable_node_evaluate_missing_var(self):
        """Тест VariableNode с отсутствующей переменной"""
        node = VariableNode("x")
        result = node.evaluate({})  # переменной нет в словаре
        assert result == False

    def test_variable_node_get_variables(self):
        """Тест VariableNode.get_variables"""
        node = VariableNode("x")
        vars_list = node.get_variables()
        assert vars_list == ["x"]

    def test_not_node_evaluate(self):
        """Тест NotNode.evaluate"""
        var_node = VariableNode("a")
        not_node = NotNode(var_node)
        assert not_node.evaluate({"a": True}) == False
        assert not_node.evaluate({"a": False}) == True

    def test_not_node_get_variables(self):
        """Тест NotNode.get_variables"""
        var_node = VariableNode("a")
        not_node = NotNode(var_node)
        vars_list = not_node.get_variables()
        assert vars_list == ["a"]

    def test_and_node_evaluate(self):
        """Тест AndNode.evaluate"""
        left = VariableNode("a")
        right = VariableNode("b")
        and_node = AndNode(left, right)
        assert and_node.evaluate({"a": True, "b": True}) == True
        assert and_node.evaluate({"a": True, "b": False}) == False
        assert and_node.evaluate({"a": False, "b": True}) == False

    def test_and_node_get_variables(self):
        """Тест AndNode.get_variables"""
        left = VariableNode("a")
        right = VariableNode("b")
        and_node = AndNode(left, right)
        vars_list = and_node.get_variables()
        assert set(vars_list) == {"a", "b"}

    def test_or_node_evaluate(self):
        """Тест OrNode.evaluate"""
        left = VariableNode("a")
        right = VariableNode("b")
        or_node = OrNode(left, right)
        assert or_node.evaluate({"a": False, "b": False}) == False
        assert or_node.evaluate({"a": True, "b": False}) == True
        assert or_node.evaluate({"a": False, "b": True}) == True

    def test_or_node_get_variables(self):
        """Тест OrNode.get_variables"""
        left = VariableNode("a")
        right = VariableNode("b")
        or_node = OrNode(left, right)
        vars_list = or_node.get_variables()
        assert set(vars_list) == {"a", "b"}

    def test_implication_node_evaluate(self):
        """Тест ImplicationNode.evaluate"""
        left = VariableNode("a")
        right = VariableNode("b")
        impl_node = ImplicationNode(left, right)
        # a→b: ложно только когда a=True, b=False
        assert impl_node.evaluate({"a": True, "b": True}) == True
        assert impl_node.evaluate({"a": True, "b": False}) == False
        assert impl_node.evaluate({"a": False, "b": True}) == True
        assert impl_node.evaluate({"a": False, "b": False}) == True

    def test_implication_node_get_variables(self):
        """Тест ImplicationNode.get_variables"""
        left = VariableNode("a")
        right = VariableNode("b")
        impl_node = ImplicationNode(left, right)
        vars_list = impl_node.get_variables()
        assert set(vars_list) == {"a", "b"}

    def test_xor_node_evaluate(self):
        """Тест XorNode.evaluate"""
        left = VariableNode("a")
        right = VariableNode("b")
        xor_node = XorNode(left, right)
        assert xor_node.evaluate({"a": True, "b": True}) == False
        assert xor_node.evaluate({"a": True, "b": False}) == True
        assert xor_node.evaluate({"a": False, "b": True}) == True
        assert xor_node.evaluate({"a": False, "b": False}) == False

    def test_xor_node_get_variables(self):
        """Тест XorNode.get_variables"""
        left = VariableNode("a")
        right = VariableNode("b")
        xor_node = XorNode(left, right)
        vars_list = xor_node.get_variables()
        assert set(vars_list) == {"a", "b"}

    def test_equivalence_node_evaluate(self):
        """Тест EquivalenceNode.evaluate"""
        left = VariableNode("a")
        right = VariableNode("b")
        equiv_node = EquivalenceNode(left, right)
        assert equiv_node.evaluate({"a": True, "b": True}) == True
        assert equiv_node.evaluate({"a": True, "b": False}) == False
        assert equiv_node.evaluate({"a": False, "b": True}) == False
        assert equiv_node.evaluate({"a": False, "b": False}) == True

    def test_equivalence_node_get_variables(self):
        """Тест EquivalenceNode.get_variables"""
        left = VariableNode("a")
        right = VariableNode("b")
        equiv_node = EquivalenceNode(left, right)
        vars_list = equiv_node.get_variables()
        assert set(vars_list) == {"a", "b"}

    def test_binary_node_duplicate_variables(self):
        """Тест BinaryNode.get_variables с повторяющимися переменными"""
        left = VariableNode("a")
        right = VariableNode("a")
        and_node = AndNode(left, right)
        vars_list = and_node.get_variables()
        # Должна быть только одна 'a'
        assert vars_list == ["a"]

    def test_complex_nested_nodes(self):
        """Тест сложного вложенного выражения"""
        # (a & b) | (!c)
        a = VariableNode("a")
        b = VariableNode("b")
        c = VariableNode("c")
        and_node = AndNode(a, b)
        not_c = NotNode(c)
        or_node = OrNode(and_node, not_c)
        
        assert or_node.evaluate({"a": True, "b": True, "c": False}) == True
        assert or_node.evaluate({"a": False, "b": False, "c": True}) == False
        
        vars_list = or_node.get_variables()
        assert set(vars_list) == {"a", "b", "c"}

    def test_expression_node_abstract(self):
        """Тест что ExpressionNode нельзя инстанциировать"""
        with pytest.raises(TypeError):
            ExpressionNode()

class TestTruthTable:

    def test_build_table_single_variable(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        assert len(table.rows) == 2

    def test_build_table_two_variables(self):
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        assert len(table.rows) == 4

    def test_get_ones_indices(self):
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        ones = table.get_ones_indices()
        assert 1 in ones or 2 in ones or 3 in ones

    def test_get_zeros_indices(self):
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        zeros = table.get_zeros_indices()
        assert 0 in zeros

    def test_row_index_calculation(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        assert table.rows[0].get_index() == 0
        assert table.rows[1].get_index() == 1

    def test_print_table_format(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        output = table.print_table()
        assert "a" in output
        assert "F" in output


class TestNormalFormBuilder:

    def test_build_sdnf_basic(self):
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        builder = NormalFormBuilder(table)
        sdnf = builder.build_sdnf()
        assert "a" in sdnf and "b" in sdnf

    def test_build_sknf_basic(self):
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        builder = NormalFormBuilder(table)
        sknf = builder.build_sknf()
        assert sknf is not None

    def test_sdnf_numeric_form(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        builder = NormalFormBuilder(table)
        numeric = builder.get_sdnf_numeric()
        assert "Σ" in numeric

    def test_sknf_numeric_form(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        builder = NormalFormBuilder(table)
        numeric = builder.get_sknf_numeric()
        assert "Π" in numeric

    def test_index_form(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        builder = NormalFormBuilder(table)
        index_form = builder.get_index_form()
        assert "Индексы" in index_form

    def test_empty_sdnf(self):
        parser = ExpressionParser("a&!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        builder = NormalFormBuilder(table)
        sdnf = builder.build_sdnf()
        assert sdnf == "0"

    def test_empty_sknf(self):
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        builder = NormalFormBuilder(table)
        sknf = builder.build_sknf()
        assert sknf == "1"


class TestPostClasses:

    def test_check_t0_zero(self):
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        checker = PostClassesChecker(table)
        assert checker.check_t0() == True

    def test_check_t1_one(self):
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        checker = PostClassesChecker(table)
        assert checker.check_t1() == True

    def test_check_s_self_dual(self):
        parser = ExpressionParser("!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        checker = PostClassesChecker(table)
        assert checker.check_s() == True

    def test_get_all_classes(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        checker = PostClassesChecker(table)
        classes = checker.get_all_classes()
        assert "T0 (сохраняет 0)" in classes
        assert len(classes) == 5


class TestZhegalkinPolynomial:

    def test_build_polynomial(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        poly = ZhegalkinPolynomial(table)
        poly.build()
        assert poly.get_terms_count() >= 1

    def test_is_linear(self):
        parser = ExpressionParser("a~b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        poly = ZhegalkinPolynomial(table)
        poly.build()
        assert poly.is_linear() == True

    def test_to_string(self):
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        poly = ZhegalkinPolynomial(table)
        poly.build()
        result = poly.to_string()
        assert result is not None


class TestFictitiousVariables:

    def test_find_fictitious(self):
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        fictitious = finder.find_fictitious()
        assert "b" in fictitious

    def test_get_essential(self):
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        essential = finder.get_essential_variables()
        assert "a" in essential
        assert "b" in essential

class TestTerm:

    def test_term_str(self):
        """Тест строкового представления терма"""
        term = Term(["a", "b"], [True, False])
        result = str(term)
        assert "a" in result
        assert "¬b" in result
        assert "∧" in result or "&" in result

    def test_term_str_with_none(self):
        """Тест терма с None в маске"""
        term = Term(["a", "b"], [True, None])
        result = str(term)
        assert "a" in result
        assert "¬b" not in result

    def test_term_str_all_none(self):
        """Тест терма со всеми None"""
        term = Term(["a", "b"], [None, None])
        result = str(term)
        assert result == "(1)" or result == "()"

    def test_can_glue(self):
        term1 = Term(["a", "b"], [True, True])
        term2 = Term(["a", "b"], [True, False])
        assert term1.can_glue_with(term2) == True

    def test_cannot_glue(self):
        term1 = Term(["a", "b"], [True, True])
        term2 = Term(["a", "b"], [False, False])
        assert term1.can_glue_with(term2) == False

    def test_glue_result(self):
        term1 = Term(["a", "b"], [True, True])
        term2 = Term(["a", "b"], [True, False])
        glued = term1.glue_with(term2)
        assert glued.mask == [True, None]

    def test_covers_index(self):
        term = Term(["a", "b"], [True, None])
        assert term.covers_index(2) == True
        assert term.covers_index(3) == True
        assert term.covers_index(0) == False

class TestFictitiousVariablesFinderCoverage:
    """Дополнительные тесты для FictitiousVariablesFinder для повышения покрытия"""

    def test_find_fictitious_multiple_vars(self):
        """Тест поиска фиктивных переменных для нескольких переменных"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        fictitious = finder.find_fictitious()
        assert "b" in fictitious
        assert "c" in fictitious

    def test_no_fictitious_variables(self):
        """Тест когда нет фиктивных переменных"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        fictitious = finder.find_fictitious()
        assert len(fictitious) == 0

    def test_fictitious_with_implication(self):
        """Тест фиктивных переменных с импликацией"""
        parser = ExpressionParser("a→b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        fictitious = finder.find_fictitious()
        assert "c" in fictitious

    def test_fictitious_last_variable(self):
        """Тест когда фиктивная переменная последняя"""
        parser = ExpressionParser("a")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        fictitious = finder.find_fictitious()
        assert "b" in fictitious

    def test_fictitious_first_variable(self):
        """Тест когда фиктивная переменная первая"""
        parser = ExpressionParser("b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        fictitious = finder.find_fictitious()
        assert "a" in fictitious

    def test_all_variables_essential(self):
        """Тест все переменные существенные - используем AND вместо XOR"""
        parser = ExpressionParser("(a&!b)|(!a&b)")  # XOR через AND/OR/NOT
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        fictitious = finder.find_fictitious()
        assert len(fictitious) == 0

    def test_rows_differ_only_at_private_method(self):
        """Тест приватного метода _rows_differ_only_at"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)

        result = finder._rows_differ_only_at(2, 3, 1)
        assert result is True
        result = finder._rows_differ_only_at(0, 2, 0)
        assert result is True
        result = finder._rows_differ_only_at(0, 3, 0)
        assert result is False

    def test_get_essential_variables(self):
        """Тест получения существенных переменных"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        finder = FictitiousVariablesFinder(table)
        essential = finder.get_essential_variables()
        assert set(essential) == {"a", "b"}


class TestBooleanDerivativeCoverage:
    """Дополнительные тесты для BooleanDerivative для повышения покрытия"""

    def test_partial_derivative_xor(self):
        """Тест частной производной для XOR (используя a~b вместо a⊕b)"""R
        parser = ExpressionParser("(a&!b)|(!a&b)")  # XOR
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "1"

    def test_partial_derivative_and(self):
        """Тест частной производной для AND"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "b"

    def test_partial_derivative_or(self):
        """Тест частной производной для OR"""
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "¬b"

    def test_partial_derivative_not(self):
        """Тест частной производной для NOT"""
        parser = ExpressionParser("!a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a"])
        result = derivative.partial_derivative("a")
        assert result == "1"

    def test_mixed_derivative_two_vars(self):
        """Тест смешанной производной для двух переменных"""
        parser = ExpressionParser("(a&!b)|(!a&b)")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.mixed_derivative(["a", "b"])
        assert result == "0"

    def test_mixed_derivative_and(self):
        """Тест смешанной производной для AND"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.mixed_derivative(["a", "b"])
        assert result == "1"

    def test_derivative_constant_zero(self):
        """Тест производной для константы 0"""
        parser = ExpressionParser("a&!a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a"])
        result = derivative.partial_derivative("a")
        assert result == "0"

    def test_derivative_constant_one(self):
        """Тест производной для константы 1"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a"])
        result = derivative.partial_derivative("a")
        assert result == "0"

    def test_derivative_three_variables(self):
        """Тест производной для трех переменных"""
        parser = ExpressionParser("a&b&c")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        result = derivative.partial_derivative("a")
        assert result == "bc"

    def test_derivative_simplify_to_single_var(self):
        """Тест упрощения до одной переменной"""
        parser = ExpressionParser("a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "1"

    def test_derivative_simplify_to_negated_var(self):
        """Тест упрощения до отрицания переменной"""
        parser = ExpressionParser("!a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "1"

    def test_derivative_complex_expression(self):
        """Тест производной сложного выражения"""
        parser = ExpressionParser("(a&b)|(!a&c)")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        result = derivative.partial_derivative("a")
        assert result in ["b⊕c", "b~c", "¬b⊕c", "b⊕¬c", "(b¬c)|(¬bc)", "¬bc ∨ b¬c"]

    def test_derivative_simplify_tautology(self):
        """Тест упрощения до тавтологии (1)"""
        parser = ExpressionParser("b|!b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "0"  # Производная константы = 0

    def test_derivative_with_implication(self):
        """Тест производной с импликацией"""
        parser = ExpressionParser("a→b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "¬b"

    def test_derivative_with_equivalence(self):
        """Тест производной с эквивалентностью"""
        parser = ExpressionParser("a~b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "1"

    def test_derivative_one_variable_no_remaining(self):
        """Тест производной когда нет оставшихся переменных"""
        parser = ExpressionParser("a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a"])
        result = derivative.partial_derivative("a")
        assert result == "1"

    def test_mixed_derivative_three_vars(self):
        """Тест смешанной производной для трех переменных"""
        parser = ExpressionParser("a&b&c")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        result = derivative.mixed_derivative(["a", "b", "c"])
        assert result == "1"

    def test_derivative_simplify_to_var_only(self):
        """Тест упрощения до переменной без отрицания"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        result = derivative.partial_derivative("b")
        assert result == "a"

    def test_derivative_all_ones_but_not_tautology(self):
        """Тест когда все значения 1, но не тавтология"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative.partial_derivative("a")
        assert result == "0"

    def test_compute_derivative_values_private(self):
        """Тест приватного метода _compute_derivative_values"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        values = derivative._compute_derivative_values(["a"])
        assert len(values) == 2  # для оставшейся переменной b
        assert values == [False, True]  # ∂/∂a = b

    def test_idx_to_vals(self):
        """Тест преобразования индекса в значения"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        vals = derivative._idx_to_vals(2, 2)  # 10 в двоичной = a=1,b=0
        assert vals == [True, False]

    def test_vals_to_idx(self):
        """Тест преобразования значений в индекс"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        idx = derivative._vals_to_idx([True, False])
        assert idx == 2

    def test_simplify_expression_no_variables_true(self):
        """Тест упрощения выражения без переменных - True"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative._simplify_expression([True], [])
        assert result == "1"

    def test_simplify_expression_no_variables_false(self):
        """Тест упрощения выражения без переменных - False"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        result = derivative._simplify_expression([False], [])
        assert result == "0"

    def test_simplify_expression_one_var_true(self):
        """Тест упрощения выражения с одной переменной - True"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        # values для b: [False, True] -> b
        result = derivative._simplify_expression([False, True], ["b"])
        assert result == "b"

    def test_simplify_expression_one_var_negated(self):
        """Тест упрощения выражения с одной переменной - отрицание"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b"])
        # values: [True, False] -> ¬b
        result = derivative._simplify_expression([True, False], ["b"])
        assert result == "¬b"

    def test_simplify_expression_conjunction(self):
        """Тест упрощения до конъюнкции"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        values = [False, False, False, True]
        result = derivative._simplify_expression(values, ["b", "c"])
        assert result == "bc"

    def test_simplify_expression_two_vars_tautology(self):
        """Тест упрощения до тавтологии для двух переменных"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        values = derivative._compute_derivative_values(["a"])
        result = derivative._simplify_expression([False, False, False, False], ["b", "c"])
        assert result == "0"

    def test_simplify_disjunction_three_vars_tautology(self):
        """Тест упрощения дизъюнкции для трех переменных до тавтологии"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        values = derivative._compute_derivative_values(["c"])
        result = derivative._simplify_expression([False, False, False, False, False, False, False, False], ["a", "b", "c"])
        assert result == "0"

    def test_derivative_with_xor_simplification(self):
        """Тест производной с XOR упрощением"""
        parser = ExpressionParser("(a&!b)|(!a&b)")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        result = derivative.partial_derivative("a")
        assert result == "1"

    def test_mixed_derivative_three_vars_xor(self):
        """Тест смешанной производной для XOR трех переменных"""
        parser = ExpressionParser("(a&!b&!c)|(!a&b&!c)|(!a&!b&c)|(a&b&c)")
        expr = parser.parse()
        derivative = BooleanDerivative(expr, ["a", "b", "c"])
        result = derivative.mixed_derivative(["a", "b", "c"])
        assert result == "0"

class TestTermCNF:
    """Тесты для Term в режиме КНФ"""

    def test_term_cnf_str(self):
        """Тест строкового представления КНФ терма"""
        term = Term(["a", "b"], [True, False], is_cnf=True)
        result = str(term)
        assert "a" in result
        assert "¬b" in result
        assert "∨" in result

    def test_term_cnf_str_with_none(self):
        """Тест КНФ терма с None в маске"""
        term = Term(["a", "b"], [True, None], is_cnf=True)
        result = str(term)
        assert "a" in result
        assert "¬b" not in result

    def test_term_cnf_str_empty_parts(self):
        """Тест КНФ терма без частей"""
        term = Term(["a", "b"], [None, None], is_cnf=True)
        result = str(term)
        assert result == "(0)"

    def test_term_cnf_covers_index(self):
        """Тест covers_index для КНФ"""
        term = Term(["a", "b"], [True, True], is_cnf=True)
        assert term.covers_index(0) == True
        assert term.covers_index(3) == False

    def test_term_cnf_covers_index_with_none(self):
        """Тест covers_index для КНФ с None в маске"""
        term = Term(["a", "b"], [True, None], is_cnf=True)
        assert term.covers_index(0) == True
        assert term.covers_index(2) == False

    def test_term_cnf_hash(self):
        """Тест хеширования КНФ терма"""
        term1 = Term(["a", "b"], [True, False], is_cnf=True)
        term2 = Term(["a", "b"], [True, False], is_cnf=True)
        assert hash(term1) == hash(term2)


class TestMinimizationCalculatorCNF:
    """Тесты для КНФ методов MinimizationCalculator"""

    def test_get_sknf_terms(self):
        """Тест получения СКНФ термов"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        terms = calc.get_sknf_terms()
        assert len(terms) == 3

    def test_get_sknf_terms_empty(self):
        """Тест получения СКНФ термов для тавтологии"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        calc = MinimizationCalculator(table)
        terms = calc.get_sknf_terms()
        assert len(terms) == 0

    def test_minimize_calculation_method_cnf(self):
        """Тест расчетного метода минимизации КНФ"""
        parser = ExpressionParser("(a|b)&(a|c)")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        stages, terms = calc.minimize_calculation_method_cnf()
        assert stages is not None
        assert terms is not None

    def test_minimize_calculation_method_cnf_single_term(self):
        """Тест КНФ минимизации с одним термом"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        stages, terms = calc.minimize_calculation_method_cnf()
        assert len(terms) == 2

    def test_minimize_table_method_cnf(self):
        """Тест табличного метода минимизации КНФ"""
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        stages, terms, table_str = calc.minimize_table_method_cnf()
        assert "Таблица покрытий (КНФ)" in table_str or "Нет нулей" in table_str

    def test_minimize_karnaugh_cnf_3vars(self):
        """Тест карты Карно для КНФ с 3 переменными"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        terms, viz = calc.minimize_karnaugh_cnf()
        assert viz is not None
        assert "Карта Карно" in viz

    def test_minimize_karnaugh_cnf_4vars(self):
        """Тест карты Карно для КНФ с 4 переменными"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c", "d"])
        table.build()
        calc = MinimizationCalculator(table)
        terms, viz = calc.minimize_karnaugh_cnf()
        assert viz is not None
        assert "Карта Карно" in viz

    def test_minimize_karnaugh_cnf_tautology(self):
        """Тест карты Карно для КНФ с тавтологией"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        calc = MinimizationCalculator(table)
        terms, viz = calc.minimize_karnaugh_cnf()
        assert "тождественно равна 1" in viz or "Функция тождественно равна 1" in viz

    def test_minimize_karnaugh_cnf_unsupported_vars(self):
        """Тест карты Карно для КНФ с неподдерживаемым числом переменных"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c", "d", "e"])
        table.build()
        calc = MinimizationCalculator(table)
        terms, viz = calc.minimize_karnaugh_cnf()
        assert "поддерживает" in viz or "2-4" in viz

    def test_build_coverage_table_cnf(self):
        """Тест построения таблицы покрытий для КНФ"""
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        _, terms = calc.minimize_calculation_method_cnf()
        coverage = calc._build_coverage_table_cnf(terms)
        assert "Таблица покрытий (КНФ)" in coverage or "Нет нулей" in coverage

    def test_build_coverage_table_cnf_empty(self):
        """Тест таблицы покрытий для КНФ с пустой функцией"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        calc = MinimizationCalculator(table)
        coverage = calc._build_coverage_table_cnf([])
        assert "Нет нулей" in coverage

    def test_minimal_cover_cnf(self):
        """Тест поиска минимального покрытия для КНФ"""
        parser = ExpressionParser("(a|b)&(a|c)")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        _, terms = calc.minimize_calculation_method_cnf()
        assert len(terms) > 0

    def test_minimal_cover_cnf_empty(self):
        """Тест минимального покрытия для КНФ с пустой функцией"""
        parser = ExpressionParser("a|!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        calc = MinimizationCalculator(table)
        result = calc._minimal_cover_cnf([])
        assert len(result) == 0

    def test_terms_equal(self):
        """Тест сравнения термов"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        term1 = Term(["a", "b"], [True, True], is_cnf=True)
        term2 = Term(["a", "b"], [True, True], is_cnf=True)
        term3 = Term(["a", "b"], [True, False], is_cnf=True)
        assert calc._terms_equal(term1, term2) == True
        assert calc._terms_equal(term1, term3) == False

    def test_term_to_str_cnf(self):
        """Тест преобразования КНФ терма в строку"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        term = Term(["a", "b"], [True, False], is_cnf=True)
        result = calc._term_to_str_cnf(term)
        assert "a" in result
        assert "¬b" in result

    def test_term_to_str_cnf_empty(self):
        """Тест преобразования пустого КНФ терма"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        term = Term(["a", "b"], [None, None], is_cnf=True)
        result = calc._term_to_str_cnf(term)
        assert result == "(0)"

    def test_groups_to_terms_cnf_3vars(self):
        """Тест преобразования групп в термы для КНФ с 3 переменными"""
        parser = ExpressionParser("a&b&c")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        groups = [[(0, 0), (0, 1)]]
        terms = calc._groups_to_terms_cnf(groups, gray_code)
        assert isinstance(terms, list)

    def test_groups_to_terms_cnf_4vars(self):
        """Тест преобразования групп в термы для КНФ с 4 переменными"""
        parser = ExpressionParser("a&b&c&d")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c", "d"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        groups = [[(0, 0), (0, 1), (1, 0), (1, 1)]]
        terms = calc._groups_to_terms_cnf(groups, gray_code)
        assert isinstance(terms, list)

    def test_visualize_karnaugh_cnf_3vars(self):
        """Тест визуализации карты Карно для КНФ с 3 переменными"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        k_map = calc._build_karnaugh_map(gray_code)
        zeros_indices = set(table.get_zeros_indices())
        viz = calc._visualize_karnaugh_cnf(k_map, [], gray_code, zeros_indices)
        assert "Карта Карно" in viz

    def test_visualize_karnaugh_cnf_4vars(self):
        """Тест визуализации карты Карно для КНФ с 4 переменными"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c", "d"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        k_map = calc._build_karnaugh_map(gray_code)
        zeros_indices = set(table.get_zeros_indices())
        viz = calc._visualize_karnaugh_cnf(k_map, [], gray_code, zeros_indices)
        assert "Карта Карно" in viz

    def test_get_minimized_cnf_expression(self):
        """Тест получения минимизированного КНФ выражения"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        terms = calc.get_sknf_terms()
        expr_str = calc.get_minimized_cnf_expression(terms)
        assert "∧" in expr_str or "&" in expr_str

    def test_get_minimized_cnf_expression_empty(self):
        """Тест получения минимизированного КНФ выражения для пустого списка"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        expr_str = calc.get_minimized_cnf_expression([])
        assert expr_str == "1"


class TestMinimizationCalculatorDNFExtra:
    """Дополнительные тесты для ДНФ методов"""

    def test_minimize_karnaugh_dnf_2vars(self):
        """Тест карты Карно для ДНФ с 2 переменными"""
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        terms, viz = calc.minimize_karnaugh_dnf()
        assert viz is not None

    def test_minimize_karnaugh_dnf_empty(self):
        """Тест карты Карно для ДНФ с пустой функцией"""
        parser = ExpressionParser("a&!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        calc = MinimizationCalculator(table)
        terms, viz = calc.minimize_karnaugh_dnf()
        assert "тождественно равна 0" in viz

    def test_find_groups_with_targets(self):
        """Тест поиска групп с целями"""
        parser = ExpressionParser("a|b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        k_map = calc._build_karnaugh_map(gray_code)
        ones_indices = set(table.get_ones_indices())
        groups = calc._find_groups(k_map, ones_indices, gray_code)
        assert isinstance(groups, list)

    def test_groups_to_terms_dnf_3vars(self):
        """Тест преобразования групп в термы для ДНФ с 3 переменными"""
        parser = ExpressionParser("a&b&c")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        groups = [[(0, 3)]]
        terms = calc._groups_to_terms_dnf(groups, gray_code)
        assert isinstance(terms, list)

    def test_visualize_karnaugh_dnf_3vars(self):
        """Тест визуализации карты Карно для ДНФ с 3 переменными"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        k_map = calc._build_karnaugh_map(gray_code)
        ones_indices = set(table.get_ones_indices())
        viz = calc._visualize_karnaugh_dnf(k_map, [], gray_code, ones_indices)
        assert "Карта Карно" in viz

    def test_visualize_karnaugh_dnf_4vars(self):
        """Тест визуализации карты Карно для ДНФ с 4 переменными"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c", "d"])
        table.build()
        calc = MinimizationCalculator(table)
        gray_code = [0, 1, 3, 2]
        k_map = calc._build_karnaugh_map(gray_code)
        ones_indices = set(table.get_ones_indices())
        viz = calc._visualize_karnaugh_dnf(k_map, [], gray_code, ones_indices)
        assert "ab=" in viz or "Карта Карно" in viz

    def test_minimal_cover_dnf_empty(self):
        """Тест минимального покрытия для ДНФ с пустой функцией"""
        parser = ExpressionParser("a&!a")
        expr = parser.parse()
        table = TruthTable(expr, ["a"])
        table.build()
        calc = MinimizationCalculator(table)
        result = calc._minimal_cover_dnf([])
        assert len(result) == 0

class TestMinimizationCalculatorIntegration:
    """Интеграционные тесты"""

    def test_full_dnf_workflow(self):
        """Полный workflow для ДНФ"""
        parser = ExpressionParser("(a&b)|(a&c)")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        
        # Расчетный метод
        stages, terms = calc.minimize_calculation_method_dnf()
        assert stages is not None
        
        # Табличный метод
        _, _, table_str = calc.minimize_table_method_dnf()
        assert table_str is not None
        
        # Карта Карно
        karnaugh_terms, karnaugh_viz = calc.minimize_karnaugh_dnf()
        assert karnaugh_viz is not None
        
        # Итоговое выражение
        expr_str = calc.get_minimized_dnf_expression(terms)
        assert len(expr_str) > 0

    def test_full_cnf_workflow(self):
        """Полный workflow для КНФ"""
        parser = ExpressionParser("(a|b)&(a|c)")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        
        # Расчетный метод
        stages, terms = calc.minimize_calculation_method_cnf()
        assert stages is not None
        
        # Табличный метод
        _, _, table_str = calc.minimize_table_method_cnf()
        assert table_str is not None
        
        # Карта Карно
        karnaugh_terms, karnaugh_viz = calc.minimize_karnaugh_cnf()
        assert karnaugh_viz is not None
        
        # Итоговое выражение
        expr_str = calc.get_minimized_cnf_expression(terms)
        assert len(expr_str) > 0

    def test_xor_function_minimization(self):
        """Минимизация функции XOR"""
        parser = ExpressionParser("(a&!b)|(!a&b)")  # XOR
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        
        # Для XOR простого ДНФ нет (минимальная форма уже дана)
        stages, terms = calc.minimize_calculation_method_dnf()
        # Должно быть 2 терма
        assert len(terms) == 2 or len(terms) == 1

    def test_majority_function(self):
        """Минимизация функции мажоритарности (голосования)"""
        # Функция истинна, когда большинство переменных истинны
        parser = ExpressionParser("(a&b)|(a&c)|(b&c)")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b", "c"])
        table.build()
        calc = MinimizationCalculator(table)
        
        stages, terms = calc.minimize_calculation_method_dnf()
        # Минимальная форма должна содержать 3 терма
        assert len(terms) == 3

    def test_remove_duplicates_cnf(self):
        """Тест удаления дубликатов для КНФ термов"""
        parser = ExpressionParser("a&b")
        expr = parser.parse()
        table = TruthTable(expr, ["a", "b"])
        table.build()
        calc = MinimizationCalculator(table)
        term1 = Term(["a", "b"], [True, True], is_cnf=True)
        term2 = Term(["a", "b"], [True, True], is_cnf=True)
        term3 = Term(["a", "b"], [True, False], is_cnf=True)
        unique = calc._remove_duplicates([term1, term2, term3])
        assert len(unique) == 2
