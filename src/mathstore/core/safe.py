"""Safe parsing and evaluation utilities for mathematical expressions."""

from __future__ import annotations

import re
from typing import Any

import sympy as sp

DANGEROUS_PATTERNS = [
    r"__",
    r"\b(?:import|eval|exec|compile|open|builtins|globals|locals|getattr|setattr|delattr|breakpoint|subprocess|os|sys|shutil)\b",
]


def safe_sympify(text: Any, locals_dict: dict[str, Any] | None = None) -> sp.Basic:
    """
    Safely parse an expression into a SymPy object, blocking dangerous code injection vectors.

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
            raise ValueError("Invalid or unsafe expression: forbidden pattern detected.")

    try:
        return sp.sympify(raw, locals=locals_dict)
    except Exception as e:
        raise ValueError(f"Failed to parse mathematical expression '{text}': {e}") from e
