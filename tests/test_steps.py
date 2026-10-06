import pytest

from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.study.steps import (
    get_derivative_steps,
    get_equation_steps,
    get_integral_steps,
    get_ode_steps,
)


class TestDerivativeSteps:
    """Tests for derivative step-by-step breakdown."""

    def test_derivative_steps_polynomial(self):
        steps = get_derivative_steps("x**3 + 2*x", variable="x")
        assert len(steps) >= 3
        text = "\n".join(steps)
        assert "Sum Rule" in text
        assert "Power Rule" in text

    def test_derivative_steps_product(self):
        steps = get_derivative_steps("x**2 * sin(x)", variable="x")
        text = "\n".join(steps)
        assert "Product Rule" in text
        assert "sin(x)" in text
        assert "cos(x)" in text

    def test_derivative_steps_chain_trig(self):
        steps = get_derivative_steps("sin(3*x)", variable="x")
        text = "\n".join(steps)
        assert "Chain Rule" in text
        assert "cos" in text

    def test_derivative_steps_chain_exp(self):
        steps = get_derivative_steps("exp(2*x)", variable="x")
        text = "\n".join(steps)
        assert "Chain Rule" in text or "exp" in text

    def test_derivative_steps_log(self):
        steps = get_derivative_steps("log(x)", variable="x")
        text = "\n".join(steps)
        assert "1/x" in text or "log" in text

    def test_derivative_steps_constant(self):
        steps = get_derivative_steps("42", variable="x")
        text = "\n".join(steps)
        assert "constant" in text.lower() or "0" in text

    def test_derivative_steps_variable(self):
        steps = get_derivative_steps("x", variable="x")
        text = "\n".join(steps)
        assert "1" in text

    def test_derivative_steps_custom_variable(self):
        steps = get_derivative_steps("y**3", variable="y")
        text = "\n".join(steps)
        assert "d/dy" in text or "y" in text
        assert "3*y^2" in text or "3*y**2" in text

    def test_derivative_steps_higher_order(self):
        steps = get_derivative_steps("x**3", variable="x", order=2)
        text = "\n".join(steps)
        assert "order 1" in text.lower()
        assert "order 2" in text.lower()
        assert "6*x" in text

    def test_derivative_steps_invalid_syntax(self):
        with pytest.raises(ValueError, match="Could not parse expression"):
            get_derivative_steps("x +* 2", variable="x")

    def test_calculus_analyzer_differentiate_steps(self):
        calc = CalculusAnalyzer()
        steps = calc.differentiate_steps("x**2", variable="x")
        assert any("Power Rule" in s for s in steps)


class TestIntegralSteps:
    """Tests for integral step-by-step breakdown."""

    def test_integral_steps_power_rule(self):
        steps = get_integral_steps("x**3", variable="x")
        assert len(steps) >= 2
        text = "\n".join(steps)
        assert "Power Rule" in text
        assert "x**4/4" in text

    def test_integral_steps_sum_rule(self):
        steps = get_integral_steps("x + sin(x)", variable="x")
        text = "\n".join(steps)
        assert "Sum Rule" in text or "split" in text.lower()
        assert "cos" in text

    def test_integral_steps_parts(self):
        steps = get_integral_steps("x * exp(x)", variable="x")
        text = "\n".join(steps)
        assert "Integration by Parts" in text or "parts" in text.lower()
        assert "exp(x)" in text

    def test_integral_steps_substitution(self):
        steps = get_integral_steps("cos(2*x)", variable="x")
        text = "\n".join(steps)
        assert "substitution" in text.lower() or "u =" in text
        assert "sin(2*x)" in text

    def test_integral_steps_reciprocal(self):
        steps = get_integral_steps("1/x", variable="x")
        text = "\n".join(steps)
        assert "reciprocal" in text.lower() or "ln|x|" in text or "log" in text

    def test_integral_steps_arctan(self):
        steps = get_integral_steps("1/(x**2 + 1)", variable="x")
        text = "\n".join(steps)
        assert "atan" in text.lower() or "arctan" in text.lower()

    def test_integral_steps_definite(self):
        steps = get_integral_steps("x**2", variable="x", limits=(0, 2))
        text = "\n".join(steps)
        assert "Fundamental Theorem of Calculus" in text
        assert "8/3" in text

    def test_integral_steps_custom_variable(self):
        steps = get_integral_steps("y**2", variable="y")
        text = "\n".join(steps)
        assert "y" in text
        assert "y**3/3" in text

    def test_integral_steps_invalid_syntax(self):
        with pytest.raises(ValueError, match="Could not parse integral expression"):
            get_integral_steps("x +* 2")

    def test_calculus_analyzer_integrate_steps(self):
        calc = CalculusAnalyzer()
        steps = calc.integrate_steps("x**2", variable="x")
        assert len(steps) >= 2


class TestEquationSteps:
    """Tests for equation solving step-by-step breakdown."""

    def test_equation_steps_linear(self):
        steps = get_equation_steps("2*x + 4 = 10", variable="x")
        assert len(steps) >= 4
        text = "\n".join(steps)
        assert "linear" in text.lower()
        assert "x = 3" in text

    def test_equation_steps_quadratic_two_real_roots(self):
        steps = get_equation_steps("x**2 - 5*x + 6 = 0", variable="x")
        text = "\n".join(steps)
        assert "discriminant" in text.lower() or "Δ" in text
        assert "two distinct real roots" in text.lower()
        assert "2" in text and "3" in text

    def test_equation_steps_quadratic_repeated_root(self):
        steps = get_equation_steps("x**2 - 4*x + 4 = 0", variable="x")
        text = "\n".join(steps)
        assert "one repeated real root" in text.lower() or "Δ = 0" in text

    def test_equation_steps_quadratic_complex_roots(self):
        steps = get_equation_steps("x**2 + 4 = 0", variable="x")
        text = "\n".join(steps)
        assert "complex" in text.lower() or "Δ < 0" in text

    def test_equation_steps_polynomial_higher_degree(self):
        steps = get_equation_steps("x**3 - x = 0", variable="x")
        text = "\n".join(steps)
        assert "degree 3" in text or "factor" in text.lower()

    def test_equation_steps_general(self):
        steps = get_equation_steps("exp(x) = 5", variable="x")
        text = "\n".join(steps)
        assert "log(5)" in text

    def test_equation_steps_missing_equals(self):
        with pytest.raises(ValueError, match="Equation must contain '='"):
            get_equation_steps("2*x + 4")

    def test_equation_steps_invalid_syntax(self):
        with pytest.raises(ValueError, match="Could not parse equation"):
            get_equation_steps("2*x + = 10")

    def test_equation_solver_solve_steps(self):
        solver = EquationSolver()
        steps = solver.solve_steps("3*x - 9 = 0", variable="x")
        assert any("x = 3" in s for s in steps)


class TestODESteps:
    """Tests for ODE step-by-step breakdown."""

    def test_ode_steps_separable(self):
        steps = get_ode_steps("y' = x*y", variable="x", function="y")
        assert len(steps) >= 5
        text = "\n".join(steps)
        assert "Separable First-Order ODE" in text
        assert "Integrate both sides" in text

    def test_ode_steps_linear(self):
        steps = get_ode_steps("y' + 2*y = exp(x)", variable="x", function="y")
        assert len(steps) >= 6
        text = "\n".join(steps)
        assert "First-Order Linear ODE" in text
        assert "Integrating Factor" in text

    def test_ode_steps_bernoulli(self):
        steps = get_ode_steps("2xy y' = y^2 - x^2", variable="x", function="y")
        assert len(steps) >= 8
        text = "\n".join(steps)
        assert "Bernoulli Differential Equation" in text
        assert "substitution v" in text or "Integrating Factor" in text
        assert "y(x)**2 = x*(C1 - x)" in text or "C1" in text

        # Higher power Bernoulli
        steps2 = get_ode_steps("xy' + y = (x^3)y^6", variable="x", function="y")
        assert len(steps2) >= 8
        text2 = "\n".join(steps2)
        assert "Bernoulli Differential Equation" in text2
        assert "v = y^(1-n)" in text2 or "v = y^{-5}" in text2

    def test_ode_steps_homogeneous(self):
        steps = get_ode_steps("y' = (x^2 + y^2)/(2*x^2)", variable="x", function="y")
        assert len(steps) >= 6
        text = "\n".join(steps)
        assert "Homogeneous First-Order ODE" in text
        assert "v = y/x" in text or "substitution" in text.lower()

    def test_ode_steps_exact(self):
        steps = get_ode_steps("(2*x + y) + (x + 2*y)*y' = 0", variable="x", function="y")
        assert len(steps) >= 6
        text = "\n".join(steps)
        assert "Exact First-Order ODE" in text
        assert "potential function" in text.lower() or "exact" in text.lower()


