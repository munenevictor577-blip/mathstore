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


def test_normalize_ode_natural_language(solver: ODESolver) -> None:
    # y'(x) notation (Bug 1 regression)
    sol1 = solver.solve("y'(x) + 2*y(x) = 0")
    assert "C1" in sol1
    assert "exp(-2*x)" in sol1

    # Implicit multiplication with coefficient: 2x + 6y' = 0
    sol2 = solver.solve("2x + 6y' = 0")
    assert "C1" in sol2
    assert "x**2/6" in sol2

    # 2y' + 4y = 0
    sol3 = solver.solve("2y' + 4y = 0")
    assert "exp(-2*x)" in sol3

    # y''(x) + 4y(x) = 0
    sol4 = solver.solve("y''(x) + 4y(x) = 0")
    assert "sin(2*x)" in sol4

    # Juxtaposed variables: y' = 2xy
    sol5 = solver.solve("y' = 2xy")
    assert "C1" in sol5
    assert "exp(x**2)" in sol5

    # xy' + y = 0
    sol6 = solver.solve("xy' + y = 0")
    assert "C1/x" in sol6


def test_parse_equation_extended(solver: ODESolver) -> None:
    x = sp.Symbol("x")
    y = sp.Function("y")
    # sp.Expr passed directly
    eq_expr = solver.parse_equation(sp.Derivative(y(x), x) + 2 * y(x))
    assert isinstance(eq_expr, sp.Eq)

    # Syntax error in equation
    with pytest.raises(ValueError, match="Failed to parse differential equation"):
        solver.parse_equation("y' +* 2 = 0")

    # Unsupported type
    with pytest.raises(TypeError, match="Unsupported equation type"):
        solver.parse_equation(12345)  # type: ignore[arg-type]


def test_parse_ics_extended(solver: ODESolver) -> None:
    x = sp.Symbol("x")
    y = sp.Function("y")
    # sp.Basic key in dict
    ics_sym = solver.parse_ics({y(0): 1})
    assert ics_sym == {y(0): sp.Integer(1)}

    # Invalid key type in dict
    with pytest.raises(TypeError, match="Invalid initial condition key type"):
        solver.parse_ics({None: 1})

    # Unsupported ics input type
    with pytest.raises(TypeError, match="Unsupported initial conditions type"):
        solver.parse_ics([1, 2])

    # Unparseable ics format
    with pytest.raises(ValueError, match="Could not parse initial condition specification"):
        solver.parse_ics("y[0] = 1")

    # Higher order Leibniz initial condition
    ics_leibniz = solver.parse_ics("d^2y/dx^2(0) = 2")
    assert len(ics_leibniz) == 1


def test_classify_extended_heuristics(solver: ODESolver) -> None:
    from unittest.mock import patch

    # Bernoulli
    c_bern = solver.classify("y' + y = x*y**2")
    assert "Bernoulli" in c_bern["primary_type"]

    # Exact
    c_exact = solver.classify("(2*x*y + y**2) + (x**2 + 2*x*y)*y' = 0")
    assert "Exact" in c_exact["primary_type"]

    # Variation of Parameters
    c_vop = solver.classify("y'' + y = sec(x)")
    assert "Variation of Parameters" in c_vop["primary_type"]

    # Undetermined coefficients
    c_und = solver.classify("y'' + 4*y = exp(x)")
    assert "Undetermined Coefficients" in c_und["primary_type"]

    # Homogeneous coeff
    c_hom = solver.classify("y' = (y**2 + 2*x**2)/(x*y + x**2)")
    assert "Homogeneous First-Order ODE" in c_hom["primary_type"]

    # Linear ODE fallback
    c_lin = solver.classify("x**3*y''' + x**2*y'' + x*y' + y = 0")
    assert "Linear Differential Equation" in c_lin["primary_type"]

    # Exception in classify_ode
    with patch("mathstore.ode.solver.classify_ode", side_effect=RuntimeError("SymPy error")):
        c_err = solver.classify("y' + 2*y = 0")
        assert c_err["hints"] == []


def test_is_linear_and_homogeneous_extended(solver: ODESolver) -> None:
    x = sp.Symbol("x")
    dummy_eq = sp.Eq(x, 0)
    from unittest.mock import patch
    with patch.object(solver, "parse_equation", return_value=dummy_eq):
        assert solver.is_linear("dummy = 0") is False
        assert solver.is_homogeneous("dummy = 0") is False


def test_solve_extended(solver: ODESolver) -> None:
    from unittest.mock import patch

    # Custom hint
    sol = solver.solve("y' = 2*x*y", hint="separable")
    assert "exp(x**2)" in sol

    # Exception in dsolve
    with patch("mathstore.ode.solver.sp.dsolve", side_effect=RuntimeError("dsolve error")):
        with pytest.raises(ValueError, match="Unable to find an analytical solution"):
            solver.solve("y' + 2*y = 0")


def test_check_solution_extended(solver: ODESolver) -> None:
    from unittest.mock import patch

    x = sp.Symbol("x")
    y = sp.Function("y")
    # sp.Eq
    assert solver.check_solution("y' + 2*y = 0", sp.Eq(y(x), 3 * sp.exp(-2 * x))) is True

    # sp.Expr
    assert solver.check_solution("y' + 2*y = 0", 3 * sp.exp(-2 * x)) is True

    # int / float
    assert solver.check_solution("y' = 0", 5) is True

    # y = ... natural syntax (Bug 2 regression)
    assert solver.check_solution("y' + 2*y = 0", "y = 3*exp(-2*x)") is True
    assert solver.check_solution("y' + 2*y = 0", "y = C1*exp(-2*x)") is True
    assert solver.check_solution("y' + 2*y = 0", "2*y(x) = 6*exp(-2*x)") is True

    # Implicit multiplication in solution
    assert solver.check_solution("y' + 2*y = 0", "3exp(-2x)") is True

    # Unsupported solution type
    with pytest.raises(ValueError, match="Unsupported solution type"):
        solver.check_solution("y' = 0", [1, 2])  # type: ignore[arg-type]

    # checkodesol exception
    with patch("mathstore.ode.solver.checkodesol", side_effect=RuntimeError("check error")):
        assert solver.check_solution("y' + 2*y = 0", "3*exp(-2*x)") is False


def test_format_solution_extended(solver: ODESolver) -> None:
    sol_eq = solver.solve("y' + 2*y = 0", format="sympy")
    x = sp.Symbol("x")
    expr_sol = 3 * sp.exp(-2 * x)

    # List of solutions
    list_res = solver.format_solution([sol_eq], format="str")
    assert isinstance(list_res, list)

    # Non-Eq solution in latex, pretty, str
    assert "e^{- 2 x}" in solver.format_solution(expr_sol, format="latex")
    assert "ℯ" in solver.format_solution(expr_sol, format="pretty") or "e" in solver.format_solution(expr_sol, format="pretty")
    assert "exp" in solver.format_solution(expr_sol, format="str")
