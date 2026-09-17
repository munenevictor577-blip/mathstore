from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.core.matrix import MatrixAnalyzer
from mathstore.reference import get_reference, list_topics
from mathstore.statistics.analyzer import StatsAnalyzer


def main() -> None:
    print("Hello from mathstore!")


__all__ = [
    "CalculusAnalyzer",
    "EquationSolver",
    "MatrixAnalyzer",
    "StatsAnalyzer",
    "get_reference",
    "list_topics",
    "main",
]



