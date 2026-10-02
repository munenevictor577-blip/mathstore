import pytest

import mathstore


def test_init_main(capsys: pytest.CaptureFixture):
    """Test the default entrypoint function in mathstore package __init__."""
    mathstore.main()
    captured = capsys.readouterr()
    assert "Hello from mathstore!" in captured.out


def test_init_exports():
    """Verify top-level package exports."""
    assert hasattr(mathstore, "EquationSolver")
    assert hasattr(mathstore, "CalculusAnalyzer")
    assert hasattr(mathstore, "get_reference")
    assert hasattr(mathstore, "list_topics")
    assert hasattr(mathstore, "main")
