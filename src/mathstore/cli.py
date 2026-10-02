import argparse
import random
import sys

from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.core.matrix import MatrixAnalyzer
from mathstore.ode.solver import ODESolver
from mathstore.reference import get_reference, list_topics_formatted
from mathstore.statistics.analyzer import StatsAnalyzer


def main():
    parser = argparse.ArgumentParser(
        prog="mathstore",
        description="MathStore CLI: A clean, modular mathematical toolkit for university study and revision",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve", help="Solve an algebraic equation")
    solve_parser.add_argument(
        "equation", type=str, help="Equation to solve (e.g., 2*x + 4 = 10)"
    )
    solve_parser.add_argument(
        "--var", type=str, default="x", help="Variable to isolate (default: x)"
    )
    solve_parser.add_argument(
        "--latex", action="store_true", help="Output solution in LaTeX format"
    )
    solve_parser.add_argument(
        "--pretty", action="store_true", help="Output solution in pretty Unicode format"
    )
    solve_parser.add_argument(
        "--steps", action="store_true", help="Output step-by-step solution breakdown"
    )

    diff_parser = subparsers.add_parser(
        "diff", help="Differentiate a mathematical expression"
    )
    diff_parser.add_argument(
        "expression", type=str, help="Expression to differentiate (e.g., sin(x)*x)"
    )
    diff_parser.add_argument(
        "--var",
        type=str,
        default="x",
        help="Variable to differentiate against (default: x)",
    )
    diff_parser.add_argument(
        "--order", type=int, default=1, help="Derivative order (default: 1)"
    )
    diff_parser.add_argument(
        "--latex", action="store_true", help="Output derivative in LaTeX format"
    )
    diff_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Output derivative in pretty Unicode format",
    )
    diff_parser.add_argument(
        "--steps",
        action="store_true",
        help="Output step-by-step differentiation breakdown",
    )

    int_parser = subparsers.add_parser(
        "integrate", help="Find the integral of an expression."
    )
    int_parser.add_argument("expression", type=str, help="Expression to integrate.")
    int_parser.add_argument(
        "--var", type=str, default="x", help="Variable of integration (default: x)"
    )
    int_parser.add_argument(
        "--limits",
        nargs=2,
        type=float,
        default=None,
        help="The upper and lower bound for a definite integral (lower, upper)",
    )
    int_parser.add_argument(
        "--latex", action="store_true", help="Output integral in LaTeX format"
    )
    int_parser.add_argument(
        "--pretty", action="store_true", help="Output integral in pretty Unicode format"
    )
    int_parser.add_argument(
        "--steps", action="store_true", help="Output step-by-step integration breakdown"
    )

    limit_parser = subparsers.add_parser(
        "limit", help="Calculate the limit of an expression"
    )
    limit_parser.add_argument(
        "expression", type=str, help="Expression to evaluate (e.g., sin(x)/x)"
    )
    limit_parser.add_argument(
        "target", type=str, help="Target value the variable approaches (e.g., 0, oo)"
    )
    limit_parser.add_argument(
        "--var",
        type=str,
        default="x",
        help="Variable for limit calculation (default: x)",
    )
    limit_parser.add_argument(
        "--latex", action="store_true", help="Output limit in LaTeX format"
    )
    limit_parser.add_argument(
        "--pretty", action="store_true", help="Output limit in pretty Unicode format"
    )

    ref_parser = subparsers.add_parser(
        "ref", help="Lookup study reference cheat sheets and formula tables"
    )
    ref_parser.add_argument(
        "topic",
        type=str,
        nargs="?",
        default=None,
        help="Reference topic (e.g., derivatives, integrals, trig, limits, series)",
    )
    ref_parser.add_argument(
        "--list", "-l", action="store_true", help="List all available reference topics"
    )
    ref_parser.add_argument(
        "--latex",
        action="store_true",
        help="Output reference cheat sheet in LaTeX format",
    )

    matrix_parser = subparsers.add_parser(
        "matrix", help="Matrix operations & linear algebra"
    )
    matrix_parser.add_argument(
        "operation",
        choices=[
            "det",
            "inv",
            "rref",
            "eigen",
            "eigenvects",
            "rank",
            "nullity",
            "trace",
            "transpose",
            "charpoly",
        ],
        help="Matrix operation to perform",
    )
    matrix_parser.add_argument(
        "matrix",
        type=str,
        help="Matrix input (e.g. '1, 2; 3, 4' or '[[1, 2], [3, 4]]')",
    )
    matrix_parser.add_argument(
        "--latex", action="store_true", help="Output matrix result in LaTeX format"
    )
    matrix_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Output matrix result in pretty Unicode format",
    )

    stats_parser = subparsers.add_parser(
        "stats", help="Descriptive statistics, distributions & hypothesis testing"
    )
    stats_sub = stats_parser.add_subparsers(dest="stats_command", required=True)

    summary_p = stats_sub.add_parser(
        "summary", help="Calculate 5-number & distribution summary"
    )
    summary_p.add_argument(
        "data", type=str, help="Dataset (e.g. '10, 12, 14, 15, 18' or '[10, 12, 14]')"
    )
    summary_p.add_argument(
        "--latex", action="store_true", help="Output in LaTeX tabular format"
    )
    summary_p.add_argument(
        "--pretty", action="store_true", help="Output in pretty Unicode format"
    )

    normal_p = stats_sub.add_parser(
        "normal", help="Normal distribution PDF, CDF, and z-score"
    )
    normal_p.add_argument("x", type=float, help="Value to evaluate")
    normal_p.add_argument(
        "--mu", type=float, default=0.0, help="Mean mu (default: 0.0)"
    )
    normal_p.add_argument(
        "--sigma",
        type=float,
        default=1.0,
        help="Standard deviation sigma (default: 1.0)",
    )

    bin_p = stats_sub.add_parser("binomial", help="Binomial distribution PMF and CDF")
    bin_p.add_argument("k", type=int, help="Number of successes")
    bin_p.add_argument("--n", type=int, required=True, help="Number of trials")
    bin_p.add_argument("--p", type=float, required=True, help="Success probability")

    pois_p = stats_sub.add_parser("poisson", help="Poisson distribution PMF and CDF")
    pois_p.add_argument("k", type=int, help="Number of occurrences")
    pois_p.add_argument(
        "--lam", type=float, required=True, help="Rate parameter lambda"
    )

    ci_p = stats_sub.add_parser("ci", help="Confidence interval for sample mean")
    ci_p.add_argument("data", type=str, help="Sample dataset")
    ci_p.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        help="Confidence level (default: 0.95)",
    )
    ci_p.add_argument("--latex", action="store_true", help="Output in LaTeX format")
    ci_p.add_argument(
        "--pretty", action="store_true", help="Output in pretty Unicode format"
    )

    ttest_p = stats_sub.add_parser("ttest", help="One-sample Student's t-test")
    ttest_p.add_argument("data", type=str, help="Sample dataset")
    ttest_p.add_argument(
        "--pop-mean", type=float, required=True, help="Null hypothesis population mean"
    )
    ttest_p.add_argument(
        "--alt",
        choices=["two-sided", "greater", "less"],
        default="two-sided",
        help="Alternative hypothesis (default: two-sided)",
    )
    ttest_p.add_argument("--latex", action="store_true", help="Output in LaTeX format")
    ttest_p.add_argument(
        "--pretty", action="store_true", help="Output in pretty Unicode format"
    )

    practice_p = subparsers.add_parser(
        "practice", help="Interactive active-recall quizzer for university revision"
    )
    practice_p.add_argument(
        "topic",
        type=str,
        nargs="?",
        default="all",
        help="Practice topic (derivatives, integrals, algebra, matrix, stats, or all)",
    )
    practice_p.add_argument(
        "--topic",
        "-t",
        dest="topic_opt",
        type=str,
        default=None,
        help="Practice topic option (alternative to positional argument)",
    )
    practice_p.add_argument(
        "--count",
        "-n",
        type=int,
        default=None,
        help="Number of questions (default: 5 for quiz, 1 for --generate)",
    )
    practice_p.add_argument(
        "--difficulty",
        "-d",
        choices=["easy", "medium", "hard", "all"],
        default="medium",
        help="Question difficulty (default: medium)",
    )
    practice_p.add_argument(
        "--generate",
        "-g",
        action="store_true",
        help="Generate questions with hints and step solutions non-interactively",
    )
    practice_p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible question generation",
    )

    ode_p = subparsers.add_parser(
        "ode", help="Solve, classify, or verify ordinary differential equations"
    )
    ode_p.add_argument(
        "equation",
        type=str,
        help='Differential equation (e.g. "y\' + 2*y = exp(x)" or "y\'\' + 4*y = 0")',
    )
    ode_p.add_argument(
        "--ics",
        type=str,
        default=None,
        help='Initial conditions (e.g. "y(0)=1, y\'(0)=2")',
    )
    ode_p.add_argument(
        "--var",
        type=str,
        default="x",
        help="Independent variable (default: x)",
    )
    ode_p.add_argument(
        "--func",
        type=str,
        default="y",
        help="Dependent variable / function name (default: y)",
    )
    ode_p.add_argument(
        "--classify",
        action="store_true",
        help="Classify the ODE instead of solving",
    )
    ode_p.add_argument(
        "--check",
        type=str,
        default=None,
        help="Verify if candidate solution satisfies the ODE",
    )
    ode_p.add_argument(
        "--hint",
        type=str,
        default="default",
        help="Optional SymPy solving hint (default: default)",
    )
    ode_p.add_argument(
        "--steps",
        action="store_true",
        help="Output step-by-step pedagogical solution explanation",
    )
    ode_p.add_argument(
        "--latex", action="store_true", help="Output solution in LaTeX format"
    )
    ode_p.add_argument(
        "--pretty", action="store_true", help="Output solution in pretty Unicode format"
    )

    args = parser.parse_args()

    try:
        fmt = (
            "latex"
            if getattr(args, "latex", False)
            else ("pretty" if getattr(args, "pretty", False) else "str")
        )

        if args.command == "solve":
            solver = EquationSolver()
            if getattr(args, "steps", False):
                steps = solver.solve_steps(args.equation, args.var)
                print(f"Step-by-step solution for {args.equation}:")
                for idx, s in enumerate(steps, 1):
                    print(f"  {idx}. {s}")
            result = solver.solve_linear(args.equation, args.var)
            if fmt == "str":
                print(f"Solution: {args.var} = {result}")
            else:
                print(solver.format_solution(result, args.var, format=fmt))

        elif args.command == "diff":
            calc = CalculusAnalyzer()
            if getattr(args, "steps", False):
                steps = calc.differentiate_steps(args.expression, args.var, args.order)
                print(f"Step-by-step differentiation of {args.expression}:")
                for idx, s in enumerate(steps, 1):
                    print(f"  {idx}. {s}")
            result = calc.differentiate(
                args.expression, args.var, args.order, format=fmt
            )
            if fmt == "str":
                print(f"Derivative (order {args.order}): {result}")
            else:
                print(result)

        elif args.command == "integrate":
            calc = CalculusAnalyzer()
            if getattr(args, "steps", False):
                steps = calc.integrate_steps(args.expression, args.var, args.limits)
                lim_text = (
                    f" definite integral from {args.limits[0]} to {args.limits[1]}"
                    if args.limits
                    else ""
                )
                print(f"Step-by-step integration of {args.expression}{lim_text}:")
                for idx, s in enumerate(steps, 1):
                    print(f"  {idx}. {s}")
            result = calc.integrate(args.expression, args.var, args.limits, format=fmt)
            if fmt == "str":
                print(f"Integral: {result}")
            else:
                print(result)

        elif args.command == "limit":
            calc = CalculusAnalyzer()
            result = calc.get_limit(args.expression, args.target, args.var, format=fmt)
            if fmt == "str":
                print(f"Limit: {result}")
            else:
                print(result)

        elif args.command == "ref":
            if args.list or not args.topic:
                print(list_topics_formatted())
            else:
                print(get_reference(args.topic, latex=args.latex))

        elif args.command == "matrix":
            mat_calc = MatrixAnalyzer()
            if args.operation == "det":
                print(mat_calc.determinant(args.matrix, format=fmt))
            elif args.operation == "inv":
                print(mat_calc.inverse(args.matrix, format=fmt))
            elif args.operation == "rref":
                print(mat_calc.rref(args.matrix, format=fmt))
            elif args.operation == "eigen":
                print(mat_calc.eigenvalues(args.matrix, format=fmt))
            elif args.operation == "eigenvects":
                print(mat_calc.eigenvectors(args.matrix, format=fmt))
            elif args.operation == "rank":
                print(f"Rank: {mat_calc.rank(args.matrix)}")
            elif args.operation == "nullity":
                print(f"Nullity: {mat_calc.nullity(args.matrix)}")
            elif args.operation == "trace":
                print(mat_calc.trace(args.matrix, format=fmt))
            elif args.operation == "transpose":
                print(mat_calc.transpose(args.matrix, format=fmt))
            elif args.operation == "charpoly":
                print(mat_calc.characteristic_polynomial(args.matrix, format=fmt))

        elif args.command == "stats":
            stats_calc = StatsAnalyzer()
            if args.stats_command == "summary":
                print(stats_calc.summary(args.data, format=fmt))
            elif args.stats_command == "normal":
                pdf = stats_calc.normal_pdf(args.x, args.mu, args.sigma)
                cdf_val = stats_calc.normal_cdf(args.x, args.mu, args.sigma)
                z = stats_calc.z_score(args.x, args.mu, args.sigma)
                print(
                    f"Normal N(μ={args.mu}, σ={args.sigma}) at x={args.x}:\n"
                    f"  z-score: {z:.4f}\n"
                    f"  PDF:     {pdf:.6f}\n"
                    f"  CDF:     {cdf_val:.6f}"
                )
            elif args.stats_command == "binomial":
                pmf = stats_calc.binomial_pmf(args.k, args.n, args.p)
                cdf_val = stats_calc.binomial_cdf(args.k, args.n, args.p)
                print(
                    f"Binomial(n={args.n}, p={args.p}) at k={args.k}:\n"
                    f"  P(X = k):  {pmf:.6f}\n"
                    f"  P(X <= k): {cdf_val:.6f}"
                )
            elif args.stats_command == "poisson":
                pmf = stats_calc.poisson_pmf(args.k, args.lam)
                cdf_val = stats_calc.poisson_cdf(args.k, args.lam)
                print(
                    f"Poisson(λ={args.lam}) at k={args.k}:\n"
                    f"  P(X = k):  {pmf:.6f}\n"
                    f"  P(X <= k): {cdf_val:.6f}"
                )
            elif args.stats_command == "ci":
                ci_res = stats_calc.confidence_interval(
                    args.data, confidence=args.confidence, format=fmt
                )
                if fmt == "str":
                    lower, upper, margin = ci_res
                    pct = int(args.confidence * 100)
                    print(
                        f"{pct}% Confidence Interval: [{lower}, {upper}] (margin: ±{margin})"
                    )
                else:
                    print(ci_res)
            elif args.stats_command == "ttest":
                print(
                    stats_calc.one_sample_t_test(
                        args.data, args.pop_mean, alternative=args.alt, format=fmt
                    )
                )

        elif args.command == "practice":
            topic = args.topic_opt if args.topic_opt else args.topic
            if args.generate:
                count = args.count if args.count is not None else 1
                from mathstore.study.practice import (
                    format_question_card,
                    generate_question,
                )

                rng = random.Random(args.seed) if args.seed is not None else None
                for i in range(1, count + 1):
                    q = generate_question(
                        topic=topic, difficulty=args.difficulty, rng=rng
                    )
                    card = format_question_card(q, index=i if count > 1 else None)
                    print(card)
                    if i < count:
                        print("-" * 40)
            else:
                count = args.count if args.count is not None else 5
                from mathstore.study.practice import PracticeSession

                session = PracticeSession(
                    topic=topic,
                    count=count,
                    difficulty=args.difficulty,
                    seed=args.seed,
                )
                session.run()

        elif args.command == "ode":
            ode_solver = ODESolver(default_var=args.var, default_func=args.func)
            if args.check:
                is_valid = ode_solver.check_solution(
                    args.equation, args.check, var=args.var, func=args.func
                )
                if is_valid:
                    print(
                        f"Verified: '{args.check}' is a valid solution to '{args.equation}'."
                    )
                else:
                    print(
                        f"Verification failed: '{args.check}' does not satisfy '{args.equation}'."
                    )
            elif args.classify:
                info = ode_solver.classify(args.equation, var=args.var, func=args.func)
                print(f"ODE Classification for '{args.equation}':")
                print(f"  Order:        {info['order']}")
                print(f"  Linear:       {info['is_linear']}")
                print(f"  Homogeneous:  {info['is_homogeneous']}")
                print(f"  Primary Type: {info['primary_type']}")
                if info["hints"]:
                    print(f"  Solver Hints: {', '.join(info['hints'][:5])}")
            elif getattr(args, "steps", False):
                steps = ode_solver.get_steps(
                    args.equation, var=args.var, func=args.func
                )
                for step in steps:
                    print(step)
            else:
                sol = ode_solver.solve(
                    args.equation,
                    ics=args.ics,
                    var=args.var,
                    func=args.func,
                    hint=args.hint,
                    format=fmt,
                )
                if fmt == "str":
                    print(f"Solution: {sol}")
                else:
                    print(sol)

    except Exception as e:  # noqa: BLE001
        print(f"Error executing '{args.command}' : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
