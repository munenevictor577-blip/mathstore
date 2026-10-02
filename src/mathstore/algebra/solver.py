import sympy as sp

from mathstore.core.safe import safe_sympify


class EquationSolver:
    """Handles algebraic equation solving isolating the sympy implementation."""

    def __init__(self):
        self.x, self.y, self.z = sp.symbols("x y z")

    def solve_linear(self, equation_str: str, variable: str = "x") -> list:
        """Solves an equation like '2*x + 4 = 10'."""
        try:
            var = sp.Symbol(variable)
            if "=" not in equation_str:
                raise ValueError(
                    "Equation must contain '=' separating left and right sides."
                )
            parts = equation_str.split("=")
            if len(parts) != 2:
                raise ValueError("Equation must contain exactly one '=' sign.")
            left, right = parts
            eq = sp.Eq(safe_sympify(left.strip()), safe_sympify(right.strip()))

            return sp.solve(eq, var)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Failed to parse or solve the equation: {e}") from e

    def simplify_expression(self, expression_str: str) -> str:
        """Simplifies algebraic expressions."""
        try:
            expr = safe_sympify(expression_str)
            return str(sp.simplify(expr))
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Failed to parse or simplify the expression: {e}")

    def format_solution(
        self, solutions: list, variable: str = "x", format: str = "str"
    ) -> str:
        """
        Formats equation solutions into standard text, LaTeX, or pretty Unicode.

        Args:
            solutions: List of solutions returned by solve_linear.
            variable: The variable solved for (default: 'x').
            format: Output format ('str', 'latex', or 'pretty').
        """
        if format == "latex":
            if not solutions:
                return r"\emptyset"
            if len(solutions) == 1:
                return f"{variable} = {sp.latex(solutions[0])}"
            inner = ", ".join(sp.latex(s) for s in solutions)
            return f"{variable} \\in \\left\\{{ {inner} \\right\\}}"

        if format == "pretty":
            if not solutions:
                return "No solution (∅)"
            if len(solutions) == 1:
                return f"{variable} = {sp.pretty(solutions[0], use_unicode=True)}"
            inner = ", ".join(sp.pretty(s, use_unicode=True) for s in solutions)
            return f"{variable} ∈ {{{inner}}}"

        return f"Solution: {variable} = {solutions}"

    def solve_steps(self, equation_str: str, variable: str = "x") -> list[str]:
        """
        Returns step-by-step algebraic isolation and solution breakdown for an equation.

        Args:
            equation_str: The equation to solve (e.g., '2*x + 4 = 10').
            variable: The variable to isolate (default: 'x').
        """
        from mathstore.study.steps import get_equation_steps

        return get_equation_steps(equation_str, variable=variable)
