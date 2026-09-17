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


