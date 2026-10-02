import random
import sympy as sp

from mathstore.study.practice.models import PracticeQuestion
from mathstore.study.steps import (
    get_derivative_steps,
    get_integral_steps,
    get_equation_steps
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

__all__ = [
    "CANONICAL_TOPICS",
    "TOPIC_ALIASES",
    "_gen_algebra_question",
    "_gen_derivative_question",
    "_gen_integral_question",
    "_gen_matrix_question",
    "_gen_stats_question",
    "_randint_nonzero",
    "_select_subtype",
    "generate_question",
    "randit_nonzero",
    "randint_nonzero",
]


def _select_subtype(
    rng: random.Random,
    subtypes: list[str],
    exclude_subtypes: set[str] | list[str] | None = None,
) -> str:
    """Select a question subtype, preferring ones not yet used in the session."""
    if exclude_subtypes:
        candidates = [s for s in subtypes if s not in exclude_subtypes]
        if candidates:
            return rng.choice(candidates)
    return rng.choice(subtypes)

def randint_nonzero(
    rng: random.Random,
    low: int,
    high: int,
    exclude: tuple[int, ...] | set[int] = (0,),
) -> int:
    """Generate a random integer in [low, high] excluding zero and any optional excluded values."""
    val = rng.randint(low, high)
    while val in exclude:
        val = rng.randint(low, high)
    return val


_randint_nonzero = randint_nonzero
randit_nonzero = randint_nonzero


def _gen_derivative_question(
    difficulty: str,
    rng: random.Random,
    exclude_subtypes: set[str] | list[str] | None = None,
) -> PracticeQuestion:
    x = sp.Symbol("x")
    if difficulty == "easy":
        subtypes = ["poly", "trig", "exp", "log"]
        choice = _select_subtype(rng, subtypes, exclude_subtypes)
        if choice == "poly":
            a = rng.randint(2, 6)
            n = rng.randint(2, 4)
            b = rng.randint(1, 9)
            expr = a * x**n + b * x
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = "Recall the power rule: d/dx[x^n] = n*x^(n-1) and sum rule."
        elif choice == "exp":
            a = randint_nonzero(rng, -5, 5)
            expr = a * sp.exp(x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = "Recall the exponential rule: d/dx[exp(x)] = exp(x)."
        elif choice == "log":
            a = randint_nonzero(rng, -5, 5)
            expr = a * sp.log(x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = "Recall the logarithmic rule: d/dx[ln(x)] = 1/x."
        else:
            a = randint_nonzero(rng, -8, 8)
            fn = rng.choice([sp.sin, sp.cos])
            expr = a * fn(x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = (
                f"Recall the derivative of {fn.__name__}(x) and factor out constants."
            )

    elif difficulty == "medium":
        subtypes = [
            "product",
            "chain_exp",
            "chain_trig",
            "quotient",
            "chain_power",
            "chain_log",
        ]
        choice = _select_subtype(rng, subtypes, exclude_subtypes)
        if choice == "product":
            n = rng.choice([1, 2])
            fn = rng.choice([sp.sin, sp.exp])
            expr = (x**n) * fn(x)
            ans = sp.diff(expr, x)
            prompt = f"Differentiate using the product rule: f(x) = {expr}"
            hint = "Recall the Product Rule: (u*v)' = u'*v + u*v'."
        elif choice == "chain_exp":
            k = randint_nonzero(rng, -5, 7)
            a = randint_nonzero(rng, -3, 4)
            expr = a * sp.exp(k * x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = "Recall the Chain Rule: d/dx[exp(k*x)] = k * exp(k*x)."
        elif choice == "chain_trig":
            k = randint_nonzero(rng, -5, 7)
            fn = rng.choice([sp.sin, sp.cos])
            expr = fn(k * x)
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = f"Recall the Chain Rule: d/dx[{fn.__name__}(k*x)] = {fn.__name__}'(k*x) * k."
        elif choice == "quotient":
            c = randint_nonzero(rng, 1, 5)
            expr = x / (x + c)
            ans = sp.diff(expr, x)
            prompt = f"Differentiate using the quotient rule: f(x) = {expr}"
            hint = "Recall the Quotient Rule: (u/v)' = (u'*v - u*v') / v^2."
        elif choice == "chain_power":
            a = randint_nonzero(rng, 2, 4)
            b = randint_nonzero(rng, -3, 4)
            n = rng.choice([3, 4])
            expr = (a * x + b) ** n
            ans = sp.diff(expr, x)
            prompt = f"Find the derivative f'(x) for f(x) = {expr}"
            hint = "Recall the Generalized Power Rule: d/dx[u^n] = n*u^(n-1) * u'."
        else:  # chain_log
            a = randint_nonzero(rng, 2, 4)
            b = randint_nonzero(rng, 1, 5)
            expr = sp.log(a * x + b)
            ans = sp.diff(expr, x)
            prompt = f"Differentiate the composite function: f(x) = {expr}"
            hint = "Recall the Logarithmic Chain Rule: d/dx[ln(u)] = (1/u) * u'."

    else:  # hard
        subtypes = ["composite_log", "prod_trig_exp", "quotient", "composite_exp_trig"]
        choice = _select_subtype(rng, subtypes, exclude_subtypes)
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
        elif choice == "composite_exp_trig":
            expr = sp.exp(sp.sin(x))
            ans = sp.diff(expr, x)
            prompt = f"Differentiate the composite function: f(x) = {expr}"
            hint = "Apply the Chain Rule: d/dx[exp(u)] = exp(u) * u'."
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
        subtype=choice,
    )

def _gen_integral_question(
    difficulty: str,
    rng: random.Random,
    exclude_subtypes: set[str] | list[str] | None = None,
) -> PracticeQuestion:
    x = sp.Symbol("x")
    if difficulty == "easy":
        subtypes = ["poly", "trig"]
        choice = _select_subtype(rng, subtypes, exclude_subtypes)
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
            subtype=choice,
        )

    if difficulty == "medium":
        subtypes = ["u_sub", "exp", "reciprocal", "definite"]
        choice = _select_subtype(rng, subtypes, exclude_subtypes)
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
                subtype=choice,
            )
        if choice == "exp":
            k = randint_nonzero(rng, -5, 5)
            a = randint_nonzero(rng, -3, 4)
            expr = a * sp.exp(k * x)
            ans = sp.integrate(expr, x)
            prompt = f"Evaluate: ∫ ({expr}) dx"
            hint = (
                f"Recall: ∫ a*exp(k*x) dx = a*exp(k*x)/k + C."
                if a != 1
                else f"Recall: ∫ exp(k*x) dx = exp(k*x)/k + C with k = {k}."
            )
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
                subtype=choice,
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
                subtype=choice,
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
            subtype=choice,
        )

    # hard
    subtypes = ["parts_exp", "parts_trig", "arctan_form"]
    choice = _select_subtype(rng, subtypes, exclude_subtypes)
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
        subtype=choice,
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
            a, b = rng.randint(-6, 6), rng.randint(-6, 6)
            c, d = rng.randint(-6, 6), rng.randint(-6, 6)
            trace_val = a + d
            prompt = f"Calculate the trace of matrix A = [[{a}, {b}], [{c}, {d}]]"
            hint = "The trace is the sum of diagonal elements: trace(A) = a11 + a22."
            d_str = f"({d})" if d < 0 else str(d)
            steps = [
                f"Given matrix A = [[{a}, {b}], [{c}, {d}]]",
                f"Identify diagonal entries: a11 = {a}, a22 = {d}",
                f"Calculate trace: {a} + {d_str} = {trace_val}",
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
        a = randint_nonzero(rng, -7, 7)
        d = randint_nonzero(rng, -7, 7)
        det_val = a * d
        prompt = f"Find the determinant of the diagonal matrix A = [[{a}, 0], [0, {d}]]"
        hint = "For a diagonal matrix, det is the product of diagonal elements: det = a11 * a22."
        steps = [
            f"Given diagonal matrix A = [[{a}, 0], [0, {d}]]",
            f"Compute product of diagonal entries: ({a}) * ({d}) = {det_val}",
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
        a, b = rng.randint(-5, 5), rng.randint(-5, 5)
        c, d = rng.randint(-5, 5), rng.randint(-5, 5)
        det_val = a * d - b * c
        prompt = f"Find the determinant of matrix A = [[{a}, {b}], [{c}, {d}]]"
        hint = "Use formula det(A) = a*d - b*c."
        bc_str = f"({b * c})" if b * c < 0 else str(b * c)
        steps = [
            f"Given 2x2 matrix A = [[{a}, {b}], [{c}, {d}]]",
            "Formula: det(A) = a*d - b*c",
            f"Substitute values: ({a})*({d}) - ({b})*({c}) = {a * d} - {bc_str} = {det_val}",
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
        d1, d2, d3 = rng.randint(-7, 7), rng.randint(-7, 7), rng.randint(-7, 7)
        trace_val = d1 + d2 + d3
        prompt = (
            f"Find the trace of matrix A = [[{d1}, 2, 3], [0, {d2}, 5], [1, 4, {d3}]]"
        )
        hint = "Sum the three main diagonal elements: a11 + a22 + a33."
        diag_str = " + ".join(f"({d})" if d < 0 else str(d) for d in [d1, d2, d3])
        steps = [
            "Identify the main diagonal entries: a11, a22, a33",
            f"Entries: {d1}, {d2}, {d3}",
            f"Trace = {diag_str} = {trace_val}",
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
    d1 = randint_nonzero(rng, -8, 8)
    d2 = randint_nonzero(rng, -8, 8)
    d3 = randint_nonzero(rng, -8, 8)
    det_val = d1 * d2 * d3
    prompt = f"Find the determinant of upper-triangular matrix A = [[{d1}, 3, 1], [0, {d2}, 4], [0, 0, {d3}]]"
    hint = "For any triangular matrix, determinant equals the product of its diagonal entries."
    steps = [
        "Matrix is upper triangular (all entries below diagonal are 0)",
        "Property: det(A) = product of diagonal entries",
        f"Calculate: ({d1}) * ({d2}) * ({d3}) = {det_val}",
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
    exclude_subtypes: set[str] | list[str] | None = None,
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
        return _gen_derivative_question(
            chosen_diff, rng, exclude_subtypes=exclude_subtypes
        )
    if canonical_topic == "integrals":
        return _gen_integral_question(
            chosen_diff, rng, exclude_subtypes=exclude_subtypes
        )
    if canonical_topic == "algebra":
        return _gen_algebra_question(chosen_diff, rng)
    if canonical_topic == "matrix":
        return _gen_matrix_question(chosen_diff, rng)
    if canonical_topic == "stats":
        return _gen_stats_question(chosen_diff, rng)

    return _gen_derivative_question(chosen_diff, rng, exclude_subtypes=exclude_subtypes)
