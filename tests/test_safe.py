import pytest
import sympy as sp

from mathstore.core.safe import safe_sympify


def test_safe_sympify_malicious_injection():
    with pytest.raises(ValueError):
        safe_sympify("import os; os.system('clear')")


def test_safe_sympify_blocks_dunder():
    with pytest.raises(ValueError, match="forbidden pattern detected"):
        safe_sympify("__import__('os').system('echo pwned')")


def test_safe_sympify_blocks_keywords():
    for word in [
        "import",
        "eval",
        "exec",
        "open",
        "builtins",
        "subprocess",
        "os",
        "sys",
    ]:
        with pytest.raises(ValueError, match="forbidden pattern detected"):
            safe_sympify(f"{word}('something')")


def test_safe_sympify_allows_normal_math():
    expr = safe_sympify("cos(x) + sin(2*x) + 3*x**2")
    assert expr.has(sp.Symbol("x"))


def test_safe_sympify_invalid_syntax():
    with pytest.raises(ValueError, match="parse"):
        safe_sympify("2 + * x")


def test_safe_sympify_dunder_attributes():
    with pytest.raises(ValueError):
        safe_sympify("__class__.__bases__")


def test_safe_sympify_already_sympy_object():
    """Hits line 42: returns immediately if already a SymPy object."""
    x = sp.Symbol("x")
    assert safe_sympify(x) == x


def test_safe_sympify_non_string_valid():
    """Hits line 45: passes a standard integer."""
    assert safe_sympify(5) == sp.Integer(5)


def test_safe_sympify_non_string_invalid():
    """Hits lines 47-48: fails gracefully on unsympifiable objects."""

    class BadObject:
        def __repr__(self):
            return "invalid_syntax++!!"

    with pytest.raises(ValueError, match="Failed to parse value"):
        safe_sympify(BadObject())


def test_safe_sympify_empty_string():
    """Hits line 52: rejects empty or whitespace strings."""
    with pytest.raises(ValueError, match="Expression string cannot be empty"):
        safe_sympify("   ")


def test_safe_sympify_strip_differential_with_variable():
    """Hits line 64: strips 'dx' when variable='x' is explicitly provided."""
    # "2*x dx" should become "2*x"
    result = safe_sympify("2*x dx", variable="x")
    assert result == sp.sympify("2*x")


def test_safe_sympify_variable_is_e():
    """Hits line 76: treats 'e' as a variable instead of Euler's number."""
    result = safe_sympify("e**2", variable="e")
    e_sym = sp.Symbol("e")
    assert result == e_sym**2


def test_safe_sympify_with_locals_dict():
    """Hits line 79: updates local dictionary with custom variables."""
    custom_sym = sp.Symbol("custom")
    result = safe_sympify("custom * 2", locals_dict={"custom": custom_sym})
    assert result == custom_sym * sp.Integer(2)
