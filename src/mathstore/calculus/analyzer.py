import sympy as sp


class CalculusAnalyzer:
    """Handles differentiation and integration, shielding user from Sympy internals."""

    def __init__(self):
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')

    def differentiate(self, expression_str: str, variable: str = 'x', order: int = 1) -> str:
        """
        Calculates the nth derivative of an algebraic expression.

        Args:
            expression_str: The mathematical expression (e.g. 'sin(x) * exp(x)')
            variable: The variable to differentiate with respect to (default: 'x')
            order: The degree of the derivative (default: 1)
        """
        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression_str)
            result = sp.diff(expr, var, order)
            return str(result)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Calculus error during differentiation: {e}")

    def integrate(self, expression_str: str, variable: str = 'x', limits: tuple[float, float] | None = None) -> str:
        """
        Calculates either the indefinite or definite integral.

        Args:
            expression_str: The mathematical expression to integrate.
            variable: The integration variable (default: 'x').
            limits: A tuple of (lower_bound, upper_bound) for definite integrals
        """
        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression_str)

            if limits is not None:
                lower, upper = limits
                result = sp.integrate(expr, (var, lower, upper))
            else:
                result = sp.integrate(expr, var)

            return str(result)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Calculus error during integration: {e}")

    def get_limit(self, expression_str: str, limits: float | sp.Basic | str, variable: str = 'x') -> str:
        """
        Calculates the limit of a mathematical expression.

        Args:
            expression_str: The mathematical expression.
            limits: The value towards which the variable tends to.
            variable: The limit variable (default: 'x').
        """
        try:
            var = sp.Symbol(variable)
            expr = sp.sympify(expression_str)
            target = sp.sympify(limits)
            result = sp.limit(expr, var, target)
            return str(result)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Calculus error during limit calculation: {e}")

        