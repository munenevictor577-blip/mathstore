from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.reference import get_reference, list_topics


def main() -> None:
    print("Hello from mathstore!")


__all__ = [
    "CalculusAnalyzer",
    "EquationSolver",
    "get_reference",
    "list_topics",
    "main",
]


