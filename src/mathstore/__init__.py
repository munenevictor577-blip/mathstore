from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.core.matrix import MatrixAnalyzer
from mathstore.reference import get_reference, list_topics
from mathstore.statistics.analyzer import StatsAnalyzer
from mathstore.study import (
    PracticeQuestion,
    PracticeSession,
    generate_question,
    get_derivative_steps,
    get_equation_steps,
    get_integral_steps,
)


def main() -> None:
    print("Hello from mathstore!")


__all__ = [
    "CalculusAnalyzer",
    "EquationSolver",
    "MatrixAnalyzer",
    "PracticeQuestion",
    "PracticeSession",
    "StatsAnalyzer",
    "generate_question",
    "get_derivative_steps",
    "get_equation_steps",
    "get_integral_steps",
    "get_reference",
    "list_topics",
    "main",
]
