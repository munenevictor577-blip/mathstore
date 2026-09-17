import argparse
import sys

from mathstore.algebra.solver import EquationSolver
from mathstore.calculus.analyzer import CalculusAnalyzer

def main():
    parser = argparse.ArgumentParser(
        prog="mathstore",
        description="MathStore CLI: A clean , modular mathematical toolkit"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve", help="Solve an algabraic equation")
    solve_parser.add_argument("equation", type=str, help="Equation to solve (e.g., 2*x + 4 = 10)")
    solve_parser.add_argument("--var", type=str, default="x", help="Variable to isolate (default: x)")

    diff_parser = subparsers.add_parser("diff", help="Differentiate a mathematical expression")
    diff_parser.add_argument("expression", type=str, help="Expression to differentiate (e.g., sin(x)*x)")
    diff_parser.add_argument("--var", type=str, default="x", help="Variable to differentiate against (default: x)")
    diff_parser.add_argument("--order", type=int, default=1, help="Derivative order (default: 1)")

    int_parser = subparsers.add_parser("integrate", help="Find the integral of an expression.")
    int_parser.add_argument("expression", type=str, help="Expression to integrate.")
    int_parser.add_argument("--var", type=str, default="x", help="variable of integration (default: X)")
    int_parser.add_argument("--limits", type=tuple, default=None, help="The upper and lower bound for a definite integral (lower, upper)")

    args = parser.parse_args()

    try:
        if args.command == "solve":
            solver = EquationSolver()
            result = solver.solve_linear(args.equation, args.var)
            print(f"Solution: {args.var} = {result}")

        elif args.command == "diff":
            calc = CalculusAnalyzer()
            result = calc.differentiate(args.expression, args.var, args.order)
            print(f"Derivative (order {args.order}): {result}")

        elif args.command == "integrate":
            calc = CalculusAnalyzer()
            result = calc.integrate(args.expression, args.var, args.limits)
            print(f"Integral: {result}")

    except Exception as e:
        print(f"Error executing '{args.command}' : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()        