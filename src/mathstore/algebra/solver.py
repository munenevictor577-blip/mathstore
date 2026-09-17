import sympy as sp


class EquationSolver:
    """Handles algebraic equation solving isolating the sympy implementation."""

    def __init__(self):
        self.x, self.y, self.z = sp.symbols("x y z")

    def solve_linear(self, equation_str: str, variable: str = "x") -> list:
        """Solves an equation like '2*x + 4 = 10'."""
        try:
            var = sp.Symbol(variable)
            left, right = equation_str.split("=")
            eq = sp.Eq(sp.sympify(left.strip()), sp.sympify(right.strip()))

            return sp.solve(eq, var)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Failed to parse or solve the equation: {e}")

    def simplify_expression(self, expression_str: str) -> str:
        """Simplifies algebraic expressions."""
        try:
            expr = sp.sympify(expression_str)
            return str(sp.simplify(expr))
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Failed to parse or simplify the expression: {e}")