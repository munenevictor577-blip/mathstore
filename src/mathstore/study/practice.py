import random
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from mathstore.core.safe import safe_sympify
from mathstore.study.steps import (
    get_derivative_steps,
    get_equation_steps,
    get_integral_steps,
)

TOPIC_ALIASES = {
    "calc": "derivatives",
    "diff": "derivatives",
    "derivative": "derivatives",
    "derivatives": "derivatives",
    "calculus": "derivatives",
    "int": "integrals",
    "integrate": "integrals",
    "integral": "integrals",
    "integrals": "integrals",
    "alg": "algebra",
    "eq": "algebra",
    "equations": "algebra",
    "solve": "algebra",
    "algebra": "algebra",
    "matrix": "matrix",
    "matrices": "matrix",
    "linalg": "matrix",
    "linear_algebra": "matrix",
    "stat": "stats",
    "stats": "stats",
    "statistics": "stats",
    "all": "all",
}

CANONICAL_TOPICS = ["derivatives", "integrals", "algebra", "matrix", "stats"]


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


def _gen_derivative_question(difficulty: str, rng: random.Random) -> PracticeQuestion:
    x = sp.Symbol("x")
    if difficulty == "easy":
        choice = rng.choice(["poly", "trig"])
        if choice == "poly":
            a = rng.randint(2, 6)
            n = rng.randint(2, 4)
            b = rng.randint(1, 9)
            expr = a * x**n + b * x
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = "Recall the power rule: d/dx[x^n] = n*x^(n-1) and sum rule."
        else:
            a = rng.randint(2, 5)
            fn = rng.choice([sp.sin, sp.cos])
            expr = a * fn(x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = (
                f"Recall the derivative of {fn.__name__}(x) and factor out constants."
            )

    elif difficulty == "medium":
        choice = rng.choice(["product", "chain_exp", "chain_trig"])
        if choice == "product":
            n = rng.choice([1, 2])
            fn = rng.choice([sp.sin, sp.exp])
            expr = (x**n) * fn(x)
            ans = sp.diff(expr, x)
            prompt = f"Differentiate using the product rule: f(x) = {expr}"
            hint = "Recall the Product Rule: (u*v)' = u'*v + u*v'."
        elif choice == "chain_exp":
            k = rng.choice([2, 3, 4])
            expr = sp.exp(k * x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = "Recall the Chain Rule: d/dx[exp(k*x)] = k * exp(k*x)."
        else:
            k = rng.choice([2, 3, 4])
            fn = rng.choice([sp.sin, sp.cos])
            expr = fn(k * x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = f"Recall the Chain Rule: d/dx[{fn.__name__}(k*x)] = {fn.__name__}'(k*x) * k."

    else:  # hard
        choice = rng.choice(["composite_log", "prod_trig_exp", "quotient"])
        if choice == "composite_log":
            k = rng.randint(2, 4)
            expr = sp.log(k * x**2 + 1)
            ans = sp.diff(expr, x)
            prompt = f"Differentiate the composite function: f(x) = {expr}"
            hint = "Recall the logarithmic chain rule: d/dx[ln(u)] = (1/u) * u'."
        elif choice == "prod_trig_exp":
            k = rng.choice([2, 3])
            expr = sp.exp(k * x) * sp.sin(x)
            ans = sp.diff(expr, x)
            prompt = f"Differentiate using product and chain rules: f(x) = {expr}"
            hint = "Apply the Product Rule (u*v)' = u'*v + u*v' with u=exp(k*x) and v=sin(x)."
        else:
            c = rng.randint(1, 4)
            expr = x / (x + c)
            ans = sp.diff(expr, x)
            prompt = f"Differentiate using the quotient rule: f(x) = {expr}"
            hint = "Recall the Quotient Rule: (u/v)' = (u'*v - u*v') / v^2."

    steps = get_derivative_steps(str(expr), "x")
    return PracticeQuestion(
        topic="derivatives",
        difficulty=difficulty,
        prompt=prompt,
        expected_answer=str(ans),
        hint=hint,
        steps=steps,
        question_type="derivative",
        correct_value=ans,
        variable="x",
    )


def _gen_integral_question(difficulty: str, rng: random.Random) -> PracticeQuestion:
    x = sp.Symbol("x")
    if difficulty == "easy":
        choice = rng.choice(["poly", "trig"])
        if choice == "poly":
            a = rng.randint(2, 5)
            n = rng.randint(1, 3)
            c = rng.randint(1, 5)
            expr = a * x**n + c
            ans = sp.integrate(expr, x)
            prompt = f"Evaluate the indefinite integral: ∫ ({expr}) dx"
            hint = "Recall the power rule: ∫ x^n dx = x^(n+1)/(n+1) + C."
        else:
            a = rng.randint(2, 4)
            fn = rng.choice([sp.sin, sp.cos])
            expr = a * fn(x)
            ans = sp.integrate(expr, x)
            prompt = f"Evaluate the indefinite integral: ∫ ({expr}) dx"
            hint = f"Recall that ∫ {fn.__name__}(x) dx = {sp.integrate(fn(x), x)} + C."
        steps = get_integral_steps(str(expr), "x")
        return PracticeQuestion(
            topic="integrals",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=f"{ans} + C",
            hint=hint,
            steps=steps,
            question_type="integral",
            correct_value=ans,
            variable="x",
            is_definite=False,
        )

    if difficulty == "medium":
        choice = rng.choice(["u_sub", "exp", "reciprocal", "definite"])
        if choice == "u_sub":
            k = rng.choice([2, 3, 4])
            fn = rng.choice([sp.sin, sp.cos])
            expr = fn(k * x)
            ans = sp.integrate(expr, x)
            prompt = f"Evaluate using u-substitution: ∫ {expr} dx"
            hint = f"Let u = {k}*x, then du = {k} dx."
            steps = get_integral_steps(str(expr), "x")
            return PracticeQuestion(
                topic="integrals",
                difficulty=difficulty,
                prompt=prompt,
                expected_answer=f"{ans} + C",
                hint=hint,
                steps=steps,
                question_type="integral",
                correct_value=ans,
                variable="x",
                is_definite=False,
            )
        if choice == "exp":
            k = rng.choice([2, 3])
            expr = sp.exp(k * x)
            ans = sp.integrate(expr, x)
            prompt = f"Evaluate: ∫ {expr} dx"
            hint = f"Recall: ∫ exp(k*x) dx = exp(k*x)/k + C with k = {k}."
            steps = get_integral_steps(str(expr), "x")
            return PracticeQuestion(
                topic="integrals",
                difficulty=difficulty,
                prompt=prompt,
                expected_answer=f"{ans} + C",
                hint=hint,
                steps=steps,
                question_type="integral",
                correct_value=ans,
                variable="x",
                is_definite=False,
            )
        if choice == "reciprocal":
            a = rng.randint(2, 5)
            expr = a / x
            ans = a * sp.log(x)
            prompt = f"Evaluate: ∫ ({expr}) dx"
            hint = "Recall: ∫ 1/x dx = ln|x| + C."
            steps = get_integral_steps(str(expr), "x")
            return PracticeQuestion(
                topic="integrals",
                difficulty=difficulty,
                prompt=prompt,
                expected_answer=f"{ans} + C",
                hint=hint,
                steps=steps,
                question_type="integral",
                correct_value=ans,
                variable="x",
                is_definite=False,
            )
        # definite
        upper = rng.randint(1, 3)
        expr = x**2
        ans = sp.integrate(expr, (x, 0, upper))
        prompt = f"Evaluate the definite integral: ∫[0 to {upper}] ({expr}) dx"
        hint = "Apply Fundamental Theorem of Calculus: F(b) - F(a) where F(x) = x^3/3."
        steps = get_integral_steps(str(expr), "x", limits=(0, upper))
        return PracticeQuestion(
            topic="integrals",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=str(ans),
            hint=hint,
            steps=steps,
            question_type="integral",
            correct_value=ans,
            variable="x",
            is_definite=True,
        )

    # hard
    choice = rng.choice(["parts_exp", "parts_trig", "arctan_form"])
    if choice == "parts_exp":
        expr = x * sp.exp(x)
        ans = sp.integrate(expr, x)
        prompt = f"Evaluate using integration by parts: ∫ ({expr}) dx"
        hint = "Choose u = x, dv = exp(x) dx. Formula: ∫ u dv = u*v - ∫ v du."
    elif choice == "parts_trig":
        expr = x * sp.cos(x)
        ans = sp.integrate(expr, x)
        prompt = f"Evaluate using integration by parts: ∫ ({expr}) dx"
        hint = "Choose u = x, dv = cos(x) dx. Formula: ∫ u dv = u*v - ∫ v du."
    else:
        expr = 1 / (x**2 + 1)
        ans = sp.atan(x)
        prompt = f"Evaluate the standard rational integral: ∫ ({expr}) dx"
        hint = "Recall standard inverse trigonometric integral form: ∫ 1/(x^2 + 1) dx = atan(x) + C."

    steps = get_integral_steps(str(expr), "x")
    return PracticeQuestion(
        topic="integrals",
        difficulty=difficulty,
        prompt=prompt,
        expected_answer=f"{ans} + C",
        hint=hint,
        steps=steps,
        question_type="integral",
        correct_value=ans,
        variable="x",
        is_definite=False,
    )


def _gen_algebra_question(difficulty: str, rng: random.Random) -> PracticeQuestion:
    x = sp.Symbol("x")
    if difficulty == "easy":
        a = rng.randint(2, 6)
        sol = rng.randint(1, 9)
        b = rng.randint(1, 15)
        c = a * sol + b
        eq_str = f"{a}*x + {b} = {c}"
        prompt = f"Solve for x: {eq_str}"
        hint = f"Subtract {b} from both sides, then divide by {a}."
        steps = get_equation_steps(eq_str, "x")
        return PracticeQuestion(
            topic="algebra",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=str(sol),
            hint=hint,
            steps=steps,
            question_type="roots",
            correct_value=[sp.Integer(sol)],
            variable="x",
        )

    if difficulty == "medium":
        choice = rng.choice(["both_sides", "monic_quadratic"])
        if choice == "both_sides":
            a = rng.randint(4, 8)
            c = rng.randint(1, a - 1)
            sol = rng.randint(2, 8)
            d = rng.randint(1, 10)
            b = c * sol + d - a * sol
            lhs_expr = a * x + b
            rhs_expr = c * x + d
            eq_str = f"{lhs_expr} = {rhs_expr}"
            prompt = f"Solve for x: {eq_str}"
            hint = "Collect all x terms on one side and constant terms on the other."
            steps = get_equation_steps(eq_str, "x")
            return PracticeQuestion(
                topic="algebra",
                difficulty=difficulty,
                prompt=prompt,
                expected_answer=str(sol),
                hint=hint,
                steps=steps,
                question_type="roots",
                correct_value=[sp.Integer(sol)],
                variable="x",
            )
        # monic quadratic
        r1 = rng.randint(1, 5)
        r2 = rng.randint(6, 9)
        eq_expr = sp.expand((x - r1) * (x - r2))
        eq_str = f"{eq_expr} = 0"
        prompt = f"Find all real solutions for x: {eq_str}"
        hint = f"Factor into (x - {r1})*(x - {r2}) = 0 or use the quadratic formula."
        steps = get_equation_steps(eq_str, "x")
        return PracticeQuestion(
            topic="algebra",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=f"{r1}, {r2}",
            hint=hint,
            steps=steps,
            question_type="roots",
            correct_value=[sp.Integer(r1), sp.Integer(r2)],
            variable="x",
        )

    # hard: quadratic with distinct positive/negative roots
    r1 = rng.randint(-6, -1)
    r2 = rng.randint(1, 6)
    eq_expr = sp.expand((x - r1) * (x - r2))
    eq_str = f"{eq_expr} = 0"
    prompt = f"Solve the quadratic equation for all roots: {eq_str}"
    hint = "Use the quadratic formula: x = (-b ± √(b^2 - 4ac)) / (2a)."
    steps = get_equation_steps(eq_str, "x")
    return PracticeQuestion(
        topic="algebra",
        difficulty=difficulty,
        prompt=prompt,
        expected_answer=f"{r1}, {r2}",
        hint=hint,
        steps=steps,
        question_type="roots",
        correct_value=[sp.Integer(r1), sp.Integer(r2)],
        variable="x",
    )


def _gen_matrix_question(difficulty: str, rng: random.Random) -> PracticeQuestion:
    if difficulty == "easy":
        choice = rng.choice(["trace", "diag_det"])
        if choice == "trace":
            a, b = rng.randint(1, 6), rng.randint(1, 6)
            c, d = rng.randint(1, 6), rng.randint(1, 6)
            trace_val = a + d
            prompt = f"Calculate the trace of matrix A = [[{a}, {b}], [{c}, {d}]]"
            hint = "The trace is the sum of diagonal elements: trace(A) = a11 + a22."
            steps = [
                f"Given matrix A = [[{a}, {b}], [{c}, {d}]]",
                f"Identify diagonal entries: a11 = {a}, a22 = {d}",
                f"Calculate trace: {a} + {d} = {trace_val}",
            ]
            return PracticeQuestion(
                topic="matrix",
                difficulty=difficulty,
                prompt=prompt,
                expected_answer=str(trace_val),
                hint=hint,
                steps=steps,
                question_type="number",
                correct_value=float(trace_val),
            )
        a = rng.randint(2, 7)
        d = rng.randint(2, 7)
        det_val = a * d
        prompt = f"Find the determinant of the diagonal matrix A = [[{a}, 0], [0, {d}]]"
        hint = "For a diagonal matrix, det is the product of diagonal elements: det = a11 * a22."
        steps = [
            f"Given diagonal matrix A = [[{a}, 0], [0, {d}]]",
            f"Compute product of diagonal entries: {a} * {d} = {det_val}",
        ]
        return PracticeQuestion(
            topic="matrix",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=str(det_val),
            hint=hint,
            steps=steps,
            question_type="number",
            correct_value=float(det_val),
        )

    if difficulty == "medium":
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        c, d = rng.randint(1, 5), rng.randint(1, 5)
        det_val = a * d - b * c
        prompt = f"Find the determinant of matrix A = [[{a}, {b}], [{c}, {d}]]"
        hint = "Use formula det(A) = a*d - b*c."
        steps = [
            f"Given 2x2 matrix A = [[{a}, {b}], [{c}, {d}]]",
            "Formula: det(A) = a*d - b*c",
            f"Substitute values: ({a})*({d}) - ({b})*({c}) = {a * d} - {b * c} = {det_val}",
        ]
        return PracticeQuestion(
            topic="matrix",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=str(det_val),
            hint=hint,
            steps=steps,
            question_type="number",
            correct_value=float(det_val),
        )

    # hard: 3x3 trace or upper triangular determinant
    choice = rng.choice(["3x3_trace", "triangular_det"])
    if choice == "3x3_trace":
        d1, d2, d3 = rng.randint(1, 7), rng.randint(1, 7), rng.randint(1, 7)
        trace_val = d1 + d2 + d3
        prompt = (
            f"Find the trace of matrix A = [[{d1}, 2, 3], [0, {d2}, 5], [1, 4, {d3}]]"
        )
        hint = "Sum the three main diagonal elements: a11 + a22 + a33."
        steps = [
            "Identify the main diagonal entries: a11, a22, a33",
            f"Entries: {d1}, {d2}, {d3}",
            f"Trace = {d1} + {d2} + {d3} = {trace_val}",
        ]
        return PracticeQuestion(
            topic="matrix",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=str(trace_val),
            hint=hint,
            steps=steps,
            question_type="number",
            correct_value=float(trace_val),
        )
    d1, d2, d3 = rng.randint(2, 5), rng.randint(2, 5), rng.randint(2, 5)
    det_val = d1 * d2 * d3
    prompt = f"Find the determinant of upper-triangular matrix A = [[{d1}, 3, 1], [0, {d2}, 4], [0, 0, {d3}]]"
    hint = "For any triangular matrix, determinant equals the product of its diagonal entries."
    steps = [
        "Matrix is upper triangular (all entries below diagonal are 0)",
        "Property: det(A) = product of diagonal entries",
        f"Calculate: {d1} * {d2} * {d3} = {det_val}",
    ]
    return PracticeQuestion(
        topic="matrix",
        difficulty=difficulty,
        prompt=prompt,
        expected_answer=str(det_val),
        hint=hint,
        steps=steps,
        question_type="number",
        correct_value=float(det_val),
    )


def _gen_stats_question(difficulty: str, rng: random.Random) -> PracticeQuestion:
    if difficulty == "easy":
        choice = rng.choice(["mean", "median"])
        if choice == "mean":
            vals = [rng.randint(2, 10) * 2 for _ in range(5)]
            mean_val = sum(vals) / len(vals)
            prompt = f"Calculate the mean of the dataset: {vals}"
            hint = "Mean = (sum of all values) / (number of observations)."
            steps = [
                f"Dataset has n = {len(vals)} values: {vals}",
                f"Compute sum: {' + '.join(map(str, vals))} = {sum(vals)}",
                f"Divide by n = {len(vals)}: {sum(vals)} / {len(vals)} = {mean_val:.2f}",
            ]
            return PracticeQuestion(
                topic="stats",
                difficulty=difficulty,
                prompt=prompt,
                expected_answer=f"{mean_val:.2f}",
                hint=hint,
                steps=steps,
                question_type="number",
                correct_value=float(mean_val),
            )
        vals = [rng.randint(1, 20) for _ in range(5)]
        sorted_vals = sorted(vals)
        median_val = sorted_vals[2]
        prompt = f"Find the median of the dataset: {vals}"
        hint = "Sort the numbers from lowest to highest and pick the middle element."
        steps = [
            f"Original dataset: {vals}",
            f"Sort numbers: {sorted_vals}",
            f"For n = 5 (odd), the median is at index (5+1)/2 = 3: {median_val}",
        ]
        return PracticeQuestion(
            topic="stats",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=str(median_val),
            hint=hint,
            steps=steps,
            question_type="number",
            correct_value=float(median_val),
        )

    if difficulty == "medium":
        choice = rng.choice(["zscore", "range"])
        if choice == "zscore":
            mu = rng.choice([50.0, 60.0, 70.0, 100.0])
            sigma = rng.choice([5.0, 10.0, 15.0])
            mult = rng.choice([-2, -1, 1, 2])
            x_val = mu + mult * sigma
            z_val = (x_val - mu) / sigma
            prompt = f"Find the z-score for observation x = {x_val} from a population with mean μ = {mu} and standard deviation σ = {sigma}"
            hint = "Recall the standard score formula: z = (x - μ) / σ."
            steps = [
                f"Formula: z = (x - μ) / σ with x = {x_val}, μ = {mu}, σ = {sigma}",
                f"Calculate difference: {x_val} - {mu} = {x_val - mu}",
                f"Divide by σ: ({x_val - mu}) / {sigma} = {z_val:.2f}",
            ]
            return PracticeQuestion(
                topic="stats",
                difficulty=difficulty,
                prompt=prompt,
                expected_answer=f"{z_val:.2f}",
                hint=hint,
                steps=steps,
                question_type="number",
                correct_value=float(z_val),
            )
        vals = [rng.randint(10, 50) for _ in range(5)]
        range_val = max(vals) - min(vals)
        prompt = f"Calculate the statistical range of the dataset: {vals}"
        hint = "Range = maximum value - minimum value."
        steps = [
            f"Identify maximum: max = {max(vals)}",
            f"Identify minimum: min = {min(vals)}",
            f"Compute range: {max(vals)} - {min(vals)} = {range_val}",
        ]
        return PracticeQuestion(
            topic="stats",
            difficulty=difficulty,
            prompt=prompt,
            expected_answer=str(range_val),
            hint=hint,
            steps=steps,
            question_type="number",
            correct_value=float(range_val),
        )

    # hard: median of 6 numbers (even dataset)
    vals = [rng.randint(2, 25) for _ in range(6)]
    sorted_vals = sorted(vals)
    median_val = (sorted_vals[2] + sorted_vals[3]) / 2.0
    prompt = f"Find the median of the 6-element dataset: {vals}"
    hint = (
        "For an even sample size, the median is the average of the two middle elements."
    )
    steps = [
        f"Original dataset: {vals}",
        f"Sorted dataset: {sorted_vals}",
        f"Two middle elements (positions 3 and 4): {sorted_vals[2]} and {sorted_vals[3]}",
        f"Compute average: ({sorted_vals[2]} + {sorted_vals[3]}) / 2 = {median_val:.2f}",
    ]
    return PracticeQuestion(
        topic="stats",
        difficulty=difficulty,
        prompt=prompt,
        expected_answer=f"{median_val:.2f}",
        hint=hint,
        steps=steps,
        question_type="number",
        correct_value=float(median_val),
    )


def generate_question(
    topic: str = "all",
    difficulty: str = "medium",
    seed: int | None = None,
    rng: random.Random | None = None,
) -> PracticeQuestion:
    """Generates a randomized practice problem according to requested topic and difficulty."""
    if rng is None:
        rng = random.Random(seed)

    canonical_topic = TOPIC_ALIASES.get(topic.lower().strip(), "all")
    if canonical_topic == "all":
        canonical_topic = rng.choice(CANONICAL_TOPICS)

    chosen_diff = difficulty.lower().strip()
    if chosen_diff not in ("easy", "medium", "hard"):
        chosen_diff = rng.choice(["easy", "medium", "hard"])

    if canonical_topic == "derivatives":
        return _gen_derivative_question(chosen_diff, rng)
    if canonical_topic == "integrals":
        return _gen_integral_question(chosen_diff, rng)
    if canonical_topic == "algebra":
        return _gen_algebra_question(chosen_diff, rng)
    if canonical_topic == "matrix":
        return _gen_matrix_question(chosen_diff, rng)
    if canonical_topic == "stats":
        return _gen_stats_question(chosen_diff, rng)

    return _gen_derivative_question(chosen_diff, rng)


def format_question_card(q: PracticeQuestion, index: int | None = None) -> str:
    """Formats a single practice question with hints, answers, and steps for non-interactive output."""
    prefix = f"Question #{index}: " if index is not None else ""
    lines = [
        f"[{q.topic.upper()}] (Difficulty: {q.difficulty})",
        f"{prefix}{q.prompt}",
        f"Hint: {q.hint}",
        f"Expected Answer: {q.expected_answer}",
        "Step-by-step solution:",
    ]
    for idx, s in enumerate(q.steps, 1):
        lines.append(f"  {idx}. {s}")
    return "\n".join(lines)


class PracticeSession:
    """Interactive CLI practice quizzer with score tracking, hints, and derivations."""

    def __init__(
        self,
        topic: str = "all",
        count: int = 5,
        difficulty: str = "medium",
        seed: int | None = None,
        input_func: Callable[[str], str] | None = None,
        print_func: Callable[..., None] | None = None,
    ):
        self.topic = topic
        self.count = max(1, count)
        self.difficulty = difficulty
        self.rng = random.Random(seed)
        self.input_func = input_func if input_func is not None else input
        self.print_func = print_func if print_func is not None else print

    def run(self) -> dict[str, Any]:
        """Runs the interactive practice session."""
        self.print_func("=" * 60)
        self.print_func("  MathStore University Practice & Revision Quizzer")
        self.print_func(
            f"  Topic: {self.topic.capitalize()} | Difficulty: {self.difficulty.capitalize()} | Questions: {self.count}"
        )
        self.print_func(
            "  Commands: 'hint' for a hint, 'skip' to reveal solution, 'quit' to exit."
        )
        self.print_func("=" * 60)

        score = 0
        skipped = 0
        completed = 0

        for i in range(1, self.count + 1):
            q = generate_question(
                topic=self.topic,
                difficulty=self.difficulty,
                rng=self.rng,
            )

            self.print_func(
                f"\n[Question {i}/{self.count}] ({q.topic.capitalize()} - {q.difficulty})"
            )
            self.print_func(f"  {q.prompt}")

            attempts = 0
            while True:
                try:
                    user_resp = self.input_func("  Your answer > ").strip()
                except (EOFError, KeyboardInterrupt):
                    self.print_func("\nSession ended by user.")
                    return {
                        "total": self.count,
                        "completed": completed,
                        "correct": score,
                        "skipped": skipped,
                        "percentage": (score / max(1, completed)) * 100
                        if completed
                        else 0.0,
                    }

                if user_resp.lower() == "quit":
                    self.print_func("\nExiting practice session early...")
                    self._show_summary(score, completed, skipped)
                    return {
                        "total": self.count,
                        "completed": completed,
                        "correct": score,
                        "skipped": skipped,
                        "percentage": (score / max(1, completed)) * 100
                        if completed
                        else 0.0,
                    }

                if user_resp.lower() == "hint":
                    self.print_func(f"  💡 Hint: {q.hint}")
                    continue

                if user_resp.lower() == "skip":
                    self.print_func(
                        f"  ⏭ Skipped. Expected answer: {q.expected_answer}"
                    )
                    self.print_func("  Step-by-step solution:")
                    for idx, s in enumerate(q.steps, 1):
                        self.print_func(f"    {idx}. {s}")
                    skipped += 1
                    completed += 1
                    break

                is_correct, feedback = check_answer(user_resp, q)
                if is_correct:
                    self.print_func(f"  {feedback}")
                    score += 1
                    completed += 1
                    break

                attempts += 1
                self.print_func(f"  ✗ {feedback}")
                if attempts >= 2:
                    self.print_func(f"  The correct answer was: {q.expected_answer}")
                    self.print_func("  Step-by-step solution:")
                    for idx, s in enumerate(q.steps, 1):
                        self.print_func(f"    {idx}. {s}")
                    completed += 1
                    break

        self._show_summary(score, completed, skipped)
        pct = (score / max(1, completed)) * 100 if completed else 0.0
        return {
            "total": self.count,
            "completed": completed,
            "correct": score,
            "skipped": skipped,
            "percentage": pct,
        }

    def _show_summary(self, score: int, completed: int, skipped: int) -> None:
        self.print_func("\n" + "=" * 60)
        self.print_func("  Practice Quiz Completed!")
        pct = (score / max(1, completed)) * 100 if completed else 0.0
        self.print_func(f"  Questions Attempted: {completed}/{self.count}")
        self.print_func(f"  Correct Answers:     {score}")
        self.print_func(f"  Skipped:             {skipped}")
        self.print_func(f"  Score:               {pct:.1f}%")

        if pct >= 80.0:
            self.print_func("  🌟 Outstanding! You have mastered these concepts.")
        elif pct >= 60.0:
            self.print_func(
                "  👍 Good effort! Review the tricky derivations and try again."
            )
        else:
            self.print_func(
                "  📚 Keep revising! Use 'mathstore ref' to consult cheat sheets."
            )
        self.print_func("=" * 60)
