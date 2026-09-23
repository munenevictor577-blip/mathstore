import anyio.abc
import anyio.from_thread
import pytest

# Map anyio.abc.BlockingPortal to anyio.from_thread.BlockingPortal (new standard)
# to resolve the upstream Starlette testclient import warning.
anyio.abc.BlockingPortal = anyio.from_thread.BlockingPortal

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
