import sympy as sp

from mathstore.core.safe import safe_sympify


class CalculusAnalyzer:
    """Handles differentiation and integration, shielding user from Sympy internals."""

    def __init__(self):
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')

    def differentiate(
        self, expression_str: str, variable: str = 'x', order: int = 1, format: str = 'str'
    ) -> str:
        """
        Calculates the nth derivative of an algebraic expression.

        Args:
            expression_str: The mathematical expression (e.g. 'sin(x) * exp(x)')
            variable: The variable to differentiate with respect to (default: 'x')
            order: The degree of the derivative (default: 1)
            format: Output format ('str', 'latex', or 'pretty')
        """
        try:
            var = sp.Symbol(variable)
            expr = safe_sympify(expression_str)
            result = sp.diff(expr, var, order)
            if format == 'latex':
                return sp.latex(sp.Eq(sp.Derivative(expr, var, order), result, evaluate=False))
            if format == 'pretty':
                return sp.pretty(
                    sp.Eq(sp.Derivative(expr, var, order), result, evaluate=False),
                    use_unicode=True,
                )
            return str(result)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Calculus error during differentiation: {e}")

    def integrate(
        self,
        expression_str: str,
        variable: str = 'x',
        limits: tuple[float, float] | None = None,
        format: str = 'str',
    ) -> str:
        """
        Calculates either the indefinite or definite integral.

        Args:
            expression_str: The mathematical expression to integrate.
            variable: The integration variable (default: 'x').
            limits: A tuple of (lower_bound, upper_bound) for definite integrals
            format: Output format ('str', 'latex', or 'pretty')
        """
        try:
            var = sp.Symbol(variable)
            expr = safe_sympify(expression_str)

            if limits is not None:
                lower, upper = limits
                result = sp.integrate(expr, (var, lower, upper))
                if format == 'latex':
                    return sp.latex(
                        sp.Eq(sp.Integral(expr, (var, lower, upper)), result, evaluate=False)
                    )
                if format == 'pretty':
                    return sp.pretty(
                        sp.Eq(sp.Integral(expr, (var, lower, upper)), result, evaluate=False),
                        use_unicode=True,
                    )
            else:
                result = sp.integrate(expr, var)
                if format == 'latex':
                    return sp.latex(sp.Eq(sp.Integral(expr, var), result, evaluate=False))
                if format == 'pretty':
                    return sp.pretty(
                        sp.Eq(sp.Integral(expr, var), result, evaluate=False),
                        use_unicode=True,
                    )

            return str(result)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Calculus error during integration: {e}")

    def get_limit(
        self,
        expression_str: str,
        limits: float | sp.Basic | str,
        variable: str = 'x',
        format: str = 'str',
    ) -> str:
        """
        Calculates the limit of a mathematical expression.

        Args:
            expression_str: The mathematical expression.
            limits: The value towards which the variable tends to.
            variable: The limit variable (default: 'x').
            format: Output format ('str', 'latex', or 'pretty')
        """
        try:
            var = sp.Symbol(variable)
            expr = safe_sympify(expression_str)
            target = safe_sympify(limits)
            result = sp.limit(expr, var, target)
            if format == 'latex':
                return sp.latex(sp.Eq(sp.Limit(expr, var, target), result, evaluate=False))
            if format == 'pretty':
                return sp.pretty(
                    sp.Eq(sp.Limit(expr, var, target), result, evaluate=False),
                    use_unicode=True,
                )
            return str(result)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Calculus error during limit calculation: {e}")

    def differentiate_steps(
        self, expression_str: str, variable: str = 'x', order: int = 1
    ) -> list[str]:
        """
        Returns step-by-step differentiation of an expression.

        Args:
            expression_str: The mathematical expression.
            variable: The variable to differentiate against (default: 'x').
            order: The derivative order (default: 1).
        """
        from mathstore.study.steps import get_derivative_steps

        return get_derivative_steps(expression_str, variable=variable, order=order)

    def integrate_steps(
        self,
        expression_str: str,
        variable: str = 'x',
        limits: tuple[float, float] | None = None,
    ) -> list[str]:
        """
        Returns step-by-step breakdown of indefinite or definite integration.

        Args:
            expression_str: The mathematical expression to integrate.
            variable: The variable of integration (default: 'x').
            limits: Optional tuple of (lower_bound, upper_bound) for definite integrals.
        """
        from mathstore.study.steps import get_integral_steps

        return get_integral_steps(expression_str, variable=variable, limits=limits)

        