import subprocess
import sys

import pytest

from mathstore.cli import main


class TestCLI:
    """Tests for the mathstore command-line interface."""

    def test_cli_solve_default_variable(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test solve subcommand with default variable 'x'."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "solve", "2*x + 4 = 10"])
        main()
        captured = capsys.readouterr()
        assert "Solution: x = [3]" in captured.out

    def test_cli_solve_custom_variable(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test solve subcommand with custom variable '--var y'."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "solve", "3*y - 6 = 0", "--var", "y"])
        main()
        captured = capsys.readouterr()
        assert "Solution: y = [2]" in captured.out

    def test_cli_solve_error(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test solve subcommand error handling when equation cannot be solved."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "solve", "invalid_equation"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error executing 'solve'" in captured.err

    def test_cli_diff_default(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test diff subcommand with default variable and order 1."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "diff", "x**2"])
        main()
        captured = capsys.readouterr()
        assert "Derivative (order 1): 2*x" in captured.out

    def test_cli_diff_custom_order(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test diff subcommand with custom derivative order."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "diff", "x**3", "--order", "2"])
        main()
        captured = capsys.readouterr()
        assert "Derivative (order 2): 6*x" in captured.out

    def test_cli_diff_custom_variable(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test diff subcommand with custom variable."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "diff", "y**3", "--var", "y"])
        main()
        captured = capsys.readouterr()
        assert "Derivative (order 1): 3*y**2" in captured.out

    def test_cli_diff_error(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test diff subcommand error handling with invalid expression."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "diff", "sin("])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error executing 'diff'" in captured.err

    def test_cli_integrate_indefinite(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test integrate subcommand with indefinite integral."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "integrate", "x**2"])
        main()
        captured = capsys.readouterr()
        assert "Integral: x**3/3" in captured.out

    def test_cli_integrate_definite(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test integrate subcommand with definite integral limits."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "integrate", "x", "--limits", "0", "2"])
        main()
        captured = capsys.readouterr()
        assert "Integral: 2" in captured.out

    def test_cli_integrate_custom_variable(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test integrate subcommand with custom variable."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "integrate", "y**2", "--var", "y"])
        main()
        captured = capsys.readouterr()
        assert "Integral: y**3/3" in captured.out

    def test_cli_integrate_error(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test integrate subcommand error handling with invalid expression."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "integrate", "sin("])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error executing 'integrate'" in captured.err

    def test_cli_limit(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test limit subcommand with indeterminate expression sin(x)/x as x -> 0."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "limit", "sin(x)/x", "0"])
        main()
        captured = capsys.readouterr()
        assert "Limit: 1" in captured.out

    def test_cli_limit_infinite(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test limit subcommand as variable approaches infinity."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "limit", "1/x", "oo"])
        main()
        captured = capsys.readouterr()
        assert "Limit: 0" in captured.out

    def test_cli_limit_error(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test limit subcommand error handling with invalid expression."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "limit", "sin(", "0"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error executing 'limit'" in captured.err

    def test_cli_missing_command(self, monkeypatch: pytest.MonkeyPatch):
        """Test CLI with no command provided raises SystemExit."""
        monkeypatch.setattr(sys, "argv", ["mathstore"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2

    def test_cli_help(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test CLI --help displays usage."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "--help"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "MathStore CLI" in captured.out

    def test_cli_subprocess_execution(self):
        """Verify CLI can be invoked end-to-end as a python module subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "mathstore.cli", "solve", "2*x + 4 = 10"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "Solution: x = [3]" in result.stdout

    def test_cli_main_execution(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Verify execution of the if __name__ == '__main__': block."""
        import runpy
        monkeypatch.setattr(sys, "argv", ["mathstore", "solve", "x - 1 = 0"])
        monkeypatch.delitem(sys.modules, "mathstore.cli", raising=False)
        runpy.run_module("mathstore.cli", run_name="__main__")
        captured = capsys.readouterr()
        assert "Solution: x = [1]" in captured.out

    def test_cli_solve_latex(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test solve subcommand with --latex flag."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "solve", "2*x + 4 = 10", "--latex"])
        main()
        captured = capsys.readouterr()
        assert "x = 3" in captured.out

    def test_cli_solve_pretty(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test solve subcommand with --pretty flag."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "solve", "2*x + 4 = 10", "--pretty"])
        main()
        captured = capsys.readouterr()
        assert "x = 3" in captured.out

    def test_cli_diff_latex_and_pretty(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test diff subcommand with --latex and --pretty flags."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "diff", "x**2", "--latex"])
        main()
        assert r"\frac{d}{d x}" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "diff", "x**2", "--pretty"])
        main()
        assert "dx" in capsys.readouterr().out

    def test_cli_integrate_latex_and_pretty(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test integrate subcommand with --latex and --pretty flags."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "integrate", "x**2", "--latex"])
        main()
        assert r"\int" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "integrate", "x**2", "--pretty"])
        main()
        assert "⌠" in capsys.readouterr().out

    def test_cli_limit_latex_and_pretty(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test limit subcommand with --latex and --pretty flags."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "limit", "sin(x)/x", "0", "--latex"])
        main()
        assert r"\lim" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "limit", "sin(x)/x", "0", "--pretty"])
        main()
        assert "lim" in capsys.readouterr().out

    def test_cli_ref_list(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test ref subcommand listing topics."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "ref", "--list"])
        main()
        captured = capsys.readouterr()
        assert "Available study reference topics:" in captured.out
        assert "derivatives" in captured.out

    def test_cli_ref_no_topic(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test ref subcommand with no topic defaults to listing topics."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "ref"])
        main()
        captured = capsys.readouterr()
        assert "Available study reference topics:" in captured.out

    def test_cli_ref_topic(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test ref subcommand showing a specific topic."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "ref", "derivatives"])
        main()
        captured = capsys.readouterr()
        assert "=== Derivatives Reference Cheat Sheet ===" in captured.out

    def test_cli_ref_topic_latex(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test ref subcommand showing a topic in LaTeX format."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "ref", "trig", "--latex"])
        main()
        captured = capsys.readouterr()
        assert r"\section*{Trigonometric Identities Cheat Sheet}" in captured.out

    def test_cli_ref_topic_error(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test ref subcommand with unknown topic."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "ref", "unknown_topic"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unknown reference topic 'unknown_topic'" in captured.err

    # --- Matrix CLI Tests ---

    def test_cli_matrix_operations(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test matrix operations: det, inv, rref, rank, nullity, trace, transpose, charpoly."""
        m_2x2 = "1, 2; 3, 4"
        # Det
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "det", m_2x2])
        main()
        assert "-2" in capsys.readouterr().out

        # Det LaTeX & Pretty
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "det", m_2x2, "--latex"])
        main()
        assert "-2" in capsys.readouterr().out

        # Inv
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "inv", "1, 0; 0, 2"])
        main()
        assert "Matrix" in capsys.readouterr().out

        # RREF
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "rref", m_2x2])
        main()
        assert "RREF:" in capsys.readouterr().out

        # Eigen & Eigenvects
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "eigen", "2, 0; 0, 5"])
        main()
        assert "2: 1" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "eigenvects", "2, 0; 0, 5"])
        main()
        assert "λ = 2" in capsys.readouterr().out

        # Rank & Nullity
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "rank", m_2x2])
        main()
        assert "Rank: 2" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "nullity", m_2x2])
        main()
        assert "Nullity: 0" in capsys.readouterr().out

        # Trace
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "trace", m_2x2])
        main()
        assert "5" in capsys.readouterr().out

        # Transpose
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "transpose", m_2x2])
        main()
        assert "Matrix" in capsys.readouterr().out

        # Charpoly
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "charpoly", m_2x2])
        main()
        assert "lambda" in capsys.readouterr().out

    def test_cli_matrix_errors(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test matrix error handling."""
        # Non-square det
        monkeypatch.setattr(sys, "argv", ["mathstore", "matrix", "det", "1, 2, 3; 4, 5, 6"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
        assert "Error executing 'matrix'" in capsys.readouterr().err

    # --- Stats CLI Tests ---

    def test_cli_stats_summary(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test stats summary command."""
        data_str = "10, 12, 14, 15, 18"
        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "summary", data_str])
        main()
        out = capsys.readouterr().out
        assert "Mean:" in out
        assert "Median:" in out

        # LaTeX & Pretty
        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "summary", data_str, "--latex"])
        main()
        assert r"\begin{tabular}" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "summary", data_str, "--pretty"])
        main()
        assert "┌─────────────┬──────────┐" in capsys.readouterr().out

    def test_cli_stats_distributions(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test stats normal, binomial, and poisson distributions."""
        # Normal
        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "normal", "1.96", "--mu", "0", "--sigma", "1"])
        main()
        out_n = capsys.readouterr().out
        assert "Normal N" in out_n
        assert "z-score:" in out_n

        # Binomial
        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "binomial", "2", "--n", "4", "--p", "0.5"])
        main()
        out_b = capsys.readouterr().out
        assert "Binomial" in out_b
        assert "P(X = k):" in out_b

        # Poisson
        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "poisson", "1", "--lam", "2.0"])
        main()
        out_p = capsys.readouterr().out
        assert "Poisson" in out_p

    def test_cli_stats_inference(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test stats CI and t-test commands."""
        data_str = "10, 12, 11, 14, 13"
        # CI
        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "ci", data_str, "--confidence", "0.95"])
        main()
        assert "Confidence Interval:" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "ci", data_str, "--latex"])
        main()
        assert r"\text{ CI}" in capsys.readouterr().out

        # T-test
        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "ttest", data_str, "--pop-mean", "10.0"])
        main()
        assert "t_statistic" in capsys.readouterr().out

        monkeypatch.setattr(sys, "argv", ["mathstore", "stats", "ttest", data_str, "--pop-mean", "10.0", "--latex"])
        main()
        assert "t =" in capsys.readouterr().out

    def test_cli_solve_steps(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test solve subcommand with --steps flag."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "solve", "2*x + 4 = 10", "--steps"])
        main()
        captured = capsys.readouterr().out
        assert "Step-by-step solution for 2*x + 4 = 10:" in captured
        assert "Linear form" in captured or "linear" in captured.lower()
        assert "Solution: x = [3]" in captured

    def test_cli_diff_steps(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test diff subcommand with --steps flag."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "diff", "x**2 * sin(x)", "--steps"])
        main()
        captured = capsys.readouterr().out
        assert "Step-by-step differentiation of x**2 * sin(x):" in captured
        assert "Product Rule" in captured
        assert "Derivative (order 1):" in captured

    def test_cli_integrate_steps(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test integrate subcommand with --steps flag."""
        monkeypatch.setattr(sys, "argv", ["mathstore", "integrate", "x * exp(x)", "--steps"])
        main()
        captured = capsys.readouterr().out
        assert "Step-by-step integration of x * exp(x):" in captured
        assert "Parts" in captured or "parts" in captured.lower()
        assert "Integral:" in captured

    def test_cli_integrate_definite_steps(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test integrate subcommand with limits and --steps flag."""
        monkeypatch.setattr(
            sys, "argv", ["mathstore", "integrate", "x**2", "--limits", "0", "2", "--steps"]
        )
        main()
        captured = capsys.readouterr().out
        assert "Step-by-step integration of x**2 definite integral from 0.0 to 2.0:" in captured
        assert "Fundamental Theorem of Calculus" in captured
        assert "Integral: 2.666" in captured

    def test_cli_practice_generate_single(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test practice subcommand in non-interactive generate mode."""
        monkeypatch.setattr(
            sys, "argv", ["mathstore", "practice", "--generate", "--topic", "algebra", "--seed", "42"]
        )
        main()
        captured = capsys.readouterr().out
        assert "[ALGEBRA]" in captured
        assert "Hint:" in captured
        assert "Step-by-step solution:" in captured

    def test_cli_practice_generate_multiple(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test practice subcommand generating multiple questions."""
        monkeypatch.setattr(
            sys, "argv", ["mathstore", "practice", "--generate", "-n", "2", "--seed", "42"]
        )
        main()
        captured = capsys.readouterr().out
        assert "Question #1:" in captured
        assert "Question #2:" in captured

    def test_cli_practice_interactive(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
        """Test practice subcommand interactive mode with quit command."""
        import builtins

        monkeypatch.setattr(builtins, "input", lambda _: "quit")
        monkeypatch.setattr(sys, "argv", ["mathstore", "practice", "derivatives"])
        main()
        captured = capsys.readouterr().out
        assert "MathStore University Practice & Revision Quizzer" in captured
        assert "Exiting practice session early" in captured



