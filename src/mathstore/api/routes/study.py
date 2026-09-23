import random

from fastapi import APIRouter, HTTPException, Query

from mathstore.api.schemas import (
    DerivativeStepsRequest,
    EquationStepsRequest,
    IntegralStepsRequest,
    PracticeCheckRequest,
    PracticeCheckResponse,
    PracticeQuestionResponse,
    ReferenceListResponse,
    ReferenceResponse,
    StepsResponse,
)
from mathstore.reference import get_reference, list_topics, list_topics_formatted
from mathstore.study.practice import (
    PracticeQuestion,
    check_answer,
    generate_question,
)
from mathstore.study.steps import (
    get_derivative_steps,
    get_equation_steps,
    get_integral_steps,
)

router = APIRouter(tags=["Study, Steps & Practice"])


# --- Step Breakdown Endpoints ---
@router.post(
    "/steps/diff",
    response_model=StepsResponse,
    summary="Step-by-step differentiation breakdown",
)
def steps_derivative_post(req: DerivativeStepsRequest) -> StepsResponse:
    """Returns rule-by-rule differentiation steps for an expression."""
    try:
        steps = get_derivative_steps(
            req.expression, variable=req.variable, order=req.order
        )
        return StepsResponse(query=req.expression, steps=steps)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/steps/diff",
    response_model=StepsResponse,
    summary="Step-by-step differentiation (GET query)",
)
def steps_derivative_get(
    expression: str = Query(..., description="Expression to differentiate"),
    variable: str = Query("x", description="Variable of differentiation"),
    order: int = Query(1, ge=1, description="Derivative order"),
) -> StepsResponse:
    return steps_derivative_post(
        DerivativeStepsRequest(expression=expression, variable=variable, order=order)
    )


@router.post(
    "/steps/integrate",
    response_model=StepsResponse,
    summary="Step-by-step integration breakdown",
)
def steps_integral_post(req: IntegralStepsRequest) -> StepsResponse:
    """Returns rule-by-rule integration steps (including FTC for definite integrals)."""
    try:
        steps = get_integral_steps(
            req.expression, variable=req.variable, limits=req.limits
        )
        return StepsResponse(query=req.expression, steps=steps)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/steps/integrate",
    response_model=StepsResponse,
    summary="Step-by-step integration (GET query)",
)
def steps_integral_get(
    expression: str = Query(..., description="Expression to integrate"),
    variable: str = Query("x", description="Integration variable"),
    lower_limit: float | None = Query(None, description="Lower limit"),
    upper_limit: float | None = Query(None, description="Upper limit"),
) -> StepsResponse:
    limits = (
        (lower_limit, upper_limit)
        if lower_limit is not None and upper_limit is not None
        else None
    )
    return steps_integral_post(
        IntegralStepsRequest(expression=expression, variable=variable, limits=limits)
    )


@router.post(
    "/steps/solve",
    response_model=StepsResponse,
    summary="Step-by-step equation solving breakdown",
)
def steps_equation_post(req: EquationStepsRequest) -> StepsResponse:
    """Returns algebraic isolation and solution steps for an equation."""
    try:
        steps = get_equation_steps(req.equation, variable=req.variable)
        return StepsResponse(query=req.equation, steps=steps)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/steps/solve",
    response_model=StepsResponse,
    summary="Step-by-step equation solving (GET query)",
)
def steps_equation_get(
    equation: str = Query(..., description="Equation to solve"),
    variable: str = Query("x", description="Variable to isolate"),
) -> StepsResponse:
    return steps_equation_post(
        EquationStepsRequest(equation=equation, variable=variable)
    )


# --- Practice Endpoints ---
@router.get(
    "/practice/question",
    response_model=PracticeQuestionResponse,
    summary="Generate a randomized practice question",
)
def practice_question_get(
    topic: str = Query(
        "all",
        description="Topic: derivatives, integrals, algebra, matrix, stats, or all",
    ),
    difficulty: str = Query(
        "medium", description="Difficulty: easy, medium, hard, or all"
    ),
    seed: int | None = Query(
        None, description="Optional seed for deterministic generation"
    ),
) -> PracticeQuestionResponse:
    """Generates an active-recall practice question with hints, steps, and expected answer."""
    rng = random.Random(seed) if seed is not None else None
    q = generate_question(topic=topic, difficulty=difficulty, rng=rng)
    return PracticeQuestionResponse(
        topic=q.topic,
        difficulty=q.difficulty,
        prompt=q.prompt,
        hint=q.hint,
        expected_answer=q.expected_answer,
        question_type=q.question_type,
        steps=q.steps,
    )


@router.post(
    "/practice/check",
    response_model=PracticeCheckResponse,
    summary="Verify student's answer with symbolic equivalence",
)
def practice_check_post(req: PracticeCheckRequest) -> PracticeCheckResponse:
    """Checks an answer using symbolic equivalence, root sets, or numerical tolerance."""
    q = PracticeQuestion(
        topic=req.topic,
        difficulty=req.difficulty,
        prompt=req.prompt,
        expected_answer=req.expected_answer,
        hint=req.hint,
        steps=req.steps,
        question_type=req.question_type,
        correct_value=req.correct_value,
        variable=req.variable,
        is_definite=req.is_definite,
        tolerance=req.tolerance,
    )
    is_correct, feedback = check_answer(req.user_input, q)
    return PracticeCheckResponse(is_correct=is_correct, feedback=feedback)


# --- Reference Cheat Sheet Endpoints ---
@router.get(
    "/ref",
    response_model=ReferenceListResponse,
    summary="List available reference topics",
)
def reference_list() -> ReferenceListResponse:
    """Lists all formula reference cheat sheets available."""
    topics = list_topics()
    formatted = list_topics_formatted()
    return ReferenceListResponse(topics=topics, formatted=formatted)


@router.get(
    "/ref/{topic}",
    response_model=ReferenceResponse,
    summary="Get topic reference cheat sheet",
)
def reference_get(
    topic: str,
    latex: bool = Query(
        False, description="Output in LaTeX format instead of Markdown text"
    ),
) -> ReferenceResponse:
    """Returns formula cheat sheet for derivatives, integrals, trig, limits, or series."""
    try:
        content = get_reference(topic, latex=latex)
        return ReferenceResponse(
            topic=topic,
            content=content,
            latex=latex,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
