import sympy as sp
from typing import Optional

class CalculusAnalyzer:
    """Handles differentiation and integration, shielding user from Sympy internals."""
    def __init__(self):
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')

    def differentiate(self, expression_str: str, variable: str = 'x', order: int = 1):
        """
        Calculates the nth derivative of an algabraic expression.

        Args:
            expression_str: The mathematical expression(e.g 'sin(x) * exp(x)')
            variable: The variable to differentiate wit respect to
            order: The degree of the derivative
        """

        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression_str)
            result = sp.diff(expr, var, order)
            return str(sp.sympify(result))
        except Exception as e:
            raise ValueError(f"Calculus error during differentiation")

    def integrate(self, expression_str: str, variable: str = 'x', limits: Optional[tuple[float, float]] = None) -> str:
        """
        Calculuates either the indefinite or definite integral

        Args:
            expression_str: The mathematical expression to integrate.
            variable: The integration variable.
            limits: A tuple of (lower_bound, upper_bound) for definite intergrals
        """

        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression_str)

            if limits is not None:
                lower, upper = limits
                result = sp.integrate(expr, (var, lower, upper))
            else:
                result = sp.integrate(expr, var)

            return str(sp.sympify(result))
        except Exception as e:
            raise ValueError(f"Calculus error during integration: {e}")


    def get_limit(self, expression_str: str, variable: str = 'x', limits: Optional[float] = None) -> str:
        """
        Calculates the limit of a mathematical expression.

        Args:
            expression_str: The mathematical expression.
            variable: The limit variable.
            limits: The value towards which the variable tends to.
        """
        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression_str)
            result = sp.limit(expr, var, limits)

            return str(sp.sympify(result))
        except Exception as e:
            raise ValueError(f"Calculus error during limit calculation: {e}")
        