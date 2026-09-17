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
