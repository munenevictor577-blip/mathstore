# MathStore 🎓

**MathStore** is a clean, modular mathematical toolkit designed for university students, educators, and STEM practitioners studying calculus, linear algebra, statistics, and equation solving.

---

## Features Overview

### 1. Step-by-Step Derivations (`--steps`)
Get step-by-step mathematical reasoning and rule breakdowns for:
- **Differentiation**: Power rule, product rule, quotient rule, chain rule, and multi-order derivatives.
- **Integration**: Rule breakdown (power rule, substitution, integration by parts, trigonometric identities, standard forms) and Fundamental Theorem of Calculus evaluations for definite integrals.
- **Equation Solving**: Linear isolation steps, quadratic discriminant calculations, and formula evaluations.

```bash
# Step-by-step differentiation
mathstore diff "x**2 * sin(x)" --steps

# Step-by-step integration
mathstore integrate "x * exp(x)" --steps

# Definite integration with FTC steps
mathstore integrate "x**2" --limits 0 2 --steps

# Step-by-step equation solving
mathstore solve "2*x + 4 = 10" --steps
mathstore solve "x**2 - 5*x + 6 = 0" --steps
```

---

### 2. Active-Recall Practice Quizzer (`mathstore practice`)
Interactive test-prep and practice quizzer with hints, symbolic equivalence verification, and instant derivations upon completion or skip:
- **Topics**: `derivatives`, `integrals`, `algebra`, `matrix`, `stats`, or `all`
- **Difficulties**: `easy`, `medium`, `hard`
- **Smart Evaluation**: Accepts standard algebraic syntax (`^` or `**`, `+ C`, permuted products, multi-root sets)
- **Non-Interactive Generation**: Generate questions, hints, and step-by-step solutions for automated revision sheets.

```bash
# Start an interactive 5-question practice session
mathstore practice

# Practice a specific topic
mathstore practice derivatives
mathstore practice matrix --difficulty hard

# Generate printable/revision questions non-interactively
mathstore practice --generate --topic algebra -n 3
```

---

### 3. Calculus Toolkit
- Differentiate expressions to any order: `mathstore diff "sin(x)*exp(x)" --order 2`
- Compute indefinite and definite integrals: `mathstore integrate "sin(x)" --limits 0 3.14159`
- Evaluate limits: `mathstore limit "sin(x)/x" 0`
- Format output as text, LaTeX (`--latex`), or pretty Unicode (`--pretty`).

---

### 4. Linear Algebra (`mathstore matrix`)
- Determinants: `mathstore matrix det "1, 2; 3, 4"`
- Inverses: `mathstore matrix inv "1, 2; 3, 4"`
- Reduced Row Echelon Form (RREF): `mathstore matrix rref "1, 2, -1; 2, 4, 3"`
- Eigenvalues & Eigenvectors: `mathstore matrix eigen "2, 0; 0, 3"`
- Rank, Nullity, Trace, Transpose, and Characteristic Polynomials.

---

### 5. Statistics & Hypothesis Testing (`mathstore stats`)
- 5-number & distribution summary: `mathstore stats summary "10, 12, 14, 15, 18, 20"`
- Normal distribution PDF, CDF, and z-score: `mathstore stats normal 1.96 --mu 0 --sigma 1`
- Binomial distribution PMF & CDF: `mathstore stats binomial 3 --n 10 --p 0.5`
- Poisson distribution PMF & CDF: `mathstore stats poisson 2 --lam 3.0`
- Confidence Intervals: `mathstore stats ci "22, 25, 27, 24, 26" --confidence 0.95`
- Student's One-Sample t-test: `mathstore stats ttest "10.2, 9.8, 10.5, 10.1" --pop-mean 10.0`

---

### 6. Study Reference Cheat Sheets (`mathstore ref`)
Quick-lookup reference sheets formatted for terminal reading or LaTeX export:
- `mathstore ref derivatives`
- `mathstore ref integrals`
- `mathstore ref trig`
- `mathstore ref limits`
- `mathstore ref series`
- `mathstore ref --list`
