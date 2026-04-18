from typing import Optional, Tuple
from src.models import (
    ExpressionNode, VariableNode, NotNode,
    AndNode, OrNode, ImplicationNode, XorNode, EquivalenceNode
)


class ParserError(Exception):
    """Ошибка парсинга"""
    pass


class ExpressionParser:
    """Парсер логических выражений"""

    OPERATORS = {'&', '|', '!', '→', '~', '-', '>'}
    VARIABLES = set('abcde')

    def __init__(self, expression: str):
        self.expression = expression.replace(' ', '')
        self.position = 0

    def parse(self) -> ExpressionNode:
        """Точка входа парсера"""
        self.position = 0
        node = self._parse_equivalence()
        if self.position < len(self.expression):
            raise ParserError(f"Неожиданный символ: {self.expression[self.position]}")
        return node

    def _parse_equivalence(self) -> ExpressionNode:
        """Разбор эквивалентности (~) - САМЫЙ НИЗКИЙ приоритет"""
        node = self._parse_implication()
        while self._current_char() == '~':
            self._consume('~')
            node = EquivalenceNode(node, self._parse_implication())
        return node

    def _parse_implication(self) -> ExpressionNode:
        """Разбор импликации (->) - НИЗКИЙ приоритет"""
        node = self._parse_or()
        while True:
            if self._current_char() == '→':
                self._consume('→')
                node = ImplicationNode(node, self._parse_or())
            elif self._current_char() == '-':
                self._consume('-')
                if self._current_char() == '>':
                    self._consume('>')
                    node = ImplicationNode(node, self._parse_or())
                else:
                    raise ParserError("Ожидалось '>' после '-'")
            else:
                break
        return node

    def _parse_or(self) -> ExpressionNode:
        """Разбор дизъюнкции (|) - СРЕДНИЙ приоритет"""
        node = self._parse_and()
        while self._current_char() == '|':
            self._consume('|')
            node = OrNode(node, self._parse_and())
        return node

    def _parse_and(self) -> ExpressionNode:
        """Разбор конъюнкции (&) - ВЫСОКИЙ приоритет"""
        node = self._parse_unary()
        while self._current_char() == '&':
            self._consume('&')
            node = AndNode(node, self._parse_unary())
        return node

    def _parse_unary(self) -> ExpressionNode:
        """Разбор унарных операций (!) - ВЫСШИЙ приоритет"""
        if self._current_char() == '!':
            self._consume('!')
            return NotNode(self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> ExpressionNode:
        """Разбор первичных выражений (переменные, скобки)"""
        char = self._current_char()
        if char == '(':
            self._consume('(')
            node = self._parse_equivalence()
            self._consume(')')
            return node
        if char and char in self.VARIABLES:
            self._consume()
            return VariableNode(char)
        raise ParserError(f"Недопустимый символ: {char}")

    def _current_char(self) -> Optional[str]:
        if self.position < len(self.expression):
            return self.expression[self.position]
        return None

    def _consume(self, expected: str = None) -> str:
        char = self._current_char()
        if expected and char != expected:
            raise ParserError(f"Ожидалось '{expected}', получено '{char}'")
        self.position += 1
        return char