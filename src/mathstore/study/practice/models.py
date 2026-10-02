from dataclasses import dataclass, field
from typing import Any

__all__ = ["PracticeQuestion"]


@dataclass
class PracticeQuestion:
    """Represents an interactive practice problem with solutions, hints, and validation metadata."""

    topic: str
    difficulty: str
    prompt: str
    expected_answer: str
    hint: str
    steps: list[str] = field(default_factory=list)
    question_type: str = (
        "symbolic"  # "derivative", "integral", "roots", "number", "symbolic"
    )
    correct_value: Any = None
    variable: str = "x"
    is_definite: bool = False
    tolerance: float = 1e-2
    subtype: str = ""