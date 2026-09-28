"""Ordinary Differential Equation (ODE) solver for university mathematics.

Provides analytical solving, classification, initial value problem (IVP) resolution,
and solution verification for first- and higher-order ODEs.
"""

from __future__ import annotations

import functools
import re
from typing import Any

import sympy as sp
from sympy.solvers.deutils import ode_order
from sympy.solvers.ode.ode import classify_ode
from sympy.solvers.ode.subscheck import checkodesol

from mathstore.core.safe import safe_sympify


@functools.lru_cache(maxsize=128)
def _compile_ode_patterns(func: str, var: str) -> tuple[re.Pattern, ...]:
    """Precompile regex patterns for a given function and variable name."""
    f_esc = re.escape(func)
    v_esc = re.escape(var)

    # Leibniz notation: d2y/dx2, d^2y/dx^2, dy/dx, d^3y/dx^3
    p_leibniz = re.compile(rf"\bd\^?(\d+)?{f_esc}/d\^?(\d+)?{v_esc}\^?(\d+)?\b")

    # Prime notation: y'''', y''', y'', y'
    p_primes_4plus = re.compile(rf"\b{f_esc}\'{{4,}}")
    p_primes_3 = re.compile(rf"\b{f_esc}\'\'\'")
    p_primes_2 = re.compile(rf"\b{f_esc}\'\'")
    p_primes_1 = re.compile(rf"\b{f_esc}\'")

    # Bare function token not followed by (
    p_bare_func = re.compile(rf"\b{f_esc}\b(?!\s*\()")

    # Initial condition pattern: y(0), y'(0), dy/dx(0)
    p_ics = re.compile(
        rf"^(?:{f_esc}(\'*)|d\^?(\d+)?{f_esc}/d\^?(\d+)?{v_esc}\^?(\d+)?)\s*\((.*?)\)$"
    )

    return (p_leibniz, p_primes_4plus, p_primes_3, p_primes_2, p_primes_1, p_bare_func, p_ics)


class ODESolver:
    """
    High-performance analytical ODE solver and classifier for STEM education.
    
    Supports:
      - 1st-order ODEs: separable, linear integrating factors, exact, Bernoulli, homogeneous.
      - Higher-order linear ODEs: constant coefficients, undetermined coefficients, variation of parameters.
      - Initial Value Problems (IVPs) via versatile initial conditions parsing.
      - Natural mathematical syntax (y', y'', dy/dx, bare y).
      - Rigorous solution verification against original differential equations.
    """

    def __init__(self, default_var: str = "x", default_func: str = "y") -> None:
        self.default_var = default_var
        self.default_func = default_func
        # Cached standard symbols
        self._symbol_cache: dict[str, sp.Symbol] = {}
        self._function_cache: dict[str, sp.Function] = {}

    def _get_symbol(self, name: str) -> sp.Symbol:
        """Retrieve or cache a SymPy Symbol."""
        if name not in self._symbol_cache:
            self._symbol_cache[name] = sp.Symbol(name)
        return self._symbol_cache[name]

    def _get_function(self, name: str) -> sp.Function:
        """Retrieve or cache an undefined SymPy Function."""
        if name not in self._function_cache:
            self._function_cache[name] = sp.Function(name)
        return self._function_cache[name]

    def normalize_ode_string(self, text: str, var: str = "x", func: str = "y") -> str:
        """
        Normalizes natural ODE notation into AST-parseable SymPy expressions.

        Transforms:
          - Prime notation: y' -> Derivative(y(x), x), y'' -> Derivative(y(x), x, 2)
          - Leibniz notation: dy/dx -> Derivative(y(x), x), d2y/dx2 -> Derivative(y(x), x, 2)
          - Bare function references: y -> y(x)
          - Equations without '=': appends '= 0'
        """
        p_leibniz, p_p4, p_p3, p_p2, p_p1, p_bare, _ = _compile_ode_patterns(func, var)

        s = text.strip()
        if not s:
            raise ValueError("ODE expression string cannot be empty.")

        # Normalize Leibniz derivatives
        def _replace_leibniz(m: re.Match) -> str:
            order = int(m.group(1) or m.group(2) or m.group(3) or 1)
            if order > 1:
                return f"Derivative({func}({var}), {var}, {order})"
            return f"Derivative({func}({var}), {var})"

        s = p_leibniz.sub(_replace_leibniz, s)

        # Normalize prime derivatives (highest order first)
        s = p_p4.sub(lambda m: f"Derivative({func}({var}), {var}, {len(m.group(0)) - len(func)})", s)
        s = p_p3.sub(f"Derivative({func}({var}), {var}, 3)", s)
        s = p_p2.sub(f"Derivative({func}({var}), {var}, 2)", s)
        s = p_p1.sub(f"Derivative({func}({var}), {var})", s)

        # Normalize bare function instances not followed by parentheses
        s = p_bare.sub(f"{func}({var})", s)

        if "=" not in s:
            s = f"{s} = 0"

        return s

    def parse_equation(
        self,
        equation: str | sp.Eq | sp.Expr,
        var: str = "x",
        func: str = "y",
    ) -> sp.Eq:
        """
        Parses an ODE into a validated SymPy equality object.

        Args:
            equation: String (e.g. "y' + 2*y = exp(x)"), sympy.Eq, or sympy.Expr.
            var: Independent variable name (default: "x").
            func: Dependent variable/function name (default: "y").

        Returns:
            sp.Eq representing the ODE.

        Raises:
            ValueError: If the equation contains syntax errors, multiple '=' signs,
                        or contains no derivatives (i.e. is an algebraic equation).
        """
        if isinstance(equation, sp.Eq):
            eq = equation
        elif isinstance(equation, sp.Expr):
            eq = sp.Eq(equation, 0)
        elif isinstance(equation, str):
            norm_str = self.normalize_ode_string(equation, var=var, func=func)
            parts = norm_str.split("=")
            if len(parts) != 2:
                raise ValueError("ODE must contain at most one '=' separating LHS and RHS.")

            var_sym = self._get_symbol(var)
            func_sym = self._get_function(func)
            locs = {
                var: var_sym,
                func: func_sym,
                "Derivative": sp.Derivative,
                "diff": sp.diff,
            }

            try:
                lhs = safe_sympify(parts[0].strip(), locals_dict=locs, variable=var)
                rhs = safe_sympify(parts[1].strip(), locals_dict=locs, variable=var)
                eq = sp.Eq(lhs, rhs)
            except Exception as e:
                raise ValueError(f"Failed to parse differential equation '{equation}': {e}") from e
        else:
            raise TypeError(f"Unsupported equation type: {type(equation).__name__}")

        # Validate differential order
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        ord_val = ode_order(eq, func_sym(var_sym))
        if ord_val == 0:
            raise ValueError(
                f"Equation contains no derivatives of '{func}({var})'. "
                "For algebraic equations, use EquationSolver."
            )

        return eq

    def parse_ics(
        self,
        ics_input: Any,
        var: str = "x",
        func: str = "y",
    ) -> dict[sp.Basic, sp.Basic] | None:
        """
        Parses initial conditions into the dictionary format expected by SymPy.

        Supported formats:
          - String: "y(0) = 1", "y(0)=1, y'(0)=2", "y(0)=1; y'(0)=2"
          - Dict with numeric keys: {0: 1}, {0: (1, 2)}
          - Dict with string keys: {"y(0)": 1, "y'(0)": 2}
          - Dict with SymPy expressions: {y(0): 1, y(x).diff(x).subs(x, 0): 2}

        Returns:
            dict[sp.Basic, sp.Basic] or None if ics_input is None.
        """
        if ics_input is None:
            return None

        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        res: dict[sp.Basic, sp.Basic] = {}

        if isinstance(ics_input, dict):
            for k, v in ics_input.items():
                if isinstance(k, sp.Basic):
                    v_sym = safe_sympify(v, variable=var) if not isinstance(v, sp.Basic) else v
                    res[k] = v_sym
                elif isinstance(k, (int, float)):
                    x0 = safe_sympify(k, variable=var)
                    if isinstance(v, (list, tuple)):
                        for order_idx, val in enumerate(v):
                            val_sym = (
                                safe_sympify(val, variable=var)
                                if not isinstance(val, sp.Basic)
                                else val
                            )
                            if order_idx == 0:
                                res[func_sym(x0)] = val_sym
                            else:
                                deriv = sp.Derivative(func_sym(var_sym), (var_sym, order_idx))
                                res[deriv.subs(var_sym, x0)] = val_sym
                    else:
                        val_sym = safe_sympify(v, variable=var) if not isinstance(v, sp.Basic) else v
                        res[func_sym(x0)] = val_sym
                elif isinstance(k, str):
                    eq_str = f"{k} = {v}"
                    res.update(self._parse_ics_string(eq_str, var=var, func=func))
                else:
                    raise TypeError(f"Invalid initial condition key type: {type(k).__name__}")
            return res

        if isinstance(ics_input, str):
            return self._parse_ics_string(ics_input, var=var, func=func)

        raise TypeError(f"Unsupported initial conditions type: {type(ics_input).__name__}")

    def _parse_ics_string(
        self,
        text: str,
        var: str = "x",
        func: str = "y",
    ) -> dict[sp.Basic, sp.Basic]:
        """Parses comma- or semicolon-separated initial conditions from a string."""
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        *_, p_ics = _compile_ode_patterns(func, var)

        res: dict[sp.Basic, sp.Basic] = {}
        # Split by comma or semicolon outside parentheses
        items = [it.strip() for it in re.split(r"[,;](?![^\(]*\))", text) if it.strip()]

        for item in items:
            if "=" not in item:
                raise ValueError(f"Initial condition must contain '=': '{item}'")
            left, right = item.split("=", 1)
            left = left.strip()
            val = safe_sympify(right.strip(), variable=var)

            m = p_ics.match(left)
            if not m:
                raise ValueError(
                    f"Could not parse initial condition specification: '{item}'. "
                    f"Expected format like '{func}(0) = 1' or '{func}'(0) = 2'."
                )

            primes = m.group(1)
            if primes is not None:
                order = len(primes)
            else:
                order = int(m.group(2) or m.group(3) or m.group(4) or 1)

            x0_str = m.group(5).strip()
            x0 = safe_sympify(x0_str, variable=var)

            if order == 0:
                res[func_sym(x0)] = val
            else:
                deriv = sp.Derivative(func_sym(var_sym), (var_sym, order))
                res[deriv.subs(var_sym, x0)] = val

        return res

    def order(
        self,
        equation: str | sp.Eq | sp.Expr,
        var: str = "x",
        func: str = "y",
    ) -> int:
        """Returns the differential order of the ODE."""
        eq = self.parse_equation(equation, var=var, func=func)
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        return int(ode_order(eq, func_sym(var_sym)))

    def is_linear(
        self,
        equation: str | sp.Eq | sp.Expr,
        var: str = "x",
        func: str = "y",
    ) -> bool:
        """Determines whether the ODE is linear in the dependent variable and its derivatives."""
        eq = self.parse_equation(equation, var=var, func=func)
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        f_app = func_sym(var_sym)

        expr = (eq.lhs - eq.rhs).expand()
        deps: set[sp.Basic] = set()

        for a in expr.atoms(sp.Derivative):
            if a.expr == f_app:
                deps.add(a)
        for a in expr.atoms(sp.core.function.AppliedUndef):
            if a == f_app:
                deps.add(a)

        if not deps:
            return False

        try:
            poly = expr.as_poly(*deps)
            return poly.total_degree() <= 1
        except Exception:  # noqa: BLE001
            return False

    def is_homogeneous(
        self,
        equation: str | sp.Eq | sp.Expr,
        var: str = "x",
        func: str = "y",
    ) -> bool:
        """Determines whether a linear ODE has a vanishing non-homogeneous source term."""
        eq = self.parse_equation(equation, var=var, func=func)
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        f_app = func_sym(var_sym)

        expr = (eq.lhs - eq.rhs).expand()
        subs_dict: dict[sp.Basic, int] = {}

        for a in expr.atoms(sp.Derivative):
            if a.expr == f_app:
                subs_dict[a] = 0
        for a in expr.atoms(sp.core.function.AppliedUndef):
            if a == f_app:
                subs_dict[a] = 0

        if not subs_dict:
            return False

        rem = expr.subs(subs_dict).simplify()
        return rem == 0

    def classify(
        self,
        equation: str | sp.Eq | sp.Expr,
        var: str = "x",
        func: str = "y",
    ) -> dict[str, Any]:
        """
        Classifies an ODE, returning order, linearity, homogeneity, and solution heuristics.

        Returns:
            Dictionary with keys:
              - "order": int
              - "is_linear": bool
              - "is_homogeneous": bool
              - "hints": list[str] (available SymPy solving methods)
              - "primary_type": str (human-readable type name)
        """
        eq = self.parse_equation(equation, var=var, func=func)
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        f_app = func_sym(var_sym)

        ord_val = int(ode_order(eq, f_app))
        linear_val = self.is_linear(eq, var=var, func=func)
        homog_val = self.is_homogeneous(eq, var=var, func=func) if linear_val else False

        try:
            hints = list(classify_ode(eq, f_app))
        except Exception:
            hints = []

        # Determine pedagogical primary type
        primary = "General ODE"
        hint_set = set(hints)
        if "separable" in hint_set:
            primary = "Separable First-Order ODE"
        elif "1st_linear" in hint_set:
            primary = "First-Order Linear ODE (Integrating Factor)"
        elif "Bernoulli" in hint_set:
            primary = "Bernoulli Differential Equation"
        elif "1st_exact" in hint_set or "exact" in hint_set:
            primary = "Exact First-Order ODE"
        elif "nth_linear_constant_coeff_homogeneous" in hint_set:
            primary = f"Order {ord_val} Linear Constant-Coefficient Homogeneous ODE"
        elif "nth_linear_constant_coeff_undetermined_coefficients" in hint_set:
            primary = f"Order {ord_val} Linear Constant-Coefficient Non-Homogeneous ODE (Undetermined Coefficients)"
        elif "nth_linear_constant_coeff_variation_of_parameters" in hint_set:
            primary = f"Order {ord_val} Linear Constant-Coefficient Non-Homogeneous ODE (Variation of Parameters)"
        elif "homogeneous_coeff" in hint_set:
            primary = "Homogeneous First-Order ODE"
        elif linear_val:
            primary = f"Order {ord_val} Linear Differential Equation"

        return {
            "order": ord_val,
            "is_linear": linear_val,
            "is_homogeneous": homog_val,
            "hints": hints,
            "primary_type": primary,
        }

    def solve(
        self,
        equation: str | sp.Eq | sp.Expr,
        ics: Any = None,
        var: str = "x",
        func: str = "y",
        hint: str = "default",
        simplify: bool = True,
        format: str = "str",
    ) -> str | sp.Eq | list[str] | list[sp.Eq]:
        """
        Solves an ordinary differential equation analytically.

        Args:
            equation: Differential equation string (e.g. "y' + 2*y = exp(x)"), sp.Eq, or sp.Expr.
            ics: Initial conditions (e.g. "y(0) = 1, y'(0) = 2" or {0: (1, 2)}).
            var: Independent variable name (default: "x").
            func: Dependent variable/function name (default: "y").
            hint: Specific SymPy solving hint (default: "default").
            simplify: Whether to algebraically simplify the result (default: True).
            format: Output format ('str', 'latex', 'pretty', 'sympy', or 'rhs').

        Returns:
            Formatted solution string, SymPy equality object, or list of solutions.

        Raises:
            ValueError: If equation/ics cannot be parsed or if no analytical solution is found.
        """
        eq = self.parse_equation(equation, var=var, func=func)
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        f_app = func_sym(var_sym)

        parsed_ics = self.parse_ics(ics, var=var, func=func) if ics is not None else None

        kwargs: dict[str, Any] = {
            "simplify": simplify,
        }
        if parsed_ics:
            kwargs["ics"] = parsed_ics
        if hint != "default":
            kwargs["hint"] = hint

        try:
            sol = sp.dsolve(eq, f_app, **kwargs)
        except Exception as e:
            raise ValueError(
                f"Unable to find an analytical solution for ODE '{equation}': {e}"
            ) from e

        return self.format_solution(sol, format=format)

    def check_solution(
        self,
        equation: str | sp.Eq | sp.Expr,
        solution: str | sp.Eq | sp.Expr,
        var: str = "x",
        func: str = "y",
    ) -> bool:
        """
        Rigorously checks whether a candidate solution satisfies the differential equation.

        Args:
            equation: The ODE.
            solution: Candidate solution (sp.Eq, or expression string e.g. "C1*exp(-2*x)").
            var: Independent variable name (default: "x").
            func: Dependent variable name (default: "y").

        Returns:
            True if the candidate solution satisfies the ODE, False otherwise.
        """
        eq = self.parse_equation(equation, var=var, func=func)
        var_sym = self._get_symbol(var)
        func_sym = self._get_function(func)
        f_app = func_sym(var_sym)

        if isinstance(solution, sp.Eq):
            sol_eq = solution
        elif isinstance(solution, sp.Expr):
            sol_eq = sp.Eq(f_app, solution)
        elif isinstance(solution, str):
            clean_sol = solution.strip()
            if "=" in clean_sol:
                parts = clean_sol.split("=", 1)
                lhs = safe_sympify(parts[0].strip(), locals_dict={func: func_sym, var: var_sym}, variable=var)
                rhs = safe_sympify(parts[1].strip(), locals_dict={func: func_sym, var: var_sym}, variable=var)
                sol_eq = sp.Eq(lhs, rhs)
            else:
                rhs = safe_sympify(clean_sol, locals_dict={func: func_sym, var: var_sym}, variable=var)
                sol_eq = sp.Eq(f_app, rhs)
        else:
            raise ValueError(f"Unsupported solution type: {type(solution).__name__}")

        try:
            is_valid, _ = checkodesol(eq, sol_eq)
            return bool(is_valid)
        except Exception:
            return False

    def format_solution(
        self,
        solution: sp.Eq | list[sp.Eq] | sp.Basic,
        format: str = "str",
    ) -> str | sp.Eq | list[str] | list[sp.Eq]:
        """
        Formats a SymPy ODE solution into standard string, LaTeX, or pretty Unicode.

        Args:
            solution: SymPy equality or list of equalities.
            format: Output format ('str', 'latex', 'pretty', 'sympy', 'rhs').
        """
        if format == "sympy":
            return solution

        if isinstance(solution, list):
            return [self.format_solution(s, format=format) for s in solution]  # type: ignore[return-value]

        if not isinstance(solution, sp.Eq):
            if format == "latex":
                return sp.latex(solution)
            if format == "pretty":
                return sp.pretty(solution, use_unicode=True)
            return str(solution)

        if format == "latex":
            return sp.latex(solution)
        if format == "pretty":
            return sp.pretty(solution, use_unicode=True)
        if format == "rhs":
            return str(solution.rhs)

        return f"{solution.lhs} = {solution.rhs}"
