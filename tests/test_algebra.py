import pytest
import sympy as sp

from mathstore.algebra.solver import EquationSolver


class TestEquationSolver:
    """Tests for EquationSolver class."""

    def test_init_symbols(self, solver: EquationSolver):
        """Verify that solver initializes x, y, z as sympy symbols."""
        assert solver.x == sp.Symbol("x")
        assert solver.y == sp.Symbol("y")
        assert solver.z == sp.Symbol("z")

    def test_solve_linear_basic(self, solver: EquationSolver):
        """Solve a standard linear equation with default variable 'x'."""
        result = solver.solve_linear("2*x + 4 = 10")
        assert result == [sp.sympify(3)]

    def test_solve_linear_subtraction_and_negative(self, solver: EquationSolver):
        """Solve linear equations with subtraction and negative coefficients."""
        result = solver.solve_linear("x - 5 = 20")
        assert result == [sp.sympify(25)]

        result_neg = solver.solve_linear("-2*x = 10")
        assert result_neg == [sp.sympify(-5)]

    def test_solve_linear_fractional_solution(self, solver: EquationSolver):
        """Solve an equation yielding a rational fraction."""
        result = solver.solve_linear("3*x = 2")
        assert result == [sp.Rational(2, 3)]

    def test_solve_linear_custom_variable(self, solver: EquationSolver):
        """Solve equations specifying alternative variable names."""
        result_y = solver.solve_linear("3*y - 9 = 0", variable="y")
        assert result_y == [sp.sympify(3)]

        result_t = solver.solve_linear("2*t + 10 = 0", variable="t")
        assert result_t == [sp.sympify(-5)]

    def test_solve_linear_variables_on_both_sides(self, solver: EquationSolver):
        """Solve linear equation where variables appear on both sides."""
        result = solver.solve_linear("4*x + 2 = 2*x + 12")
        assert result == [sp.sympify(5)]

    def test_solve_linear_no_solution(self, solver: EquationSolver):
        """Solve inconsistent equation with no solution."""
        result = solver.solve_linear("x = x + 1")
        assert result == []

    def test_solve_linear_missing_equals_sign(self, solver: EquationSolver):
        """Raise ValueError when expression has no equals sign."""
        with pytest.raises(ValueError, match="Failed to parse or solve the equation"):
            solver.solve_linear("2*x + 4")

    def test_solve_linear_too_many_equals_signs(self, solver: EquationSolver):
        """Raise ValueError when expression has multiple equals signs."""
        with pytest.raises(ValueError, match="Failed to parse or solve the equation"):
            solver.solve_linear("x = y = 2")

    def test_solve_linear_syntax_error(self, solver: EquationSolver):
        """Raise ValueError when expression has malformed mathematical syntax."""
        with pytest.raises(ValueError, match="Failed to parse or solve the equation"):
            solver.solve_linear("2*x + = 10")

    def test_solver_blocks_injection(self, solver: EquationSolver):
        """Verify that code injection attempts in equations are blocked."""
        with pytest.raises(ValueError):
            solver.solve_linear("__import__('os').system('echo') = 0")

    def test_simplify_expression_linear(self, solver: EquationSolver):
        """Simplify simple algebraic combinations."""
        simplified = solver.simplify_expression("2*x + 3*x")
        assert simplified == "5*x"

    def test_simplify_expression_polynomial(self, solver: EquationSolver):
        """Simplify expanded polynomial expressions."""
        simplified = solver.simplify_expression("(x + 1)**2 - (x**2 + 2*x + 1)")
        assert simplified == "0"

    def test_simplify_expression_trigonometric(self, solver: EquationSolver):
        """Simplify trigonometric identities."""
        simplified = solver.simplify_expression("sin(x)**2 + cos(x)**2")
        assert simplified == "1"

    def test_simplify_expression_constant(self, solver: EquationSolver):
        """Simplify arithmetic constants."""
        simplified = solver.simplify_expression("10 + 5 * 2")
        assert simplified == "20"

    def test_simplify_expression_invalid_syntax(self, solver: EquationSolver):
        """Raise error when invalid syntax is passed to simplify_expression."""
        with pytest.raises(ValueError, match="Failed to parse or simplify the expression"):
            solver.simplify_expression("x +* 2")

    def test_format_solution_single(self, solver: EquationSolver):
        """Test formatting for a single solution in str, latex, and pretty formats."""
        sol = [sp.sympify(3)]
        assert solver.format_solution(sol, "x", format="str") == "Solution: x = [3]"
        assert solver.format_solution(sol, "x", format="latex") == "x = 3"
        assert solver.format_solution(sol, "x", format="pretty") == "x = 3"

    def test_format_solution_multiple(self, solver: EquationSolver):
        """Test formatting for multiple solutions in latex and pretty formats."""
        sol = [sp.sympify(-2), sp.sympify(2)]
        latex_out = solver.format_solution(sol, "x", format="latex")
        pretty_out = solver.format_solution(sol, "x", format="pretty")
        assert "x \\in \\left\\{" in latex_out
        assert "x ∈ {" in pretty_out

    def test_format_solution_empty(self, solver: EquationSolver):
        """Test formatting for no solutions."""
        assert solver.format_solution([], "x", format="latex") == r"\emptyset"
        assert solver.format_solution([], "x", format="pretty") == "No solution (∅)"

