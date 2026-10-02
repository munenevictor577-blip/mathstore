"""Safe parsing and evaluation utilities for mathematical expressions."""

from __future__ import annotations

import re
from typing import Any

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    function_exponentiation,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

CALCULUS_TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
    function_exponentiation,
)

DANGEROUS_PATTERNS = [
    r"__",
    r"\b(?:import|eval|exec|compile|open|builtins|globals|locals|getattr|setattr|delattr|breakpoint|subprocess|os|sys|shutil)\b",
]


def safe_sympify(
    text: Any,
    locals_dict: dict[str, Any] | None = None,
    variable: str | None = None,
) -> sp.Basic:
    """
    Safely parse an expression into a SymPy object, blocking dangerous code injection vectors
    while supporting natural mathematical text (e.g. '2^x sin x', '2x + 4', 'x^2', 'e^x', 'sin^2 x').

    Raises:
        ValueError: If a dangerous token or syntax error is encountered.
    """
    if isinstance(text, sp.Basic):
        return text

    if not isinstance(text, str):
        try:
            return sp.sympify(text, locals=locals_dict)
        except Exception as e:
            raise ValueError(f"Failed to parse value {text!r}: {e}") from e

    raw = text.strip()
    if not raw:
        raise ValueError("Expression string cannot be empty.")

    for pat in DANGEROUS_PATTERNS:
        if re.search(pat, raw, flags=re.IGNORECASE):
            raise ValueError(
                "Invalid or unsafe expression: forbidden pattern detected."
            )

    # Normalize mathematical symbols
    cleaned = raw.replace("·", "*").replace("×", "*")
    cleaned = re.sub(r"\|([^|]+)\|", r"Abs(\1)", cleaned)

    # Handle natural language equations with '='
    if "=" in cleaned:
        parts = cleaned.split("=")
        if len(parts) != 2:
            raise ValueError(f"Equation must contain at most one '=' sign: '{raw}'")
        lhs = safe_sympify(parts[0].strip(), locals_dict=locals_dict, variable=variable)
        rhs = safe_sympify(parts[1].strip(), locals_dict=locals_dict, variable=variable)
        return sp.Eq(lhs, rhs)

    # Clean optional trailing differential notation (e.g., '2^x sin x dx' -> '2^x sin x')
    if variable:
        cleaned = re.sub(r"\s*d" + re.escape(variable) + r"$", "", cleaned)
    else:
        cleaned = re.sub(r"\s*d[a-zA-Z]$", "", cleaned)

    cleaned = cleaned.strip()

    # Configure local symbols and constants
    locs: dict[str, Any] = {"pi": sp.pi, "I": sp.I}
    if variable != "e":
        locs["e"] = sp.E
        locs["E"] = sp.E
    else:
        locs["e"] = sp.Symbol("e")

    if locals_dict:
        locs.update(locals_dict)

    try:
        return parse_expr(
            cleaned, local_dict=locs, transformations=CALCULUS_TRANSFORMATIONS
        )
    except Exception:
        try:
            return sp.sympify(cleaned, locals=locs)
        except Exception as e:
            raise ValueError(
                f"Failed to parse mathematical expression '{text}': {e}"
            ) from e
