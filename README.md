# MathStore 🎓

[![Tests](https://img.shields.io/badge/tests-193%20passed-success)](https://github.com/mark/mathstore)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](https://github.com/mark/mathstore)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**MathStore** is a clean, modular mathematical toolkit and interactive CLI designed for university students, educators, and STEM practitioners. It covers **symbolic calculus**, **step-by-step derivations**, **linear algebra**, **probability & statistics**, **formula cheat sheets**, and an **active-recall practice quizzer**.

---

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
  - [Step-by-Step Derivations (`--steps`)](#1-step-by-step-derivations---steps)
  - [Active-Recall Practice Quizzer (`mathstore practice`)](#2-active-recall-practice-quizzer-mathstore-practice)
  - [Calculus & Limits (`diff`, `integrate`, `limit`)](#3-calculus--limits-diff-integrate-limit)
  - [Linear Algebra (`matrix`)](#4-linear-algebra-matrix)
  - [Statistics & Hypothesis Testing (`stats`)](#5-statistics--hypothesis-testing-stats)
  - [Formula Reference Cheat Sheets (`ref`)](#6-formula-reference-cheat-sheets-ref)
  - [Formatting: LaTeX & Unicode (`--latex`, `--pretty`)](#7-formatting-latex--unicode---latex---pretty)
- [Python Library Usage](#python-library-usage)
  - [Calculus & Derivations](#calculus--derivations)
  - [Equation Solving](#equation-solving)
  - [Matrix Analysis](#matrix-analysis)
  - [Statistics & Inference](#statistics--inference)
  - [Practice & Revision API](#practice--revision-api)
- [Project Architecture](#project-architecture)
- [Development & Testing](#development--testing)

---

## Installation & Setup

### Prerequisites
- Python 3.12 or newer
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Install with `uv`
```bash
# Clone the repository
git clone https://github.com/mark/mathstore.git
cd mathstore

# Sync virtual environment and dependencies
uv sync

# Run the CLI directly
uv run mathstore --help
```

### Install with `pip`
```bash
pip install -e .
mathstore --help
```

---

## Command-Line Interface (CLI)

### 1. Step-by-Step Derivations (`--steps`)

Add the `--steps` flag to `diff`, `integrate`, or `solve` to view full human-readable derivation trees explaining each mathematical rule applied.

```bash
# Step-by-step differentiation (Sum, Product, Quotient, Chain & Power rules)
mathstore diff "x**2 * sin(x)" --steps

# Multi-order differentiation breakdown
mathstore diff "x**3" --order 2 --steps

# Step-by-step integration (Substitution, Parts, Power, Trig forms)
mathstore integrate "x * exp(x)" --steps

# Definite integration with Fundamental Theorem of Calculus (FTC) evaluation
mathstore integrate "x**2" --limits 0 2 --steps

# Step-by-step linear and quadratic equation solving
mathstore solve "2*x + 4 = 10" --steps
mathstore solve "x**2 - 5*x + 6 = 0" --steps
```

**Example output for `mathstore diff "x**2 * sin(x)" --steps`:**
```text
Step-by-step differentiation of x**2 * sin(x):
  1. Apply Product Rule to (x**2*sin(x)): (u*v)' = u'*v + u*v' with u = x**2, v = sin(x)
  2.   Differentiate u = x**2: Apply Power Rule: d/dx[x^2] = 2*x^1 = 2*x
  3.   Differentiate v = sin(x): Standard derivative of sin(x): cos(x)
  4. Substitute into product formula: (2*x)*(sin(x)) + (x**2)*(cos(x)) = x*(x*cos(x) + 2*sin(x))
Derivative (order 1): x**2*cos(x) + 2*x*sin(x)
```

---

### 2. Active-Recall Practice Quizzer (`mathstore practice`)

Interactive quizzer designed for exam preparation and active revision with randomized problems, hints, symbolic equivalence verification, and step-by-step solution reveals.

- **Topics**: `derivatives` (alias: `calc`, `diff`), `integrals` (alias: `int`), `algebra` (alias: `solve`), `matrix` (alias: `linalg`), `stats`, or `all`
- **Difficulties**: `easy`, `medium`, `hard`
- **Smart Equivalence**: Accepts standard math inputs (`^` or `**`, `+ C`, arbitrary constants, permuted products, multi-root sets e.g. `2, 3` or `[2, 3]`).

#### Interactive Mode
```bash
# Launch interactive 5-question session across all topics
mathstore practice

# Target specific subject and difficulty
mathstore practice derivatives --difficulty medium
mathstore practice matrix --difficulty hard -n 3
```

During an interactive quiz:
- Type your mathematical answer (e.g. `6*x**2`, `x^2/2 + C`, `2, 3`)
- Type `hint` for a formula clue
- Type `skip` to reveal the answer and step-by-step derivation
- Type `quit` to exit early with score summary

#### Non-Interactive Generation (`--generate` / `-g`)
Generate practice question cards with hints, answers, and solutions for problem sets or worksheets:
```bash
# Generate 3 practice problems with full solutions
mathstore practice --generate --topic algebra -n 3 --seed 42
```

---

### 3. Calculus & Limits (`diff`, `integrate`, `limit`)

```bash
# Differentiate expressions
mathstore diff "sin(x) * exp(x)"
mathstore diff "x**4" --order 3 --var x

# Indefinite integration
mathstore integrate "cos(x)"

# Definite integration with bounds [a, b]
mathstore integrate "x**2" --limits 0 3

# Compute limits
mathstore limit "sin(x)/x" 0
mathstore limit "1/x" oo
```

---

### 4. Linear Algebra (`mathstore matrix`)

Perform matrix operations by passing row-separated strings (`"1, 2; 3, 4"` or `"[[1, 2], [3, 4]]"`):

| Operation | Command Example | Description |
|---|---|---|
| `det` | `mathstore matrix det "1, 2; 3, 4"` | Determinant |
| `inv` | `mathstore matrix inv "1, 2; 3, 4"` | Matrix Inverse |
| `rref` | `mathstore matrix rref "1, 2, -1; 2, 4, 3"` | Reduced Row Echelon Form |
| `eigen` | `mathstore matrix eigen "2, 0; 0, 3"` | Eigenvalues & algebraic multiplicities |
| `eigenvects` | `mathstore matrix eigenvects "2, 0; 0, 3"` | Eigenvectors & eigenspaces |
| `rank` | `mathstore matrix rank "1, 2; 2, 4"` | Matrix Rank |
| `nullity` | `mathstore matrix nullity "1, 2; 2, 4"` | Dimension of null space |
| `trace` | `mathstore matrix trace "5, 1; 2, 3"` | Sum of diagonal entries |
| `transpose` | `mathstore matrix transpose "1, 2; 3, 4"` | Matrix Transpose |
| `charpoly` | `mathstore matrix charpoly "1, 2; 3, 4"` | Characteristic polynomial $\det(\lambda I - A)$ |

---

### 5. Statistics & Hypothesis Testing (`mathstore stats`)

```bash
# Five-number summary & distribution statistics (Mean, Median, Std, IQR, Skewness, Kurtosis)
mathstore stats summary "10, 12, 14, 15, 18, 20, 22"

# Normal distribution PDF, CDF, and z-score
mathstore stats normal 1.96 --mu 0 --sigma 1

# Binomial distribution PMF: P(X = k) and CDF: P(X <= k)
mathstore stats binomial 3 --n 10 --p 0.5

# Poisson distribution PMF & CDF
mathstore stats poisson 2 --lam 3.0

# Confidence Interval for sample mean
mathstore stats ci "22, 25, 27, 24, 26, 28" --confidence 0.95

# One-sample Student's t-test (two-sided, greater, or less)
mathstore stats ttest "10.2, 9.8, 10.5, 10.1, 9.9" --pop-mean 10.0 --alt two-sided
```

---

### 6. Formula Reference Cheat Sheets (`ref`)

Lookup high-yield formula cheat sheets directly in the terminal:

```bash
# List all available reference cheat sheets
mathstore ref --list

# View specific cheat sheet
mathstore ref derivatives
mathstore ref integrals
mathstore ref trig
mathstore ref limits
mathstore ref series

# Export reference cheat sheet in LaTeX format
mathstore ref derivatives --latex
```

---

### 7. Formatting: LaTeX & Unicode (`--latex`, `--pretty`)

All analytical commands (`diff`, `integrate`, `limit`, `solve`, `matrix`, `stats`) support `--latex` and `--pretty` output flags for homework, lab reports, and LaTeX documents:

```bash
# LaTeX output for report insertion
mathstore diff "sin(x)/x" --latex
mathstore matrix inv "1, 2; 3, 4" --latex
mathstore stats summary "10, 12, 14, 15, 18" --latex

# Pretty Unicode formatting for clean terminal viewing
mathstore diff "x**3 + 2*x" --pretty
mathstore matrix rref "1, 2; 3, 4" --pretty
```

---

## Python Library Usage

MathStore is built as a modular Python library. You can import any analyzer, step generator, or quiz component directly into your scripts or Jupyter notebooks.

### Calculus & Derivations

```python
from mathstore.calculus import CalculusAnalyzer
from mathstore.study import get_derivative_steps, get_integral_steps

calc = CalculusAnalyzer()

# Basic differentiation and integration
deriv = calc.differentiate("x**2 * sin(x)", variable="x", order=1)
integral = calc.integrate("x * exp(x)", variable="x")
lim = calc.get_limit("sin(x)/x", limits=0, variable="x")

# Step-by-step differentiation breakdown
diff_steps = calc.differentiate_steps("x**2 * sin(x)", variable="x")
for step in diff_steps:
    print(step)

# Step-by-step definite integration with FTC evaluation
int_steps = calc.integrate_steps("x**2", variable="x", limits=(0, 2))
for step in int_steps:
    print(step)
```

### Equation Solving

```python
from mathstore.algebra import EquationSolver

solver = EquationSolver()

# Solve linear or quadratic equations
solutions = solver.solve_linear("x**2 - 5*x + 6 = 0", variable="x")
print("Roots:", solutions)  # [2, 3]

# Step-by-step derivation
steps = solver.solve_steps("2*x + 4 = 10", variable="x")
for step in steps:
    print(step)

# Format solution as LaTeX
latex_str = solver.format_solution(solutions, variable="x", format="latex")
print(latex_str)  # x \in \left\{ 2, 3 \right\}
```

### Matrix Analysis

```python
from mathstore.core import MatrixAnalyzer

matrix_analyzer = MatrixAnalyzer()
mat_str = "1, 2; 3, 4"

det = matrix_analyzer.determinant(mat_str)
inv = matrix_analyzer.inverse(mat_str)
rref_mat, pivots = matrix_analyzer.rref("1, 2, -1; 2, 4, 3")
eigenvalues = matrix_analyzer.eigenvalues("2, 0; 0, 3")
rank_val = matrix_analyzer.rank(mat_str)
trace_val = matrix_analyzer.trace(mat_str)

print("Det:", det)
print("Trace:", trace_val)
```

### Statistics & Inference

```python
from mathstore.statistics import StatsAnalyzer

stats = StatsAnalyzer()
data = [10.2, 11.5, 12.1, 9.8, 10.9, 11.2]

# Summary statistics dictionary
summary = stats.summary(data)
print("Mean:", summary["mean"], "Std Dev:", summary["std_dev"])

# Confidence interval
ci_lower, ci_upper, margin = stats.confidence_interval(data, confidence=0.95)
print(f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}] ± {margin:.2f}")

# Hypothesis testing (One-sample Student's t-test)
test_results = stats.one_sample_t_test(data, pop_mean=10.0, alternative="two-sided")
print(f"t-stat: {test_results['t_statistic']:.4f}, p-value: {test_results['p_value']:.4f}")
```

### Practice & Revision API

```python
from mathstore.study import (
    generate_question,
    check_answer,
    format_question_card,
    PracticeSession,
)

# Generate a randomized question with hint and steps
question = generate_question(topic="derivatives", difficulty="medium", seed=42)
print("Prompt:", question.prompt)
print("Hint:", question.hint)
print("Expected:", question.expected_answer)

# Verify a student's answer using symbolic equivalence
is_correct, feedback = check_answer("2*cos(2*x)", question)
print("Correct?", is_correct, "-", feedback)

# Format as printable problem card
print(format_question_card(question))

# Run an interactive practice session programmatically
session = PracticeSession(topic="all", count=5, difficulty="medium")
results = session.run()
print("Score:", results["percentage"], "%")
```

---

## Project Architecture

```text
mathstore/
├── pyproject.toml              # Build & dependency configuration
├── README.md                   # Documentation & usage guide
├── src/mathstore/
│   ├── __init__.py             # Public top-level exports
│   ├── cli.py                  # Argparse CLI interface
│   ├── algebra/
│   │   └── solver.py           # Linear & polynomial equation solver
│   ├── calculus/
│   │   └── analyzer.py         # Differentiation, integration, and limits
│   ├── core/
│   │   └── matrix.py           # Matrix operations, RREF, eigenvalues
│   ├── reference/
│   │   └── sheets.py           # Formula cheat sheets (derivatives, trig, etc.)
│   ├── statistics/
│   │   └── analyzer.py         # Descriptive stats, distributions, CI, t-tests
│   └── study/
│       ├── steps.py            # Step-by-step derivation generators
│       └── practice.py         # Active-recall quizzer & answer verification
└── tests/                      # Pytest test suites (193 tests, 90% coverage)
    ├── test_algebra.py
    ├── test_calculus.py
    ├── test_cli.py
    ├── test_matrix.py
    ├── test_practice.py
    ├── test_reference.py
    ├── test_statistics.py
    └── test_steps.py
```

---

## Development & Testing

Run all unit tests, coverage reports, and linter checks with `uv`:

```bash
# Run all unit tests
uv run pytest

# Run tests with terminal coverage report
uv run pytest --cov=mathstore --cov-report=term-missing

# Run code style & linting checks
uvx ruff check .

# Auto-format code
uvx ruff format .
```

---

## License

This project is licensed under the MIT License.
