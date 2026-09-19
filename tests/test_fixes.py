"""Tests validating bug fixes, numerical improvements, and security enhancements."""

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from mathstore.algebra.solver import EquationSolver
from mathstore.api.main import app
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.core.matrix import MatrixAnalyzer
from mathstore.core.safe import safe_sympify
from mathstore.statistics.analyzer import StatsAnalyzer
from mathstore.study.practice import PracticeQuestion, check_answer
from mathstore.study.steps import DerivativeStepGenerator, get_equation_steps


class TestSecuritySafeParsing:
    """Validates that dangerous Python code injection vectors are blocked."""

    def test_safe_sympify_blocks_dunder(self):
        with pytest.raises(ValueError, match="forbidden pattern detected"):
            safe_sympify("__import__('os').system('echo pwned')")

    def test_safe_sympify_blocks_keywords(self):
        for word in ["import", "eval", "exec", "open", "builtins", "subprocess", "os", "sys"]:
            with pytest.raises(ValueError, match="forbidden pattern detected"):
                safe_sympify(f"{word}('something')")

    def test_safe_sympify_allows_normal_math(self):
        expr = safe_sympify("cos(x) + sin(2*x) + 3*x**2")
        assert expr.has(sp.Symbol("x"))

    def test_calculus_blocks_injection(self):
        c = CalculusAnalyzer()
        with pytest.raises(ValueError):
            c.differentiate("__import__('os').system('echo')")

    def test_solver_blocks_injection(self):
        s = EquationSolver()
        with pytest.raises(ValueError):
            s.solve_linear("__import__('os').system('echo') = 0")


class TestPracticeCheckFixes:
    """Validates root set string parsing and correct_value=None fallback."""

    def test_roots_matching_with_string_list(self):
        q = PracticeQuestion(
            topic="algebra",
            difficulty="medium",
            prompt="Solve x^2 - 5*x + 6 = 0",
            expected_answer="2, 3",
            hint="factor",
            question_type="roots",
            correct_value=["2", "3"],
        )
        is_correct, feedback = check_answer("3, 2", q)
        assert is_correct is True
        assert "Correct" in feedback

    def test_roots_fallback_when_correct_value_none(self):
        q = PracticeQuestion(
            topic="algebra",
            difficulty="medium",
            prompt="Solve x^2 - 5*x + 6 = 0",
            expected_answer="2, 3",
            hint="factor",
            question_type="roots",
            correct_value=None,
        )
        is_correct, feedback = check_answer("2, 3", q)
        assert is_correct is True

    def test_derivative_fallback_when_correct_value_none(self):
        q = PracticeQuestion(
            topic="derivatives",
            difficulty="easy",
            prompt="Differentiate x**2",
            expected_answer="2*x",
            hint="power rule",
            question_type="derivative",
            correct_value=None,
        )
        is_correct, feedback = check_answer("2*x", q)
        assert is_correct is True

    def test_number_fallback_when_correct_value_none(self):
        q = PracticeQuestion(
            topic="stats",
            difficulty="easy",
            prompt="Find mean",
            expected_answer="15.5",
            hint="sum/n",
            question_type="number",
            correct_value=None,
        )
        is_correct, feedback = check_answer("15.5", q)
        assert is_correct is True

    def test_integral_fallback_when_correct_value_none(self):
        q = PracticeQuestion(
            topic="integrals",
            difficulty="easy",
            prompt="Integrate x^2",
            expected_answer="x**3/3 + C",
            hint="power rule",
            question_type="integral",
            correct_value=None,
        )
        is_correct, feedback = check_answer("x**3/3", q)
        assert is_correct is True


class TestMatrixFixes:
    """Validates matrix parsing for nested list strings with symbols."""

    def test_parse_symbolic_nested_list_string(self):
        analyzer = MatrixAnalyzer()
        mat = analyzer.parse_matrix("[[x, 1], [0, 2]]")
        assert mat.shape == (2, 2)
        assert mat[0, 0] == sp.Symbol("x")


class TestStatisticsFixes:
    """Validates numerical accuracy in t-critical and zero variance handling in t-test."""

    def test_t_critical_adaptive_small_df(self):
        analyzer = StatsAnalyzer()
        # df = 1, 99.9% confidence has true t* ~ 636.62
        t_crit = analyzer._t_critical(0.999, df=1)
        assert t_crit > 600.0
        assert abs(t_crit - 636.62) < 1.0

    def test_one_sample_t_test_zero_variance_different_mean(self):
        analyzer = StatsAnalyzer()
        with pytest.raises(ValueError, match="Sample variance is zero"):
            analyzer.one_sample_t_test([5.0, 5.0, 5.0], pop_mean=10.0)

    def test_one_sample_t_test_zero_variance_identical_mean(self):
        analyzer = StatsAnalyzer()
        res = analyzer.one_sample_t_test([5.0, 5.0, 5.0], pop_mean=5.0)
        assert isinstance(res, dict)
        assert res["t_statistic"] == 0.0


class TestStepsFixes:
    """Validates step generator validation and symbolic quadratic steps."""

    def test_derivative_steps_order_zero_or_negative(self):
        gen = DerivativeStepGenerator()
        with pytest.raises(ValueError, match="must be at least 1"):
            gen.explain("x**2", order=0)
        with pytest.raises(ValueError, match="must be at least 1"):
            gen.explain("x**2", order=-1)

    def test_quadratic_steps_symbolic_coefficients(self):
        steps = get_equation_steps("a*x**2 + b*x + c = 0", variable="x")
        assert any("quadratic formula" in s.lower() for s in steps)


class TestAPIStatisticsResponseSchemas:
    """Validates that statistics endpoints return valid typed responses."""

    def test_stats_summary_response(self):
        client = TestClient(app)
        res = client.post("/math/stats/summary", json={"data": "10, 12, 14", "format": "str"})
        assert res.status_code == 200
        data = res.json()
        assert "data" in data
        assert "summary" in data

    def test_stats_poisson_response_model(self):
        client = TestClient(app)
        res = client.post("/math/stats/poisson", json={"k": 2, "lam": 3.0})
        assert res.status_code == 200
        data = res.json()
        assert data["k"] == 2
        assert data["lambda"] == 3.0
