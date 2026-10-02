import re
import sympy as sp

from mathstore.core.safe import safe_sympify
from mathstore.study.practice.models import PracticeQuestion

__all__ = ["_normalize_input_str", "check_answer"]


def _normalize_input_str(text: str) -> str:
    cleaned = text.strip()
    # Replace carets with double asterisks for exponents
    cleaned = cleaned.replace("^", "**")
    # Remove leading variable / derivative / function assignments
    cleaned = re.sub(
        r"^(?:(?:d[a-zA-Z]/d[a-zA-Z])|(?:[a-zA-Z](?:'|\([a-zA-Z]\))*))\s*=\s*",
        "",
        cleaned,
    )
    cleaned = re.sub(r"^ans\s*=\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def check_answer(user_input: str, question: PracticeQuestion) -> tuple[bool, str]:
    """
    Validates a student's answer using symbolic equivalence or numeric tolerance.

    Returns:
        tuple of (is_correct: bool, feedback: str)
    """
    if not user_input or not user_input.strip():
        return False, "Empty answer. Please enter a mathematical expression or value."

    raw = user_input.strip()

    if raw.lower() in ("hint", "skip", "quit", "exit"):
        return False, f"Command '{raw}' entered."

    q_type = question.question_type

    if q_type == "roots":
        try:
            cleaned = re.sub(r"[a-zA-Z]\s*=\s*", "", raw)
            cleaned = cleaned.strip("[]{}()")
            parts = [p.strip() for p in cleaned.split(",") if p.strip()]
            if not parts:
                return False, "Could not identify any roots in your answer."
            user_roots = {
                safe_sympify(
                    _normalize_input_str(p),
                    locals_dict={"sqrt": sp.sqrt, "I": sp.I, "pi": sp.pi, "E": sp.E},
                )
                for p in parts
            }
            if question.correct_value is not None:
                if isinstance(question.correct_value, (list, tuple, set)):
                    raw_correct = list(question.correct_value)
                else:
                    raw_correct = [question.correct_value]
            else:
                ans_cleaned = re.sub(
                    r"[a-zA-Z]\s*=\s*", "", question.expected_answer
                ).strip("[]{}()")
                raw_correct = [p.strip() for p in ans_cleaned.split(",") if p.strip()]

            correct_roots = {
                safe_sympify(
                    _normalize_input_str(str(r)),
                    locals_dict={"sqrt": sp.sqrt, "I": sp.I, "pi": sp.pi, "E": sp.E},
                )
                for r in raw_correct
            }
            if user_roots == correct_roots:
                return True, "✓ Correct! All roots match."
            return (
                False,
                f"Roots do not match. Expected {len(correct_roots)} root(s). Try again or type 'hint'.",
            )
        except Exception as e:  # noqa: BLE001
            return False, f"Could not parse roots format (use e.g. '2, 3'): {e}"

    if q_type == "number":
        try:
            norm = _normalize_input_str(raw)
            val = float(safe_sympify(norm))
            target_raw = (
                question.correct_value
                if question.correct_value is not None
                else question.expected_answer
            )
            target = float(safe_sympify(_normalize_input_str(str(target_raw))))
            if abs(val - target) <= question.tolerance:
                return True, "✓ Correct!"
            return (
                False,
                f"Numerical value is incorrect (got {val:.4f}). Try again or type 'hint'.",
            )
        except Exception as e:  # noqa: BLE001
            return False, f"Could not parse numerical value: {e}"

    if q_type == "integral":
        try:
            norm = _normalize_input_str(raw)
            c_sym = sp.Symbol("C")
            c_lower = sp.Symbol("c")
            user_expr = safe_sympify(norm, locals_dict={"C": c_sym, "c": c_lower})
            var = sp.Symbol(question.variable)

            target_raw = (
                question.correct_value
                if question.correct_value is not None
                else question.expected_answer
            )
            if isinstance(target_raw, str):
                target_norm = re.sub(r"\s*\+\s*[cC]$", "", target_raw.strip())
            else:
                target_norm = str(target_raw)

            if question.is_definite:
                target = safe_sympify(target_norm)
                if sp.simplify(user_expr - target) == 0:
                    return True, "✓ Correct!"
                try:
                    if abs(float(user_expr) - float(target)) <= question.tolerance:
                        return True, "✓ Correct!"
                except (TypeError, ValueError):
                    pass
                return (
                    False,
                    "Calculated definite integral is incorrect. Try again or type 'hint'.",
                )

            # Indefinite integral: derivative of difference with respect to var must be 0
            target_expr = safe_sympify(
                target_norm, locals_dict={"C": c_sym, "c": c_lower}
            )
            diff_wrt_var = sp.diff(user_expr - target_expr, var)
            if sp.simplify(diff_wrt_var) == 0:
                return (
                    True,
                    "✓ Correct! (Antiderivative is equivalent up to an additive constant)",
                )
            return False, "Antiderivative does not match. Try again or type 'hint'."
        except Exception as e:  # noqa: BLE001
            return False, f"Syntax error in mathematical expression: {e}"

    if q_type in ("derivative", "symbolic"):
        try:
            norm = _normalize_input_str(raw)
            user_expr = safe_sympify(norm)
            target_raw = (
                question.correct_value
                if question.correct_value is not None
                else question.expected_answer
            )
            target = safe_sympify(str(target_raw))
            if sp.simplify(user_expr - target) == 0:
                return True, "✓ Correct!"
            return False, "Expression does not match. Try again or type 'hint'."
        except Exception as e:  # noqa: BLE001
            return False, f"Syntax error in expression: {e}"

    return False, "Unsupported question type."