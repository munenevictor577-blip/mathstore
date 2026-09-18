from fastapi import APIRouter, HTTPException, Query

from mathstore.api.schemas import (
    DiffRequest,
    DiffResponse,
    IntegrateRequest,
    IntegrateResponse,
    LimitRequest,
    LimitResponse,
)
from mathstore.calculus.analyzer import CalculusAnalyzer

router = APIRouter(tags=["Calculus"])
analyzer = CalculusAnalyzer()


@router.post("/diff", response_model=DiffResponse, summary="Differentiate a mathematical expression")
def differentiate_post(req: DiffRequest) -> DiffResponse:
    """Calculates the nth derivative of an algebraic expression with optional steps."""
    try:
        steps_list = (
            analyzer.differentiate_steps(req.expression, variable=req.variable, order=req.order)
            if req.steps
            else None
        )
        res = analyzer.differentiate(
            req.expression, variable=req.variable, order=req.order, format=req.format
        )
        return DiffResponse(
            expression=req.expression,
            variable=req.variable,
            order=req.order,
            derivative=str(res),
            format=req.format,
            steps=steps_list,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/diff", response_model=DiffResponse, summary="Differentiate (GET query)")
def differentiate_get(
    expression: str = Query(..., description="Expression to differentiate"),
    variable: str = Query("x", description="Variable of differentiation"),
    order: int = Query(1, ge=1, description="Derivative order"),
    steps: bool = Query(False, description="Include steps"),
    format: str = Query("str", description="Output format"),
) -> DiffResponse:
    return differentiate_post(
        DiffRequest(
            expression=expression,
            variable=variable,
            order=order,
            steps=steps,
            format=format,
        )
    )


@router.post("/integrate", response_model=IntegrateResponse, summary="Integrate an expression")
def integrate_post(req: IntegrateRequest) -> IntegrateResponse:
    """Calculates indefinite or definite integrals with optional step derivations."""
    try:
        steps_list = (
            analyzer.integrate_steps(req.expression, variable=req.variable, limits=req.limits)
            if req.steps
            else None
        )
        res = analyzer.integrate(
            req.expression, variable=req.variable, limits=req.limits, format=req.format
        )
        return IntegrateResponse(
            expression=req.expression,
            variable=req.variable,
            limits=req.limits,
            integral=str(res),
            format=req.format,
            steps=steps_list,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/integrate", response_model=IntegrateResponse, summary="Integrate (GET query)")
def integrate_get(
    expression: str = Query(..., description="Expression to integrate"),
    variable: str = Query("x", description="Variable of integration"),
    lower_limit: float | None = Query(None, description="Lower bound for definite integral"),
    upper_limit: float | None = Query(None, description="Upper bound for definite integral"),
    steps: bool = Query(False, description="Include steps"),
    format: str = Query("str", description="Output format"),
) -> IntegrateResponse:
    limits = (lower_limit, upper_limit) if lower_limit is not None and upper_limit is not None else None
    return integrate_post(
        IntegrateRequest(
            expression=expression,
            variable=variable,
            limits=limits,
            steps=steps,
            format=format,
        )
    )


@router.post("/limit", response_model=LimitResponse, summary="Evaluate a limit")
def limit_post(req: LimitRequest) -> LimitResponse:
    """Calculates the limit of an expression approaching a target value."""
    try:
        res = analyzer.get_limit(
            req.expression, limits=req.target, variable=req.variable, format=req.format
        )
        return LimitResponse(
            expression=req.expression,
            target=req.target,
            variable=req.variable,
            limit=str(res),
            format=req.format,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/limit", response_model=LimitResponse, summary="Evaluate a limit (GET query)")
def limit_get(
    expression: str = Query(..., description="Expression to evaluate"),
    target: str = Query(..., description="Target value, e.g. 0, oo, -oo"),
    variable: str = Query("x", description="Limit variable"),
    format: str = Query("str", description="Output format"),
) -> LimitResponse:
    return limit_post(
        LimitRequest(
            expression=expression,
            target=target,
            variable=variable,
            format=format,
        )
    )
