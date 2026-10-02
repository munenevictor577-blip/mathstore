"""Practice question module for university mathematics study & active-recall revision."""

from mathstore.study.practice.evaluators import (
    _normalize_input_str,
    check_answer,
)
from mathstore.study.practice.generators import (
    CANONICAL_TOPICS,
    TOPIC_ALIASES,
    _gen_algebra_question,
    _gen_derivative_question,
    _gen_integral_question,
    _gen_matrix_question,
    _gen_stats_question,
    _randint_nonzero,
    _select_subtype,
    generate_question,
    randit_nonzero,
    randint_nonzero,
)
from mathstore.study.practice.models import PracticeQuestion
from mathstore.study.practice.session import (
    PracticeSession,
    format_question_card,
)

__all__ = [
    "CANONICAL_TOPICS",
    "TOPIC_ALIASES",
    "PracticeQuestion",
    "PracticeSession",
    "_gen_algebra_question",
    "_gen_derivative_question",
    "_gen_integral_question",
    "_gen_matrix_question",
    "_gen_stats_question",
    "_normalize_input_str",
    "_randint_nonzero",
    "_select_subtype",
    "check_answer",
    "format_question_card",
    "generate_question",
    "randit_nonzero",
    "randint_nonzero",
]