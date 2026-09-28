"""Unit tests for ODESolver."""

import pytest
import sympy as sp

from mathstore.ode.solver import ODESolver


@pytest.fixture
def solver() -> ODESolver:
    return ODESolver()


def test_ode_solver_init(solver: ODESolver) -> None:
    assert solver.default_var == "x"
    assert solver.default_func == "y"


def test_normalize_ode_string(solver: ODESolver) -> None:
    # Prime notation
    assert "Derivative(y(x), x)" in solver.normalize_ode_string("y' + 2*y = exp(x)")
    assert "Derivative(y(x), x, 2)" in solver.normalize_ode_string("y'' + 4*y = 0")
    assert "Derivative(y(x), x, 3)" in solver.normalize_ode_string("y''' - y = 0")

    # Leibniz notation
    assert "Derivative(y(x), x)" in solver.normalize_ode_string("dy/dx + 2*y = exp(x)")
    assert "Derivative(y(x), x, 2)" in solver.normalize_ode_string("d2y/dx2 + 4*y = 0")
    assert "Derivative(y(x), x, 2)" in solver.normalize_ode_string("d^2y/dx^2 + 4*y = 0")

    # Bare y converted to y(x)
    assert "y(x)" in solver.normalize_ode_string("y' + 2*y = 0")

    # Implicit equation (no '=') appends '= 0'
    res = solver.normalize_ode_string("y' + 2*y")
    assert res.endswith("= 0")


def test_parse_equation_valid(solver: ODESolver) -> None:
    eq1 = solver.parse_equation("y' + 2*y = exp(x)")
    assert isinstance(eq1, sp.Eq)

    eq2 = solver.parse_equation("y'' + 4*y = 0")
    assert isinstance(eq2, sp.Eq)

    # Pass already existing sp.Eq
    assert solver.parse_equation(eq1) == eq1


def test_parse_equation_invalid(solver: ODESolver) -> None:
    # Empty string
    with pytest.raises(ValueError, match="cannot be empty"):
        solver.parse_equation("")

    # Multiple '=' signs
    with pytest.raises(ValueError, match="at most one '='"):
        solver.parse_equation("y' = 2*y = 3")

    # Algebraic equation with order 0 (no derivatives)
    with pytest.raises(ValueError, match="contains no derivatives"):
        solver.parse_equation("2*x + 4 = 10")


def test_parse_ics(solver: ODESolver) -> None:
    # String format
    ics1 = solver.parse_ics("y(0) = 1")
    assert ics1 is not None
    assert len(ics1) == 1

    ics2 = solver.parse_ics("y(0) = 1, y'(0) = 2")
    assert ics2 is not None
    assert len(ics2) == 2

    # Semicolon separator
    ics3 = solver.parse_ics("y(0) = 1; y'(0) = 2")
    assert ics3 is not None
    assert len(ics3) == 2

    # Numeric dict format
    ics4 = solver.parse_ics({0: 1})
    assert ics4 is not None

    ics5 = solver.parse_ics({0: (1, 2)})
    assert ics5 is not None
    assert len(ics5) == 2

    # String-key dict format
    ics6 = solver.parse_ics({"y(0)": 1, "y'(0)": 2})
    assert ics6 is not None
    assert len(ics6) == 2

    # None input
    assert solver.parse_ics(None) is None

    # Invalid ics syntax
    with pytest.raises(ValueError, match="must contain '='"):
        solver.parse_ics("y(0)")


def test_order(solver: ODESolver) -> None:
    assert solver.order("y' + 2*y = 0") == 1
    assert solver.order("y'' + 4*y = 0") == 2
    assert solver.order("y''' - 6*y'' + 11*y' - 6*y = 0") == 3


def test_is_linear(solver: ODESolver) -> None:
    # Linear ODEs
    assert solver.is_linear("y' + 2*y = exp(x)") is True
    assert solver.is_linear("sin(x)*y' + cos(x)*y = 0") is True
    assert solver.is_linear("y'' + 4*y = 0") is True

    # Nonlinear ODEs
    assert solver.is_linear("y' + y**2 = 0") is False
    assert solver.is_linear("y' + sin(y) = 0") is False
    assert solver.is_linear("y' * y + 1 = 0") is False


def test_is_homogeneous(solver: ODESolver) -> None:
    assert solver.is_homogeneous("y' + 2*y = 0") is True
    assert solver.is_homogeneous("y'' + 4*y = 0") is True
    assert solver.is_homogeneous("y' + 2*y = exp(x)") is False
    assert solver.is_homogeneous("y'' + 4*y = 5") is False


def test_classify(solver: ODESolver) -> None:
    info1 = solver.classify("y' = 2*x*y")
    assert info1["order"] == 1
    assert "separable" in info1["hints"]
    assert "Separable" in info1["primary_type"]

    info2 = solver.classify("y' + 2*y = exp(x)")
    assert info2["order"] == 1
    assert info2["is_linear"] is True
    assert info2["is_homogeneous"] is False

    info3 = solver.classify("y'' + 4*y = 0")
    assert info3["order"] == 2
    assert info3["is_linear"] is True
    assert info3["is_homogeneous"] is True


def test_solve_first_order_separable(solver: ODESolver) -> None:
    sol = solver.solve("y' = 2*x*y")
    assert "C1" in sol
    assert "exp(x**2)" in sol


def test_solve_first_order_linear(solver: ODESolver) -> None:
    sol = solver.solve("y' + 2*y = 0")
    assert "C1" in sol
    assert "exp(-2*x)" in sol


def test_solve_second_order_homogeneous(solver: ODESolver) -> None:
    # y'' + 4*y = 0 -> sin(2x), cos(2x)
    sol = solver.solve("y'' + 4*y = 0")
    assert "sin(2*x)" in sol
    assert "cos(2*x)" in sol


def test_solve_ivp(solver: ODESolver) -> None:
    # 1st order IVP: y' + 2y = 0 with y(0) = 3
    sol1 = solver.solve("y' + 2*y = 0", ics="y(0) = 3")
    assert sol1 == "y(x) = 3*exp(-2*x)"

    # 2nd order IVP: y'' + 4y = 0 with y(0) = 1, y'(0) = 2
    sol2 = solver.solve("y'' + 4*y = 0", ics="y(0) = 1, y'(0) = 2")
    assert "sin(2*x)" in sol2
    assert "cos(2*x)" in sol2
    assert "C1" not in sol2
    assert "C2" not in sol2


def test_solve_custom_variable_and_func(solver: ODESolver) -> None:
    # Independent variable t, dependent function v
    sol = solver.solve("v' + 2*v = 0", var="t", func="v", ics="v(0) = 5")
    assert "v(t) = 5*exp(-2*t)" in sol


def test_check_solution(solver: ODESolver) -> None:
    # Valid solution
    assert solver.check_solution("y' + 2*y = 0", "3*exp(-2*x)") is True
    assert solver.check_solution("y' + 2*y = 0", "y(x) = 3*exp(-2*x)") is True

    # Invalid solution
    assert solver.check_solution("y' + 2*y = 0", "3*exp(2*x)") is False


def test_format_solution(solver: ODESolver) -> None:
    # Solve to get raw equality
    sol_eq = solver.solve("y' + 2*y = 0", format="sympy")
    assert isinstance(sol_eq, sp.Eq)

    # Format latex
    sol_latex = solver.format_solution(sol_eq, format="latex")
    assert "\\exp" in sol_latex or "e" in sol_latex

    # Format pretty
    sol_pretty = solver.format_solution(sol_eq, format="pretty")
    assert isinstance(sol_pretty, str)

    # Format rhs
    sol_rhs = solver.format_solution(sol_eq, format="rhs")
    assert "C1" in sol_rhs
    assert "y(x) =" not in sol_rhs
