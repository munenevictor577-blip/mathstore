from fastapi import APIRouter, HTTPException, Query

from mathstore.algebra.solver import EquationSolver
from mathstore.api.schemas import (
    SimplifyRequest,
    SimplifyResponse,
    SolveRequest,
    SolveResponse,
)

router = APIRouter(tags=["Algebra"])
solver = EquationSolver()


@router.post("/solve", response_model=SolveResponse, summary="Solve an algebraic equation")
def solve_post(req: SolveRequest) -> SolveResponse:
    """Solves linear and polynomial equations with optional step-by-step breakdown."""
    try:
        steps_list = (
            solver.solve_steps(req.equation, variable=req.variable)
            if req.steps
            else None
        )
        solutions = solver.solve_linear(req.equation, variable=req.variable)
        formatted = solver.format_solution(
            solutions, variable=req.variable, format=req.format
        )
        return SolveResponse(
            equation=req.equation,
            variable=req.variable,
            solutions=[str(s) for s in solutions],
            formatted=formatted,
            format=req.format,
            steps=steps_list,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/solve", response_model=SolveResponse, summary="Solve an equation (GET query)")
def solve_get(
    equation: str = Query(..., description="Equation to solve (e.g. 2*x + 4 = 10)"),
    variable: str = Query("x", description="Variable to isolate"),
    steps: bool = Query(False, description="Include steps"),
    format: str = Query("str", description="Output format"),
) -> SolveResponse:
    return solve_post(
        SolveRequest(
            equation=equation,
            variable=variable,
            steps=steps,
            format=format,
        )
    )


@router.post("/simplify", response_model=SimplifyResponse, summary="Simplify an algebraic expression")
def simplify_post(req: SimplifyRequest) -> SimplifyResponse:
    """Simplifies mathematical expressions."""
    try:
        res = solver.simplify_expression(req.expression)
        return SimplifyResponse(
            expression=req.expression,
            simplified=res,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/simplify", response_model=SimplifyResponse, summary="Simplify (GET query)")
def simplify_get(
    expression: str = Query(..., description="Expression to simplify"),
) -> SimplifyResponse:
    return simplify_post(SimplifyRequest(expression=expression))
