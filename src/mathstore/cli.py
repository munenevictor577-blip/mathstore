import argparse
import sys

from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer
from mathstore.reference import get_reference, list_topics_formatted


def main():
    parser = argparse.ArgumentParser(
        prog="mathstore",
        description="MathStore CLI: A clean, modular mathematical toolkit for university study and revision"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve", help="Solve an algebraic equation")
    solve_parser.add_argument("equation", type=str, help="Equation to solve (e.g., 2*x + 4 = 10)")
    solve_parser.add_argument("--var", type=str, default="x", help="Variable to isolate (default: x)")
    solve_parser.add_argument("--latex", action="store_true", help="Output solution in LaTeX format")
    solve_parser.add_argument("--pretty", action="store_true", help="Output solution in pretty Unicode format")

    diff_parser = subparsers.add_parser("diff", help="Differentiate a mathematical expression")
    diff_parser.add_argument("expression", type=str, help="Expression to differentiate (e.g., sin(x)*x)")
    diff_parser.add_argument("--var", type=str, default="x", help="Variable to differentiate against (default: x)")
    diff_parser.add_argument("--order", type=int, default=1, help="Derivative order (default: 1)")
    diff_parser.add_argument("--latex", action="store_true", help="Output derivative in LaTeX format")
    diff_parser.add_argument("--pretty", action="store_true", help="Output derivative in pretty Unicode format")

    int_parser = subparsers.add_parser("integrate", help="Find the integral of an expression.")
    int_parser.add_argument("expression", type=str, help="Expression to integrate.")
    int_parser.add_argument("--var", type=str, default="x", help="Variable of integration (default: x)")
    int_parser.add_argument(
        "--limits",
        nargs=2,
        type=float,
        default=None,
        help="The upper and lower bound for a definite integral (lower, upper)",
    )
    int_parser.add_argument("--latex", action="store_true", help="Output integral in LaTeX format")
    int_parser.add_argument("--pretty", action="store_true", help="Output integral in pretty Unicode format")

    limit_parser = subparsers.add_parser("limit", help="Calculate the limit of an expression")
    limit_parser.add_argument("expression", type=str, help="Expression to evaluate (e.g., sin(x)/x)")
    limit_parser.add_argument("target", type=str, help="Target value the variable approaches (e.g., 0, oo)")
    limit_parser.add_argument("--var", type=str, default="x", help="Variable for limit calculation (default: x)")
    limit_parser.add_argument("--latex", action="store_true", help="Output limit in LaTeX format")
    limit_parser.add_argument("--pretty", action="store_true", help="Output limit in pretty Unicode format")

    ref_parser = subparsers.add_parser("ref", help="Lookup study reference cheat sheets and formula tables")
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
        "--latex", action="store_true", help="Output reference cheat sheet in LaTeX format"
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
            result = solver.solve_linear(args.equation, args.var)
            if fmt == "str":
                print(f"Solution: {args.var} = {result}")
            else:
                print(solver.format_solution(result, args.var, format=fmt))

        elif args.command == "diff":
            calc = CalculusAnalyzer()
            result = calc.differentiate(args.expression, args.var, args.order, format=fmt)
            if fmt == "str":
                print(f"Derivative (order {args.order}): {result}")
            else:
                print(result)

        elif args.command == "integrate":
            calc = CalculusAnalyzer()
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

    except Exception as e:  # noqa: BLE001
        print(f"Error executing '{args.command}' : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
        