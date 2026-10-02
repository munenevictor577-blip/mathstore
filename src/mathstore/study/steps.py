import sympy as sp
from sympy.integrals.manualintegrate import integral_steps

from mathstore.core.safe import safe_sympify


class DerivativeStepGenerator:
    """Generates human-readable, pedagogical step-by-step differentiation derivations."""

    def __init__(self, variable: str = "x"):
        self.var_str = variable
        self.var = sp.Symbol(variable)

    def explain(self, expr_str: str, order: int = 1) -> list[str]:
        """Explains the differentiation of an expression up to the requested order."""
        if order < 1:
            raise ValueError(f"Derivative order must be at least 1 (got {order}).")
        try:
            curr = safe_sympify(expr_str)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Could not parse expression '{expr_str}': {e}")

        all_steps = []
        for o in range(1, order + 1):
            if order > 1:
                all_steps.append(f"--- Derivative order {o} for: {curr} ---")
            steps_for_order: list[str] = []
            res = self._diff_expr(curr, steps_for_order)
            all_steps.extend(steps_for_order)
            curr = sp.simplify(res)
            if order > 1:
                all_steps.append(f"Order {o} derivative result: {curr}")
        return all_steps

    def _diff_expr(self, expr: sp.Basic, steps: list[str]) -> sp.Basic:
        if not expr.has(self.var):
            steps.append(f"Derivative of constant {expr} is 0")
            return sp.Integer(0)

        if expr == self.var:
            steps.append(
                f"Derivative of variable {self.var} with respect to {self.var} is 1"
            )
            return sp.Integer(1)

        if expr.is_Add:
            steps.append(
                f"Apply Sum Rule to ({expr}): differentiate each term individually"
            )
            term_diffs = []
            for arg in expr.args:
                sub_steps: list[str] = []
                d = self._diff_expr(arg, sub_steps)
                term_diffs.append(d)
                if sub_steps:
                    steps.append(f"  • Term {arg}: " + "; ".join(sub_steps))
            res = sp.Add(*term_diffs)
            steps.append(f"Combine differentiated terms: {res}")
            return res

        if expr.is_Mul:
            coeff, rest = expr.as_coeff_Mul()
            if coeff != 1:
                steps.append(
                    f"Constant factor rule: factor out {coeff}: {coeff} * d/d{self.var}[{rest}]"
                )
                sub_steps = []
                d = self._diff_expr(rest, sub_steps)
                steps.extend(["  " + s for s in sub_steps])
                res = coeff * d
                steps.append(f"Multiply by constant factor: {res}")
                return res

            args = list(expr.args)
            u = args[0]
            v = sp.Mul(*args[1:])
            steps.append(
                f"Apply Product Rule to ({expr}): (u*v)' = u'*v + u*v' with u = {u}, v = {v}"
            )
            sub_u: list[str] = []
            sub_v: list[str] = []
            du = self._diff_expr(u, sub_u)
            dv = self._diff_expr(v, sub_v)
            if sub_u:
                steps.append(f"  Differentiate u = {u}: " + "; ".join(sub_u))
            if sub_v:
                steps.append(f"  Differentiate v = {v}: " + "; ".join(sub_v))
            res = sp.simplify(du * v + u * dv)
            steps.append(
                f"Substitute into product formula: ({du})*({v}) + ({u})*({dv}) = {res}"
            )
            return res

        if expr.is_Pow:
            base, exp = expr.as_base_exp()
            if not exp.has(self.var):
                if base == self.var:
                    res = exp * (base ** (exp - 1))
                    steps.append(
                        f"Apply Power Rule: d/d{self.var}[{self.var}^{exp}] = {exp}*{self.var}^{exp - 1} = {res}"
                    )
                    return res
                sub_b: list[str] = []
                db = self._diff_expr(base, sub_b)
                res = exp * (base ** (exp - 1)) * db
                steps.append(
                    f"Apply Power and Chain Rule to ({base})^{exp}: outer = {exp}*({base})^{exp - 1}, inner d/d{self.var}[{base}] = {db}"
                )
                steps.append(f"Result: {res}")
                return res
            if not base.has(self.var):
                sub_e: list[str] = []
                de = self._diff_expr(exp, sub_e)
                res = expr * sp.log(base) * de
                steps.append(
                    f"Apply Exponential Rule to {base}^({exp}): outer = {expr} * ln({base}), inner d/d{self.var}[{exp}] = {de}"
                )
                steps.append(f"Result: {res}")
                return res

        func_derivs = {
            "sin": (lambda u: sp.cos(u), "cos(u)"),
            "cos": (lambda u: -sp.sin(u), "-sin(u)"),
            "tan": (lambda u: sp.sec(u) ** 2, "sec(u)^2"),
            "cot": (lambda u: -(sp.csc(u) ** 2), "-csc(u)^2"),
            "sec": (lambda u: sp.sec(u) * sp.tan(u), "sec(u)*tan(u)"),
            "csc": (lambda u: -sp.csc(u) * sp.cot(u), "-csc(u)*cot(u)"),
            "exp": (lambda u: sp.exp(u), "exp(u)"),
            "log": (lambda u: 1 / u, "1/u"),
            "sinh": (lambda u: sp.cosh(u), "cosh(u)"),
            "cosh": (lambda u: sp.sinh(u), "sinh(u)"),
            "tanh": (lambda u: sp.sech(u) ** 2, "sech(u)^2"),
            "asin": (lambda u: 1 / sp.sqrt(1 - u**2), "1/sqrt(1 - u^2)"),
            "acos": (lambda u: -1 / sp.sqrt(1 - u**2), "-1/sqrt(1 - u^2)"),
            "atan": (lambda u: 1 / (1 + u**2), "1/(1 + u^2)"),
        }
        fname = expr.func.__name__
        if fname in func_derivs and len(expr.args) == 1:
            arg = expr.args[0]
            outer_fn, outer_str = func_derivs[fname]
            if arg == self.var:
                res = outer_fn(arg)
                steps.append(f"Standard derivative of {fname}({self.var}): {res}")
                return res
            sub_a: list[str] = []
            da = self._diff_expr(arg, sub_a)
            outer = outer_fn(arg)
            res = outer * da
            steps.append(
                f"Apply Chain Rule to {fname}({arg}): outer d/du[{fname}(u)] = {outer_str}, inner d/d{self.var}[{arg}] = {da}"
            )
            steps.append(f"Multiply outer and inner: ({outer}) * ({da}) = {res}")
            return res

        # Fallback to sympy diff
        res = sp.diff(expr, self.var)
        steps.append(f"Differentiate {expr} with respect to {self.var}: {res}")
        return res


def get_derivative_steps(
    expression_str: str, variable: str = "x", order: int = 1
) -> list[str]:
    """Returns a list of step-by-step explanations for differentiating an expression."""
    generator = DerivativeStepGenerator(variable=variable)
    return generator.explain(expression_str, order=order)


def format_integral_rule(rule: sp.Basic | object, depth: int = 0) -> list[str]:
    """Recursively formats a SymPy manualintegrate rule into human-readable steps."""
    steps: list[str] = []
    rule_type = type(rule).__name__

    if rule_type == "AlternativeRule":
        alternatives = getattr(rule, "alternatives", [])
        if alternatives:
            return format_integral_rule(alternatives[0], depth)
        return ["No standard elementary rule found."]

    if rule_type == "ConstantRule":
        steps.append(
            f"Integrate constant {rule.integrand}: ∫ {rule.integrand} d{rule.variable} = {rule.eval()}"
        )
    elif rule_type == "ConstantTimesRule":
        steps.append(
            f"Factor out constant factor {rule.constant}: {rule.constant} * ∫ {rule.other} d{rule.variable}"
        )
        steps.extend(format_integral_rule(rule.substep, depth + 1))
        steps.append(f"Multiply by factored constant: {rule.eval()}")
    elif rule_type == "PowerRule":
        steps.append(
            f"Apply Power Rule: ∫ {rule.variable}^{rule.exp} d{rule.variable} = {rule.eval()}"
        )
    elif rule_type == "AddRule":
        steps.append(
            f"Apply Sum Rule: ∫ ({rule.integrand}) d{rule.variable} = split into separate integrals:"
        )
        for s in getattr(rule, "substeps", []):
            for st in format_integral_rule(s, depth + 1):
                steps.append("  • " + st)
        steps.append(f"Combine all integrated terms: {rule.eval()}")
    elif rule_type == "URule":
        u_var = getattr(rule, "u_var", "_u")
        u_func = getattr(rule, "u_func", "u")
        var = getattr(rule, "variable", "x")
        du_expr = sp.diff(u_func, var)
        steps.append(
            f"Apply substitution: let u = {u_func}, then du = ({du_expr}) d{var}"
        )
        steps.append(f"Transformed integral: ∫ {rule.substep.integrand} d{u_var}")
        steps.extend(format_integral_rule(rule.substep, depth + 1))
        steps.append(f"Substitute back u = {u_func}: {rule.eval()}")
    elif rule_type == "PartsRule":
        var = getattr(rule, "variable", "x")
        du_expr = sp.diff(rule.u, var)
        v_eval = (
            rule.v_step.eval()
            if hasattr(rule.v_step, "eval")
            else sp.integrate(rule.dv, var)
        )
        steps.append("Apply Integration by Parts: ∫ u dv = u*v - ∫ v du")
        steps.append(f"  Choose u = {rule.u}, dv = {rule.dv}")
        steps.append(f"  Compute du = ({du_expr}) d{var}, v = {v_eval}")
        steps.append(
            f"  Formula gives: ({rule.u})*({v_eval}) - ∫ ({v_eval})*({du_expr}) d{var}"
        )
        steps.extend(format_integral_rule(rule.second_step, depth + 1))
        steps.append(f"Combine result from parts: {rule.eval()}")
    elif rule_type == "ExpRule":
        steps.append(
            f"Integrate exponential function {rule.integrand}: ∫ {rule.integrand} d{rule.variable} = {rule.eval()}"
        )
    elif rule_type == "SinRule":
        steps.append(
            f"Integrate sine: ∫ sin({rule.variable}) d{rule.variable} = -cos({rule.variable})"
        )
    elif rule_type == "CosRule":
        steps.append(
            f"Integrate cosine: ∫ cos({rule.variable}) d{rule.variable} = sin({rule.variable})"
        )
    elif rule_type == "Sec2Rule":
        steps.append(
            f"Integrate secant squared: ∫ sec({rule.variable})^2 d{rule.variable} = tan({rule.variable})"
        )
    elif rule_type == "Csc2Rule":
        steps.append(
            f"Integrate cosecant squared: ∫ csc({rule.variable})^2 d{rule.variable} = -cot({rule.variable})"
        )
    elif rule_type == "ReciprocalRule":
        steps.append(
            f"Integrate reciprocal: ∫ 1/{rule.variable} d{rule.variable} = ln|{rule.variable}|"
        )
    elif rule_type in ("ArctanRule", "ArcsinRule"):
        steps.append(
            f"Integrate standard form: ∫ {rule.integrand} d{rule.variable} = {rule.eval()}"
        )
    elif hasattr(rule, "substep"):
        steps.append(f"Apply {rule_type} to {getattr(rule, 'integrand', '')}")
        steps.extend(format_integral_rule(rule.substep, depth + 1))
    elif hasattr(rule, "eval"):
        steps.append(
            f"Evaluate integral of {getattr(rule, 'integrand', '')}: {rule.eval()}"
        )
    else:
        var = getattr(rule, "variable", sp.Symbol("x"))
        integrand = getattr(rule, "integrand", rule)
        res = sp.integrate(integrand, var)
        steps.append(f"Direct integration of {integrand}: {res}")

    return steps


def get_integral_steps(
    expression_str: str,
    variable: str = "x",
    limits: tuple[float, float] | None = None,
) -> list[str]:
    """Returns step-by-step breakdown of an indefinite or definite integral."""
    try:
        var = sp.Symbol(variable)
        expr = safe_sympify(expression_str)
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"Could not parse integral expression '{expression_str}': {e}")

    steps: list[str] = []
    try:
        rule = integral_steps(expr, var)
        if type(rule).__name__ == "DontKnowRule":
            res = sp.integrate(expr, var)
            steps.append(
                f"Direct integration using general integration algorithms: {res}"
            )
        else:
            steps.extend(format_integral_rule(rule))
    except Exception:  # noqa: BLE001
        res = sp.integrate(expr, var)
        steps.append(f"Evaluate antiderivative using symbolic integration: {res}")

    # Calculate antiderivative
    antideriv = sp.integrate(expr, var)

    if limits is not None:
        lower, upper = limits
        steps.append(
            "Apply the Fundamental Theorem of Calculus: ∫[a to b] f(x) dx = F(b) - F(a)"
        )
        fb = sp.simplify(antideriv.subs(var, upper))
        fa = sp.simplify(antideriv.subs(var, lower))
        steps.append(
            f"Evaluate antiderivative at upper limit x = {upper}: F({upper}) = {fb}"
        )
        steps.append(
            f"Evaluate antiderivative at lower limit x = {lower}: F({lower}) = {fa}"
        )
        net = sp.simplify(fb - fa)
        steps.append(
            f"Compute difference: F({upper}) - F({lower}) = ({fb}) - ({fa}) = {net}"
        )
    else:
        steps.append(f"Add arbitrary constant of integration: {antideriv} + C")

    return steps


def get_equation_steps(equation_str: str, variable: str = "x") -> list[str]:
    """Returns step-by-step breakdown of solving an algebraic equation."""
    if "=" not in equation_str:
        raise ValueError("Equation must contain '=' separating left and right sides.")

    var = sp.Symbol(variable)
    lhs_str, rhs_str = equation_str.split("=", 1)
    try:
        lhs = safe_sympify(lhs_str.strip())
        rhs = safe_sympify(rhs_str.strip())
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"Could not parse equation '{equation_str}': {e}")

    steps: list[str] = [f"Initial equation: {lhs} = {rhs}"]
    diff_expr = sp.simplify(lhs - rhs)

    if rhs != 0:
        steps.append(f"Move all terms to LHS: {lhs} - ({rhs}) = 0  =>  {diff_expr} = 0")

    try:
        poly = sp.Poly(diff_expr, var)
        deg = poly.degree()

        if deg == 1:
            a = poly.coeff_monomial(var**1)
            b = poly.coeff_monomial(var**0)
            steps.append(
                f"Identify linear equation a*{variable} + b = 0 with a = {a}, b = {b}"
            )
            if b != 0:
                steps.append(
                    f"Isolate variable term by subtracting constant: {a}*{variable} = {-b}"
                )
            if a != 1:
                steps.append(
                    f"Divide both sides by coefficient {a}: {variable} = {-b}/{a} = {-b / a}"
                )
            sol = -b / a
            steps.append(f"Solution: {variable} = {sol}")
            return steps

        if deg == 2:
            a = poly.coeff_monomial(var**2)
            b = poly.coeff_monomial(var**1)
            c = poly.coeff_monomial(var**0)
            steps.append(
                f"Standard quadratic form a*{variable}^2 + b*{variable} + c = 0 with a = {a}, b = {b}, c = {c}"
            )
            disc = b**2 - 4 * a * c
            steps.append(
                f"Calculate discriminant: Δ = b^2 - 4ac = ({b})^2 - 4*({a})*({c}) = {disc}"
            )
            if getattr(disc, "is_number", False) and disc.is_real:
                if disc > 0:
                    steps.append("Δ > 0: Equation has two distinct real roots.")
                elif disc == 0:
                    steps.append("Δ = 0: Equation has one repeated real root.")
                else:
                    steps.append("Δ < 0: Equation has two complex conjugate roots.")
            else:
                steps.append(
                    f"Sign of discriminant Δ = {disc} depends on parameter values."
                )
            steps.append(f"Apply quadratic formula: {variable} = (-b ± √Δ) / (2a)")
            sols = sp.solve(diff_expr, var)
            steps.append(f"Solutions: {variable} = {sols}")
            return steps

        if deg > 2:
            steps.append(f"Polynomial equation of degree {deg}")
            factored = sp.factor(diff_expr)
            steps.append(f"Factor polynomial: {factored} = 0")
            sols = sp.solve(diff_expr, var)
            steps.append(f"Solutions: {variable} = {sols}")
            return steps

    except (sp.PolynomialError, sp.GeneratorsNeeded, TypeError, ValueError):
        pass

    sols = sp.solve(diff_expr, var)
    steps.append(f"Isolate {variable} using algebraic methods: {diff_expr} = 0")
    steps.append(f"Solutions: {variable} = {sols}")
    return steps


def get_ode_steps(
    equation: str,
    variable: str = "x",
    function: str = "y",
) -> list[str]:
    """Generates pedagogical step-by-step explanations for solving an ordinary differential equation."""
    from mathstore.ode.solver import ODESolver

    return ODESolver(default_var=variable, default_func=function).get_steps(
        equation, var=variable, func=function
    )

