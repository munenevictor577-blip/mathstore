import pytest
import sympy as sp

from mathstore.calculus.analyzer import CalculusAnalyzer


class TestCalculusAnalyzer:
    """Tests for CalculusAnalyzer class."""

    def test_init_symbols(self, analyzer: CalculusAnalyzer):
        """Verify initialization of symbols x, y, z, t."""
        assert analyzer.x == sp.Symbol("x")
        assert analyzer.y == sp.Symbol("y")
        assert analyzer.z == sp.Symbol("z")
        assert analyzer.t == sp.Symbol("t")

    def test_differentiate_polynomial(self, analyzer: CalculusAnalyzer):
        """Differentiate polynomial expressions."""
        assert analyzer.differentiate("x**2") == "2*x"
        assert analyzer.differentiate("5*x**3 + 2*x") == "15*x**2 + 2"

    def test_differentiate_higher_order(self, analyzer: CalculusAnalyzer):
        """Differentiate with higher-order derivatives."""
        assert analyzer.differentiate("x**3", order=1) == "3*x**2"
        assert analyzer.differentiate("x**3", order=2) == "6*x"
        assert analyzer.differentiate("x**3", order=3) == "6"
        assert analyzer.differentiate("x**3", order=4) == "0"

    def test_differentiate_trigonometric(self, analyzer: CalculusAnalyzer):
        """Differentiate trigonometric functions."""
        assert analyzer.differentiate("sin(x)") == "cos(x)"
        assert analyzer.differentiate("cos(x)") == "-sin(x)"

    def test_differentiate_custom_variable(self, analyzer: CalculusAnalyzer):
        """Differentiate with respect to a non-default variable."""
        assert analyzer.differentiate("y**4", variable="y") == "4*y**3"
        assert analyzer.differentiate("t**2 + 3*t", variable="t") == "2*t + 3"

    def test_differentiate_product_rule(self, analyzer: CalculusAnalyzer):
        """Differentiate product of functions."""
        result = analyzer.differentiate("sin(x)*x")
        assert result == "x*cos(x) + sin(x)"

    def test_differentiate_syntax_error(self, analyzer: CalculusAnalyzer):
        """Raise ValueError when expression syntax is invalid."""
        with pytest.raises(ValueError, match="Calculus error during differentiation"):
            analyzer.differentiate("sin(")

    def test_calculus_blocks_injection(self, analyzer: CalculusAnalyzer):
        """Verify that code injection attempts in expressions are blocked."""
        with pytest.raises(ValueError):
            analyzer.differentiate("__import__('os').system('echo')")

    def test_integrate_indefinite_polynomial(self, analyzer: CalculusAnalyzer):
        """Compute indefinite integral for polynomials."""
        assert analyzer.integrate("x**2") == "x**3/3"
        assert analyzer.integrate("3*x**2") == "x**3"

    def test_integrate_indefinite_trigonometric(self, analyzer: CalculusAnalyzer):
        """Compute indefinite integral for trigonometric functions."""
        assert analyzer.integrate("cos(x)") == "sin(x)"
        assert analyzer.integrate("sin(x)") == "-cos(x)"

    def test_integrate_indefinite_custom_variable(self, analyzer: CalculusAnalyzer):
        """Compute indefinite integral with respect to custom variable."""
        assert analyzer.integrate("y**2", variable="y") == "y**3/3"

    def test_integrate_definite_polynomial(self, analyzer: CalculusAnalyzer):
        """Compute definite integral with specified bounds."""
        assert analyzer.integrate("x", limits=(0, 2)) == "2"
        assert analyzer.integrate("x**2", limits=(0, 3)) == "9"

    def test_integrate_definite_constant(self, analyzer: CalculusAnalyzer):
        """Compute definite integral of a constant."""
        assert analyzer.integrate("1", limits=(1, 5)) == "4"

    def test_integrate_syntax_error(self, analyzer: CalculusAnalyzer):
        """Raise ValueError when expression syntax is invalid."""
        with pytest.raises(ValueError, match="Calculus error during integration"):
            analyzer.integrate("sin(")

    def test_get_limit_polynomial(self, analyzer: CalculusAnalyzer):
        """Compute finite limit of polynomial expression."""
        assert analyzer.get_limit("x**2 + 2*x + 1", limits=2) == "9"

    def test_get_limit_trigonometric_indeterminate(self, analyzer: CalculusAnalyzer):
        """Compute limit of standard indeterminate form sin(x)/x as x -> 0."""
        assert analyzer.get_limit("sin(x)/x", limits=0) == "1"

    def test_get_limit_rational_cancel(self, analyzer: CalculusAnalyzer):
        """Compute limit where numerator and denominator share a root."""
        assert analyzer.get_limit("(x**2 - 4)/(x - 2)", limits=2) == "4"

    def test_get_limit_infinite(self, analyzer: CalculusAnalyzer):
        """Compute limit as variable approaches infinity."""
        assert analyzer.get_limit("1/x", limits=sp.oo) == "0"

    def test_get_limit_custom_variable(self, analyzer: CalculusAnalyzer):
        """Compute limit with custom variable."""
        assert analyzer.get_limit("y**2", variable="y", limits=3) == "9"

    def test_get_limit_syntax_error(self, analyzer: CalculusAnalyzer):
        """Raise ValueError when expression syntax is invalid."""
        with pytest.raises(ValueError, match="Calculus error during limit calculation"):
            analyzer.get_limit("sin(", limits=0)

    def test_differentiate_latex_and_pretty(self, analyzer: CalculusAnalyzer):
        """Verify LaTeX and pretty Unicode formatting for derivatives."""
        latex_res = analyzer.differentiate("x**2", format="latex")
        assert r"\frac{d}{d x}" in latex_res
        assert "2 x" in latex_res

        pretty_res = analyzer.differentiate("x**2", format="pretty")
        assert "dx" in pretty_res
        assert "2⋅x" in pretty_res

    def test_integrate_indefinite_latex_and_pretty(self, analyzer: CalculusAnalyzer):
        """Verify LaTeX and pretty Unicode formatting for indefinite integrals."""
        latex_res = analyzer.integrate("x**2", format="latex")
        assert r"\int" in latex_res
        assert r"\frac{x^{3}}{3}" in latex_res

        pretty_res = analyzer.integrate("x**2", format="pretty")
        assert "⌠" in pretty_res
        assert "3" in pretty_res

    def test_integrate_definite_latex_and_pretty(self, analyzer: CalculusAnalyzer):
        """Verify LaTeX and pretty Unicode formatting for definite integrals."""
        latex_res = analyzer.integrate("x", limits=(0, 2), format="latex")
        assert r"\int" in latex_res
        assert "2" in latex_res

        pretty_res = analyzer.integrate("x", limits=(0, 2), format="pretty")
        assert "⌠" in pretty_res
        assert "2" in pretty_res

    def test_get_limit_latex_and_pretty(self, analyzer: CalculusAnalyzer):
        """Verify LaTeX and pretty Unicode formatting for limits."""
        latex_res = analyzer.get_limit("sin(x)/x", limits=0, format="latex")
        assert r"\lim" in latex_res
        assert "1" in latex_res

        pretty_res = analyzer.get_limit("sin(x)/x", limits=0, format="pretty")
        assert "lim" in pretty_res
        assert "1" in pretty_res

    def test_natural_text_2_pow_x_sin_x(self, analyzer: CalculusAnalyzer):
        """Verify parsing and differentiation of normal text '2^x sin x'."""
        diff_res = analyzer.differentiate("2^x sin x")
        assert "2**x" in diff_res
        assert "sin(x)" in diff_res
        assert "cos(x)" in diff_res
        assert "log(2)" in diff_res

        int_res = analyzer.integrate("2^x sin x")
        assert "2**x" in int_res
        assert "sin(x)" in int_res
        assert "cos(x)" in int_res

        lim_res = analyzer.get_limit("2^x sin x", limits=0)
        assert lim_res == "0"

    def test_natural_text_implicit_multiplication_and_powers(self, analyzer: CalculusAnalyzer):
        """Verify normal text with implicit multiplication, caret powers, and e^x."""
        assert analyzer.differentiate("2x + 4") == "2"
        assert analyzer.differentiate("x^2") == "2*x"
        assert analyzer.differentiate("3x^2 + 5x - 7") == "6*x + 5"
        assert analyzer.differentiate("e^x") == "exp(x)"
        assert analyzer.differentiate("sin^2 x") == "2*sin(x)*cos(x)"
        assert analyzer.get_limit("sin x / x", limits=0) == "1"

    def test_natural_text_trailing_differential(self, analyzer: CalculusAnalyzer):
        """Verify handling of trailing differential 'dx'."""
        assert analyzer.integrate("2x dx") == "x**2"
        assert "2**x" in analyzer.integrate("2^x sin x dx")

    def test_parse_expression_method(self, analyzer: CalculusAnalyzer):
        """Verify the parse_expression helper method."""
        expr = analyzer.parse_expression("2^x sin x")
        assert expr == sp.sympify("2**x * sin(x)")
        expr2 = analyzer.parse_expression("e^(2x)")
        assert expr2 == sp.exp(2 * sp.Symbol("x"))

