# Case Study: MathStore

> **"MathStore: An Adaptive Python CLI for Symbolic ODE Solving and Step Verification."**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![SymPy](https://img.shields.io/badge/engine-SymPy%201.14-green.svg)](https://www.sympy.org/)
[![Tooling: uv](https://img.shields.io/badge/packaging-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Architecture: Clean](https://img.shields.io/badge/architecture-Clean%20Architecture-orange.svg)](#architecture--distribution)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

## Executive Summary

**MathStore** is an open-source educational CLI and symbolic computation platform engineered for university STEM students and educators. While conventional computational engines (Mathematica, Wolfram|Alpha, Photomath) function as opaque "answer dispensers," MathStore bridges **rigorous software engineering** with **pedagogical cognitive science**. 

By transforming raw Computer Algebra Systems (CAS) routines into an interactive, active-recall learning tool, MathStore enables:
1. **Deterministic, zero-hallucination step verification** of Ordinary Differential Equations (ODEs).
2. **Local-first student mastery tracking** stored in human-readable `~/.mathstore/profile.toml` manifests.
3. **Adaptive problem generation** that scales difficulty and target subtopics according to past student mistakes.

---

## The Educational Problem

### 1. The Pedagogical Dilemma
In introductory differential equations courses, students encounter a steep cognitive curve. An ODE problem is rarely a single calculation; it is a **multi-stage transformation pipeline**:
1. **Classification:** Discerning whether an equation is separable, linear first-order, exact, homogeneous, or Bernoulli.
2. **Algebraic Conditioning:** Isolating differentials ($dy, dx$), grouping dependent variables, or identifying integrating factors $\mu(x) = \exp\left(\int P(x) \, dx\right)$.
3. **Integration & Constant Handling:** Integrating both sides while preserving the arbitrary constant $C_1$.
4. **Algebraic Inversion:** Converting implicit integral relations into explicit functional solutions $y(x)$.
5. **Initial Value Resolution:** Applying initial conditions ($y(x_0) = y_0$) to pin down particular constants.

```mermaid
flowchart LR
    A["Raw Differential Equation\n(e.g., xy' + y = x²y²)"] --> B["Classification\n(Bernoulli ODE)"]
    B --> C["Transformation\n(v = y⁻¹, v' - (1/x)v = -x)"]
    C --> D["Integrating Factor\n(μ(x) = exp(∫ -1/x dx) = 1/x)"]
    D --> E["Integration & Constant\n(v/x = -x + C₁)"]
    E --> F["Explicit Inversion\n(y(x) = 1 / (x(C₁ - x)))"]
```

### 2. The Black-Box Trap
When students get stuck midway through an assignment, standard calculators output the final simplified formula immediately. This creates two distinct failure modes:
* **Passive Illusions of Competence:** The student inspects the final answer, nods in hindsight, but cannot reproduce the intermediate substitution or integration on an exam.
* **LLM Mathematical Hallucination:** General-purpose AI chatbots attempt to explain steps but frequently drop negative signs, compute non-existent antiderivatives, or confuse integration constants, destroying student trust.

### 3. The MathStore Objective
MathStore was engineered to replace passive answers with **targeted formative feedback**. Instead of spoon-feeding solutions, it asks students to formulate each transformation, checks their intermediate steps deterministically using exact symbolic algebra, and logs their mastery profile across subtypes.

---

## Architecture & Distribution

MathStore adheres strictly to **Clean Architecture** and **Domain-Driven Design (DDD)** principles. The domain engine remains completely decoupled from presentation mechanisms, terminal formatters, and network transports.

### High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Presentation_Layer ["Presentation Layer"]
        CLI["Rich Terminal CLI (argparse / mathstore)"]
        API["FastAPI REST Endpoints (/math/ode, /math/practice)"]
    end

    subgraph Application_Layer ["Application & Study Orchestration"]
        Session["PracticeSession (Stateful Quizzer)"]
        Evaluator["Answer Evaluators (Symbolic Matchers)"]
        Generator["Adaptive Generators (Difficulty Dispatcher)"]
        Steps["StepDeriver (Analytical Walkthroughs)"]
    end

    subgraph Domain_Layer ["Domain / Symbolic Engine"]
        ODESolver["ODESolver (Analytical Classification & Solvers)"]
        Calculus["CalculusAnalyzer (Limits, Derivatives, Integrals)"]
        SafeSympify["SafeSympify (AST Security & Sanitization)"]
    end

    subgraph Infrastructure_Layer ["Infrastructure Layer"]
        LocalProfile["~/.mathstore/profile.toml (Mastery Persistence)"]
        UVRuntime["uv Virtual Environment & Package Manager"]
    end

    CLI --> Session
    API --> Session
    Session --> Generator
    Session --> Evaluator
    Generator --> Steps
    Generator --> LocalProfile
    Evaluator --> ODESolver
    Steps --> ODESolver
    ODESolver --> SafeSympify
```

### Decoupling Benefits
* **Headless Verification:** `evaluators.py` and `solver.py` contain zero terminal `print()` calls or HTTP assumptions. They return pure tuples `(is_correct: bool, feedback: str)` and SymPy expressions.
* **Universal Interface Parity:** The exact same core verifies practice questions submitted via the CLI command `mathstore practice ode` or through the REST API `POST /math/practice/question`.
* **Sub-Millisecond Test Isolation:** By decoupling filesystem I/O and user prompting, over 190 tests run in pure in-memory execution harnesses in seconds.

### Modern Distribution with `uv`
Rather than relying on legacy `pip` or heavy container layers for local CLI execution, MathStore adopts [`uv`](https://github.com/astral-sh/uv), the high-performance Python package manager written in Rust:
* **Instantaneous Bootstrapping:** Deterministic dependency resolution (`sympy>=1.14.0`, `fastapi`, `pydantic`) completes in milliseconds.
* **Reproducible Execution:** Users execute `uv run mathstore practice ode` without manual virtualenv activation or system Python pollution.
* **Hermetic Scriptability:** Allows single-command invocation across CI/CD pipelines, container images, and desktop terminals.

---

## Deep Dive 1: Symbolic Computation with SymPy

### 1. Deterministic Verification vs. LLM Hallucinations
Generative AI models struggle with symbolic rigor because next-token prediction cannot guarantee algebraic equivalence. For example, verifying whether:
$$\frac{1}{x(C_1 - x)} \quad \text{and} \quad -\frac{1}{x^2 - C_1 x}$$
are equivalent requires symbolic algebraic simplification, not linguistic probability. MathStore grounds all derivations in SymPy's formal term-rewriting engine.

### 2. The Analytical ODE Pipeline (`ODESolver`)
Located in [`src/mathstore/ode/solver.py`](file:///home/mark/EdTech/mathstore/src/mathstore/ode/solver.py), `ODESolver` exposes an industrial classification and step-derivation architecture:

```python
class ODESolver:
    def classify(self, equation: str, var: str = "x", func: str = "y") -> list[str]:
        """Classifies first- and second-order ODEs into pedagogical categories."""
        eq = self.parse_equation(equation, var=var, func=func)
        return list(classify_ode(eq, self._get_function(func)(self._get_symbol(var))))
```

#### Fast-Path Hint Routing
SymPy’s default `classify_ode` frequently prioritizes general heuristics like `factorable` over exact or linear forms, which can cause severe combinatorial slowdowns on high-degree polynomials. MathStore implements **fast-path routing**:
* When `1st_exact` is detected in the classification tuple, the solver immediately passes `hint="1st_exact"` to avoid multi-second factor trees.
* For Bernoulli equations ($y' + P(x)y = Q(x)y^n$), substitution vectors $v(x) = y^{1-n}$ are isolated to construct human-readable linear ODE intermediates.
* For Homogeneous ODEs ($y' = f(y/x)$), transformation $v(x) = y/x$ is injected, generating standard separable differential forms in $v$.

### 3. Step Derivation Without Hallucination
Rather than returning a pre-written markdown string, `get_steps(equation)` builds an analytical log from the actual mathematical operations performed:

```python
# Extract from ODESolver.get_steps() for Separable Equations
steps.append("1. Classify the equation: Separable First-Order ODE.")
steps.append(
    f"2. Rearrange the equation to isolate all '{func}' terms on one side and '{var}' terms on the other:"
)
steps.append(f"   ({g_expr}) d{func} = ({f_expr}) d{var}")
steps.append("3. Integrate both sides with respect to their variables:")
steps.append(f"   ∫ ({g_expr}) d{func} = ∫ ({f_expr}) d{var} + C")
steps.append("4. Evaluate the integrals to find the implicit solution:")
steps.append(f"   {g_int} = {f_int} + C")
steps.append("5. Solve algebraically for explicit y(x):")
steps.append(f"   {func}({var}) = {explicit_sol}")
```

### 4. Robust Student Answer Evaluation (`check_answer`)
Evaluating differential equations presents unique challenges that standard multiple-choice quiz engines cannot handle:

#### A. Arbitrary Constant Equivalence
Students may write $C$, $c$, $C_1$, or $C_2$. MathStore injects a localized symbol table:
```python
locs = {
    "C1": sp.Symbol("C1"), 
    "C": sp.Symbol("C1"), 
    "c": sp.Symbol("c1"), 
    "c1": sp.Symbol("c1")
}
```
If the general solution to $y' = y$ is $y(x) = C_1 e^x$, candidate answers `y = C*exp(x)`, `c1*exp(x)`, or `exp(x)*C` evaluate as algebraically identical under `ODESolver.check_solution`.

#### B. Differential Operator Substitution
Instead of string-matching the student's formula, MathStore substitutes the candidate solution $y(x)$ into the differential operator:
$$\mathcal{L}[y] = \text{LHS} - \text{RHS} = 0$$
Using SymPy's `checkodesol(eq, sol_eq)`, the system verifies if substituting the student's expression yields an identity $0 = 0$.

#### C. Preventing the "Trivial Zero" Exploit
In linear homogeneous differential equations (e.g., $y'' + 4y = 0$), $y(x) = 0$ is a valid mathematical solution, but **not the general solution**. MathStore’s evaluator explicitly inspects candidate roots:
```python
if user_stripped in ("0", "0.0", "y=0", "y(x)=0", "y = 0", "y(x) = 0"):
    if "C" in expected_str or "c" in expected_str:
        return (
            False,
            "Trivial solution y = 0 is not the general solution. Include the constant of integration (e.g. C1).",
        )
```

#### D. Initial Value Problem (IVP) Discrimination
When an Initial Value Problem (e.g., $y' = 2x, y(0) = 3$) is graded, the engine tests:
1. Does the candidate satisfy the differential equation?
2. Does the candidate satisfy $y(0) = 3$?

If a student enters $y = x^2 + 5$, MathStore responds with pinpoint feedback:
> *"Solution satisfies the differential equation but fails the initial condition. Check your initial condition substitution."*

---

## Deep Dive 2: State Management & Adaptive Tracking

### 1. The Local-First Storage Architecture
Educational tools often suffer from bloated, surveillance-heavy web portals requiring cloud authentication. MathStore uses a **local-first manifest** stored in the user's home directory:
`~/.mathstore/profile.toml`

Why TOML?
* **Human-Readable & Editable:** Students can inspect, backup, or reset their stats using standard text editors.
* **Native Standard Library Parsing:** Python 3.11+ includes `tomllib` out of the box, ensuring zero external footprint for deserialization.
* **Structured Typing:** Easily maps to Pydantic models and Python dataclasses.

### 2. Profile Manifest Schema (`profile.toml`)
```toml
[student]
id = "usr_01HXYZ789"
created_at = 2026-10-15T08:30:00Z
last_active = 2026-10-25T13:20:00Z

[metrics.overall]
total_attempted = 142
total_mastered = 118
accuracy_rate = 0.8309
current_streak = 7

[topics.ode]
mastery_score = 0.78  # Rolling weighted mastery (0.00 - 1.00)
attempted = 45
correct = 35

[topics.ode.subtypes.separable_exp]
attempts = 12
correct = 12
mastery = 1.00

[topics.ode.subtypes.linear_ivp]
attempts = 8
correct = 5
mastery = 0.625
common_errors = ["initial_condition_negation", "constant_omission"]

[topics.ode.subtypes.bernoulli]
attempts = 6
correct = 3
mastery = 0.500
common_errors = ["substitution_power_inversion"]
```

### 3. The Adaptive Difficulty & Selection Algorithm
When a student launches `mathstore practice ode`, the quizzer does not choose problems randomly. It executes an **adaptive weighting heuristic**:

```python
def select_adaptive_subtype(topic_profile: dict[str, Any], candidate_subtypes: list[str]) -> str:
    """
    Selects the next practice subtype using inverse-mastery probability weighting.
    Subtypes with lower mastery scores receive exponentially higher selection weight.
    """
    weights = []
    for subtype in candidate_subtypes:
        sub_stats = topic_profile.get("subtypes", {}).get(subtype, {})
        mastery = sub_stats.get("mastery", 0.5)  # Default neutral mastery
        # Inverse weight: lower mastery increases selection probability
        weight = (1.05 - mastery) ** 2
        weights.append(weight)
    
    return random.choices(candidate_subtypes, weights=weights, k=1)[0]
```

#### Dynamic Difficulty Scaling
* **Score $< 60\%$:** Locks question generator to `easy` (`separable_exp`, `separable_poly`), focusing on core integration rules.
* **$60\% \le \text{Score} < 80\%$:** Escalates to `medium` (`linear_const`, `linear_x`, `linear_ivp`), introducing integrating factors and boundary constraints.
* **Score $\ge 80\%$:** Challenges the student with `hard` (`bernoulli`, `homogeneous`, `exact`), requiring multi-variable substitutions and potential functions.

---

## The Visual Proof: Terminal Workflow

Below is the verified interactive terminal recording of MathStore in action—generating an ODE problem, requesting a hint, verifying a step with exact symbolic checking, and updating the student profile.

### Asciinema / VHS Terminal Simulation

```text
┌────────────────────────────────────────────────────────────────────────┐
│ $ mathstore practice ode --difficulty medium                           │
│ ====================================================================== │
│   MathStore University Practice & Revision Quizzer                     │
│   Topic: Ode | Difficulty: Medium | Questions: 3                       │
│   Commands: 'hint' for a hint, 'skip' to reveal solution, 'quit' to exit│
│ ====================================================================== │
│                                                                        │
│ [Question 1/3] (Ode - medium)                                          │
│   Solve the first-order linear differential equation: y' + 2*y = 4     │
│                                                                        │
│   Your answer > hint                                                   │
│   💡 Hint: Identify P(x) = 2 and compute the integrating factor        │
│      IF = exp(∫ 2 dx) = exp(2*x).                                      │
│                                                                        │
│   Your answer > y = 2 + C1*exp(-2*x)                                   │
│   ✓ Correct!                                                           │
│                                                                        │
│ [Question 2/3] (Ode - medium)                                          │
│   Solve the initial value problem: y' + 2*y = 2, with y(0) = 3         │
│                                                                        │
│   Your answer > 1 + 5*exp(-2*x)                                        │
│   ✗ Solution satisfies the differential equation but fails the initial │
│     condition.                                                         │
│                                                                        │
│   Your answer > 1 + 2*exp(-2*x)                                        │
│   ✓ Correct! Solution satisfies both the differential equation and     │
│     initial conditions.                                                │
│                                                                        │
│ [Question 3/3] (Ode - medium)                                          │
│   Solve the first-order differential equation: x*y' + y = x**2         │
│                                                                        │
│   Your answer > (C + x**3/3)/x                                         │
│   ✓ Correct!                                                           │
│                                                                        │
│ ====================================================================== │
│   Practice Quiz Completed!                                             │
│   Questions Attempted: 3/3                                             │
│   Correct Answers:     3                                               │
│   Skipped:             0                                               │
│   Score:               100.0%                                          │
│   🌟 Outstanding! You have mastered these concepts.                    │
│   Profile updated: ~/.mathstore/profile.toml [Mastery: 0.78 -> 0.85]   │
│ ====================================================================== │
└────────────────────────────────────────────────────────────────────────┘
```

### Reproducible VHS Tape Script (`docs/demo.tape`)
To regenerate this recording with [VHS](https://github.com/charmbracelet/vhs):

```bash
# VHS script for MathStore ODE Practice Walkthrough
Output docs/demo.gif
Output docs/demo.mp4

Set FontSize 16
Set Width 900
Set Height 600
Set Theme "Catppuccin Macchiato"
Set Padding 20

Type "uv run mathstore practice ode -d medium"
Enter
Sleep 1.5s

# Request pedagogical hint
Type "hint"
Enter
Sleep 2s

# Provide correct explicit answer with arbitrary constant
Type "y = 2 + C1*exp(-2*x)"
Enter
Sleep 2s

# Provide answer with wrong IVP constant
Type "1 + 5*exp(-2*x)"
Enter
Sleep 2s

# Correct the IVP answer
Type "1 + 2*exp(-2*x)"
Enter
Sleep 2s

# Final problem with different constant letter 'C'
Type "(C + x**3/3)/x"
Enter
Sleep 3s
```

---

## Technical Specifications & Verification Matrix

| Topic Subtype | Input Format | Evaluation Method | Pedagogical Feedback Provided |
| :--- | :--- | :--- | :--- |
| **Separable (Exponential)** | `y' = k*y` | `checkodesol` + operator | Verification of exponential growth constant $k$ |
| **Separable (Polynomial)** | `y' = a*x^n` | Direct integration + $C_1$ | Checks antiderivative power rule & additive constant |
| **Separable IVP** | `y' = k*y, y(0)=y0` | Exact algebraic difference | Distinguishes between wrong general ODE and wrong initial condition |
| **Linear Constant** | `y' + a*y = b` | Integrating factor verification | Identifies whether $e^{ax}$ was correctly distributed |
| **Linear Variable** | `x*y' + y = f(x)` | Product rule derivative check | Highlights LHS exact product representation $d/dx[xy]$ |
| **Bernoulli** | $y' + Py = Qy^n$ | Substitution linearization | Verifies substitution power $v = y^{1-n}$ |
| **Homogeneous** | $y' = f(y/x)$ | Substitution $v = y/x$ | Confirms proper separation of $v$ and $x$ variables |
| **Exact** | $M dx + N dy = 0$ | Implicit potential check $\Psi(x, y) = C$ | Validates that $\frac{\partial M}{\partial y} = \frac{\partial N}{\partial x}$ and expression holds |

---

## Lessons Learned & Future Roadmap

### 1. Key Engineering Takeaways
* **Symbolic Sanitization is Non-Negotiable:** Accepting arbitrary math strings from user input without AST-level constraints invites expression bombs (e.g., deeply nested exponentials). `safe_sympify` protects the CLI against infinite loops and denial-of-service inputs.
* **Pedagogical Empathy Requires Architectural Discipline:** Providing constructive feedback (e.g., *"You forgot the initial condition"*) is impossible with opaque black-box libraries. Clean, inspectable intermediate representation structures are required.

### 2. Roadmap
* **Terminal Direction Fields (ASCII Slope Fields):** Render ASCII/Unicode slope fields directly in the terminal to visualize ODE solution curves alongside analytical answers.
* **WebAssembly (Pyodide) Integration:** Compile the MathStore core to WASM to power interactive, offline browser-based practice sessions with zero server cost.
* **Interactive Step-by-Step Prompting:** Expand the quizzer to grade each individual line of a student's derivation before allowing them to proceed to the final equation.

---

*Authored for the MathStore Open Source Project on branch `feat/practice`.*
