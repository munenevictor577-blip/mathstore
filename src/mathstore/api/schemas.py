from typing import Any

from pydantic import BaseModel, Field


# --- Calculus Schemas ---
class DiffRequest(BaseModel):
    expression: str = Field(..., description="Mathematical expression, e.g. 'x**2 * sin(x)'")
    variable: str = Field("x", description="Variable to differentiate with respect to")
    order: int = Field(1, ge=1, description="Derivative order (default: 1)")
    steps: bool = Field(False, description="Include step-by-step derivation breakdown")
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


class DiffResponse(BaseModel):
    expression: str
    variable: str
    order: int
    derivative: str
    format: str
    steps: list[str] | None = None


class IntegrateRequest(BaseModel):
    expression: str = Field(..., description="Mathematical expression to integrate")
    variable: str = Field("x", description="Variable of integration")
    limits: tuple[float, float] | None = Field(
        None, description="Optional bounds for definite integral (lower, upper)"
    )
    steps: bool = Field(False, description="Include step-by-step integration breakdown")
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


class IntegrateResponse(BaseModel):
    expression: str
    variable: str
    limits: tuple[float, float] | None = None
    integral: str
    format: str
    steps: list[str] | None = None


class LimitRequest(BaseModel):
    expression: str = Field(..., description="Mathematical expression, e.g. 'sin(x)/x'")
    target: str = Field(..., description="Value the variable approaches, e.g. '0', 'oo', '-oo'")
    variable: str = Field("x", description="Variable for limit")
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


class LimitResponse(BaseModel):
    expression: str
    target: str
    variable: str
    limit: str
    format: str


# --- Algebra Schemas ---
class SolveRequest(BaseModel):
    equation: str = Field(
        ..., description="Equation to solve, e.g. '2*x + 4 = 10' or 'x**2 - 5*x + 6 = 0'"
    )
    variable: str = Field("x", description="Variable to isolate")
    steps: bool = Field(False, description="Include step-by-step algebraic breakdown")
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


class SolveResponse(BaseModel):
    equation: str
    variable: str
    solutions: list[Any]
    formatted: str
    format: str
    steps: list[str] | None = None


class SimplifyRequest(BaseModel):
    expression: str = Field(..., description="Expression to algebraically simplify")


class SimplifyResponse(BaseModel):
    expression: str
    simplified: str


# --- Matrix Schemas ---
class MatrixRequest(BaseModel):
    matrix: str = Field(
        ..., description="Matrix string (e.g. '1, 2; 3, 4' or '[[1, 2], [3, 4]]')"
    )
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


class MatrixResponse(BaseModel):
    operation: str
    matrix: str
    result: Any
    format: str


# --- Statistics Schemas ---
class StatsSummaryRequest(BaseModel):
    data: str | list[float] = Field(
        ..., description="Dataset as string (e.g. '10, 12, 14') or float list"
    )
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


class NormalRequest(BaseModel):
    x: float = Field(..., description="Point to evaluate")
    mu: float = Field(0.0, description="Mean (default: 0.0)")
    sigma: float = Field(1.0, gt=0, description="Standard deviation (default: 1.0)")


class BinomialRequest(BaseModel):
    k: int = Field(..., ge=0, description="Number of successes")
    n: int = Field(..., ge=1, description="Number of trials")
    p: float = Field(..., ge=0.0, le=1.0, description="Success probability")


class PoissonRequest(BaseModel):
    k: int = Field(..., ge=0, description="Number of occurrences")
    lam: float = Field(..., gt=0, description="Rate parameter lambda")


class ConfidenceIntervalRequest(BaseModel):
    data: str | list[float] = Field(..., description="Sample dataset")
    confidence: float = Field(0.95, gt=0.0, lt=1.0, description="Confidence level (default: 0.95)")
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


class TTestRequest(BaseModel):
    data: str | list[float] = Field(..., description="Sample dataset")
    pop_mean: float = Field(..., description="Null hypothesis population mean")
    alternative: str = Field(
        "two-sided", description="Alternative hypothesis: 'two-sided', 'greater', or 'less'"
    )
    format: str = Field("str", description="Output format: 'str', 'latex', or 'pretty'")


# --- Step Breakdown Schemas ---
class DerivativeStepsRequest(BaseModel):
    expression: str = Field(..., description="Expression to differentiate")
    variable: str = Field("x", description="Variable of differentiation")
    order: int = Field(1, ge=1, description="Derivative order")


class IntegralStepsRequest(BaseModel):
    expression: str = Field(..., description="Expression to integrate")
    variable: str = Field("x", description="Variable of integration")
    limits: tuple[float, float] | None = Field(None, description="Definite integral bounds")


class EquationStepsRequest(BaseModel):
    equation: str = Field(..., description="Equation to solve")
    variable: str = Field("x", description="Variable to isolate")


class StepsResponse(BaseModel):
    query: str
    steps: list[str]


# --- Practice & Reference Schemas ---
class PracticeQuestionResponse(BaseModel):
    topic: str
    difficulty: str
    prompt: str
    hint: str
    expected_answer: str
    question_type: str
    steps: list[str]


class PracticeCheckRequest(BaseModel):
    user_input: str = Field(..., description="User's submitted answer")
    topic: str
    difficulty: str = "medium"
    prompt: str = ""
    expected_answer: str
    hint: str = ""
    steps: list[str] = Field(default_factory=list)
    question_type: str = "symbolic"
    correct_value: Any = None
    variable: str = "x"
    is_definite: bool = False
    tolerance: float = 1e-2


class PracticeCheckResponse(BaseModel):
    is_correct: bool
    feedback: str


class ReferenceListResponse(BaseModel):
    topics: dict[str, str] | list[str]
    formatted: str


class ReferenceResponse(BaseModel):
    topic: str
    content: str
    latex: bool
