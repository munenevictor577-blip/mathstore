from unittest.mock import MagicMock, patch
import pytest
import sympy as sp

from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.study.steps import (
    DerivativeStepGenerator,
    format_integral_rule,
    get_derivative_steps,
    get_equation_steps,
    get_integral_steps,
)


class TestDerivativeSteps:
    """Tests for derivative step-by-step breakdown."""

    def test_derivative_steps_power_and_exp_chain_rules(self):
        # Lines 97-104: Power and chain rule (base has variable, base != variable)
        steps_pow = get_derivative_steps("(x**2 + 1)**3", variable="x")
        assert any("Power and Chain Rule" in s for s in steps_pow)

        # Lines 105-113: Exponential rule with general constant base
        steps_exp = get_derivative_steps("2**x", variable="x")
        assert any("Exponential Rule" in s for s in steps_exp)

        # Lines 150-152: Fallback differentiation for special functions (e.g. gamma)
        steps_gamma = get_derivative_steps("gamma(x)", variable="x")
        assert any("Differentiate" in s for s in steps_gamma)

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

        with pytest.raises(ValueError, match="at least 1"):
            get_derivative_steps("x**2", variable="x", order=0)

    def test_derivative_steps_order_zero_or_negative(self):
        gen = DerivativeStepGenerator()
        with pytest.raises(ValueError, match="must be at least 1"):
            gen.explain("x**2", order=0)
        with pytest.raises(ValueError, match="must be at least 1"):
            gen.explain("x**2", order=-1)

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

    def test_integral_rule_formatting_edge_cases(self):
        # Line 170: AlternativeRule with empty alternatives
        alt_empty = type("AlternativeRule", (), {"alternatives": []})()
        assert format_integral_rule(alt_empty) == ["No standard elementary rule found."]

        # Lines 167-169 & 173-175: AlternativeRule with alternatives and ConstantRule
        const_rule = type("ConstantRule", (), {"integrand": 5, "variable": sp.Symbol("x"), "eval": lambda self: 5 * sp.Symbol("x")})()
        alt_with_sub = type("AlternativeRule", (), {"alternatives": [const_rule]})()
        assert len(format_integral_rule(alt_with_sub)) > 0

        # Line 222: Sec2Rule
        sec_rule = type("Sec2Rule", (), {"variable": sp.Symbol("x")})()
        assert any("sec(" in s for s in format_integral_rule(sec_rule))

        # Line 224: Csc2Rule
        csc_rule = type("Csc2Rule", (), {"variable": sp.Symbol("x")})()
        assert any("csc(" in s for s in format_integral_rule(csc_rule))

        # Lines 229-231: hasattr substep
        sub_rule = type("SubstepRule", (), {"substep": sec_rule, "integrand": "sec(x)^2"})()
        assert len(format_integral_rule(sub_rule)) > 0

        # Lines 232-233: hasattr eval
        eval_rule = type("EvalRule", (), {"eval": lambda self: sp.Symbol("x"), "integrand": "x"})()
        assert any("Evaluate integral" in s for s in format_integral_rule(eval_rule))

        # Lines 234-238: direct integration fallback
        direct_rule = type("DirectRule", (), {"variable": sp.Symbol("x"), "integrand": sp.Symbol("x")})()
        assert any("Direct integration" in s for s in format_integral_rule(direct_rule))

    def test_integral_steps_dontknow_and_exception(self):
        with patch("mathstore.study.steps.integral_steps") as mock_steps:
            mock_rule = MagicMock()
            type(mock_rule).__name__ = "DontKnowRule"
            mock_steps.return_value = mock_rule
            steps = get_integral_steps("x**2", variable="x")
            assert any("general integration algorithms" in s for s in steps)

        with patch("mathstore.study.steps.integral_steps", side_effect=RuntimeError("SymPy error")):
            steps = get_integral_steps("x**2", variable="x")
            assert any("symbolic integration" in s for s in steps)


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

    def test_equation_steps_symbolic_discriminant(self):
        steps = get_equation_steps("x**2 + k*x + 1 = 0", variable="x")
        assert any("depends on parameter values" in s for s in steps)

    def test_quadratic_steps_symbolic_coefficients(self):
        steps = get_equation_steps("a*x**2 + b*x + c = 0", variable="x")
        assert any("quadratic formula" in s.lower() for s in steps)
