import pytest

from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer


@pytest.fixture
def solver() -> EquationSolver:
    """Fixture providing a fresh instance of EquationSolver."""
    return EquationSolver()


@pytest.fixture
def analyzer() -> CalculusAnalyzer:
    """Fixture providing a fresh instance of CalculusAnalyzer."""
    return CalculusAnalyzer()
