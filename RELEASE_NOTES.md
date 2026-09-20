# Release Notes - MathStore v0.1.0

**Release Date:** September 20, 2026  
**Tag:** `v0.1.0`  
**License:** MIT  

---

## 🌟 Overview

**MathStore v0.1.0** is the inaugural production release of MathStore — a clean, modular mathematical toolkit, interactive CLI, and FastAPI remote service designed for university students, educators, and STEM practitioners. 

MathStore combines symbolic computation (SymPy), numerical analysis (NumPy), and modern asynchronous web architecture (FastAPI) into a unified toolkit with active-recall learning tools.

---

## 🚀 Key Features & Highlights

### 1. Symbolic Calculus & Advanced Parsing
- **Differentiation (`diff`)**: First- and higher-order derivatives (`--order N`, `--var x`).
- **Integration (`integrate`)**: Indefinite integration and definite integrals with boundary evaluation (`--limits a b`).
- **Limits (`limit`)**: Finite and infinite limits (`oo`, `-oo`) with one-sided directional support (`+`, `-`).
- **Natural Math Expression Parsing**: Automatic conversion of natural mathematical syntax (e.g., `2^x sin x`, `2x + 4`, `e^(2x)`) into valid symbolic expressions with implicit multiplication and exponentiation handling.

### 2. Step-by-Step Derivations (`--steps`)
- Human-readable derivation trees explaining the mathematical rules applied:
  - **Differentiation**: Power rule, product rule, quotient rule, chain rule, exponential, logarithmic, and trigonometric derivatives.
  - **Integration**: Power rule, substitution ($u$-substitution), integration by parts, and Fundamental Theorem of Calculus (FTC) evaluation for definite integrals.
  - **Equation Solving**: Linear and quadratic equations with discriminant analysis and root isolation steps.

### 3. Linear Algebra (`matrix`)
- Comprehensive matrix operations supporting string and bracket input syntax (`"1, 2; 3, 4"` or `"[[1, 2], [3, 4]]"`):
  - Determinants (`det`) and Matrix Inverses (`inv`)
  - Reduced Row Echelon Form (`rref`) with pivot column tracking
  - Eigenvalues (`eigen`) and Eigenvectors (`eigenvects`) with algebraic and geometric multiplicities
  - Rank (`rank`), Nullity (`nullity`), Trace (`trace`), Transpose (`transpose`)
  - Characteristic Polynomials (`charpoly`)

### 4. Probability, Statistics & Inference (`stats`)
- **Descriptive Statistics**: Five-number summary (mean, median, variance, standard deviation, IQR, skewness, kurtosis).
- **Distributions**:
  - Normal distribution PDF, CDF, and standard $z$-score.
  - Binomial distribution PMF and CDF.
  - Poisson distribution PMF and CDF.
- **Statistical Inference**:
  - Confidence intervals for sample means at arbitrary confidence levels (`--confidence 0.95`).
  - One-sample Student's $t$-test with two-sided, greater, or less hypothesis alternatives (`--alt`).

### 5. Active-Recall Practice Quizzer (`mathstore practice`)
- Interactive terminal study tool for exam preparation and revision:
  - Topics: `derivatives`, `integrals`, `algebra`, `matrix`, `stats`, or `all`.
  - Difficulty tiers: `easy`, `medium`, `hard`.
  - **Smart Equivalence Engine**: Accepts mathematically equivalent student submissions regardless of notation (`^` vs `**`, constant permutations, arbitrary constants `+ C`, multi-root sets).
  - On-demand formula hints and full step-by-step solution reveals on skip.
  - Non-interactive worksheet generation (`--generate` / `-g`) with configurable seed for repeatable problem sets.

### 6. Formula Reference Cheat Sheets (`ref`)
- High-yield quick-reference cheat sheets directly in the terminal:
  - Categories: `derivatives`, `integrals`, `trig`, `limits`, `series`.
  - Full LaTeX export capability via `--latex` for inclusion in assignments and lab reports.

### 7. Multi-Format Output: LaTeX & Unicode
- All analytical commands support `--latex` for direct LaTeX formula rendering and `--pretty` for 2D Unicode pretty-printing in modern terminal environments.

### 8. Production-Ready FastAPI Remote Server
- Complete HTTP REST API for web and mobile integration:
  - Unified routing: Root endpoints (`/diff`, `/integrate`, `/matrix/...`), `/math` prefix endpoints (`/math/diff`, `/math/matrix/...`), and `/api/v1/math` backward-compatibility aliases.
  - Interactive Swagger UI (`/docs` and `/math/docs`) and ReDoc (`/redoc` and `/math/redoc`).
  - OpenAPI 3.1 JSON schema (`/openapi.json` and `/math/openapi.json`).
  - Health check endpoint (`/health` and `/math/health`).
  - CORS middleware enabled for cross-origin web client integration.
  - CLI server runner: `mathstore-server` or `uvicorn mathstore.api.main:app`.

---

## 📦 Packaging & CI/CD Workflows

- **Package Management**: Built with modern PEP 621 / PEP 735 standards using `uv` and `uv_build`.
- **Python Support**: Tested and verified on Python 3.12+.
- **Automated Deployment**: GitHub Actions workflow (`deploy.yml`) synchronizing `main` with production GCP hosts.
- **PyPI Publishing Workflow**: Modernized `publish.yml` supporting:
  - Astral `setup-uv@v5` with caching.
  - Pytest verification (`uv sync --dev` + `uv run pytest`) before building distributions.
  - Trusted Publishing via OIDC (`permissions: id-token: write`).
  - Two-stage rollout: Automated TestPyPI upload on release tags, with optional manual dispatch to PyPI or TestPyPI.

---

## 🧪 Quality Assurance & Test Verification

- **Unit & Integration Tests**: 257 passing tests across all modules.
- **Code Coverage**: 91% overall coverage across `mathstore`.
- **Endpoint Verification**: 102/102 automated endpoint test cases passing across calculus, algebra, matrix, statistics, step derivation, practice, and reference routes.

---

## 💻 Installation

### Using `uv` (Recommended)
```bash
# Add to your project
uv add mathstore

# Or run directly in a transient environment
uvx mathstore --help
```

### Using `pip`
```bash
pip install mathstore
```

### From Source
```bash
git clone https://github.com/munenevictor577-blip/mathstore.git
cd mathstore
uv sync --dev
uv run pytest
```
