from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class ExpressionNode(ABC):
    """Базовый класс для узла выражения"""

    @abstractmethod
    def evaluate(self, variables: Dict[str, bool]) -> bool:
        pass

    @abstractmethod
    def get_variables(self) -> List[str]:
        pass


class VariableNode(ExpressionNode):
    """Узел переменной (a, b, c...)"""

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, variables: Dict[str, bool]) -> bool:
        return variables.get(self.name, False)

    def get_variables(self) -> List[str]:
        return [self.name]


class NotNode(ExpressionNode):
    """Узел отрицания (!)"""

    def __init__(self, operand: ExpressionNode):
        self.operand = operand

    def evaluate(self, variables: Dict[str, bool]) -> bool:
        return not self.operand.evaluate(variables)

    def get_variables(self) -> List[str]:
        return self.operand.get_variables()


class BinaryNode(ExpressionNode):
    """Базовый класс для бинарных операций"""

    def __init__(self, left: ExpressionNode, right: ExpressionNode):
        self.left = left
        self.right = right

    def get_variables(self) -> List[str]:
        left_vars = self.left.get_variables()
        right_vars = self.right.get_variables()
        return list(set(left_vars + right_vars))


class AndNode(BinaryNode):
    """Конъюнкция (&)"""

    def evaluate(self, variables: Dict[str, bool]) -> bool:
        return self.left.evaluate(variables) and self.right.evaluate(variables)


class OrNode(BinaryNode):
    """Дизъюнкция (|)"""

    def evaluate(self, variables: Dict[str, bool]) -> bool:
        return self.left.evaluate(variables) or self.right.evaluate(variables)


class ImplicationNode(BinaryNode):
    """Импликация (→)"""

    def evaluate(self, variables: Dict[str, bool]) -> bool:
        left = self.left.evaluate(variables)
        right = self.right.evaluate(variables)
        return (not left) or right


class XorNode(BinaryNode):
    """Исключающее ИЛИ (~)"""

    def evaluate(self, variables: Dict[str, bool]) -> bool:
        left = self.left.evaluate(variables)
        right = self.right.evaluate(variables)
        return left != right
    
class EquivalenceNode(BinaryNode):
    """Эквивалентность (~)"""

    def evaluate(self, variables: Dict[str, bool]) -> bool:
        left = self.left.evaluate(variables)
        right = self.right.evaluate(variables)
        return left == right