"""API route handlers for Ordinary Differential Equations (ODEs)."""

from fastapi import APIRouter, HTTPException, Query

from mathstore.api.schemas import (
    ODECheckRequest,
    ODECheckResponse,
    ODEClassifyRequest,
    ODEClassifyResponse,
    ODESolveRequest,
    ODESolveResponse,
    ODEStepsRequest,
    StepsResponse,
)
from mathstore.ode.solver import ODESolver

router = APIRouter(prefix="/ode", tags=["ODE"])
solver = ODESolver()


@router.post(
    "/solve",
    response_model=ODESolveResponse,
    summary="Solve an ordinary differential equation",
)
def ode_solve_post(req: ODESolveRequest) -> ODESolveResponse:
    """Solves first- and higher-order ODEs with optional initial conditions (IVP)."""
    try:
        sol = solver.solve(
            req.equation,
            ics=req.ics,
            var=req.variable,
            func=req.function,
            hint=req.hint,
            format=req.format,
        )
        steps_list = (
            solver.get_steps(req.equation, var=req.variable, func=req.function)
            if req.steps
            else None
        )
        return ODESolveResponse(
            equation=req.equation,
            variable=req.variable,
            function=req.function,
            solution=sol if isinstance(sol, (str, list)) else str(sol),
            format=req.format,
            ics=req.ics,
            steps=steps_list,
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/solve", response_model=ODESolveResponse, summary="Solve an ODE (GET query)"
)
def ode_solve_get(
    equation: str = Query(
        ..., description="Differential equation to solve (e.g. y' + 2*y = exp(x))"
    ),
    ics: str | None = Query(
        None, description="Optional initial conditions (e.g. y(0)=1, y'(0)=2)"
    ),
    variable: str = Query("x", description="Independent variable"),
    function: str = Query("y", description="Dependent function"),
    hint: str = Query("default", description="Optional solving hint"),
    format: str = Query("str", description="Output format"),
    steps: bool = Query(False, description="Include step-by-step breakdown"),
) -> ODESolveResponse:
    return ode_solve_post(
        ODESolveRequest(
            equation=equation,
            ics=ics,
            variable=variable,
            function=function,
            hint=hint,
            format=format,
            steps=steps,
        )
    )


@router.post(
    "/steps",
    response_model=StepsResponse,
    summary="Step-by-step ODE solution breakdown",
)
def ode_steps_post(req: ODEStepsRequest) -> StepsResponse:
    """Returns pedagogical step-by-step derivation for solving an ODE."""
    try:
        steps = solver.get_steps(req.equation, var=req.variable, func=req.function)
        return StepsResponse(query=req.equation, steps=steps)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/steps",
    response_model=StepsResponse,
    summary="Step-by-step ODE solution (GET query)",
)
def ode_steps_get(
    equation: str = Query(..., description="Differential equation to explain"),
    variable: str = Query("x", description="Independent variable"),
    function: str = Query("y", description="Dependent function"),
) -> StepsResponse:
    return ode_steps_post(
        ODEStepsRequest(equation=equation, variable=variable, function=function)
    )


@router.post("/classify", response_model=ODEClassifyResponse, summary="Classify an ODE")
def ode_classify_post(req: ODEClassifyRequest) -> ODEClassifyResponse:
    """Determines differential order, linearity, homogeneity, and solving methods."""
    try:
        info = solver.classify(req.equation, var=req.variable, func=req.function)
        return ODEClassifyResponse(
            equation=req.equation,
            variable=req.variable,
            function=req.function,
            order=info["order"],
            is_linear=info["is_linear"],
            is_homogeneous=info["is_homogeneous"],
            hints=info["hints"],
            primary_type=info["primary_type"],
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/classify",
    response_model=ODEClassifyResponse,
    summary="Classify an ODE (GET query)",
)
def ode_classify_get(
    equation: str = Query(..., description="Differential equation to classify"),
    variable: str = Query("x", description="Independent variable"),
    function: str = Query("y", description="Dependent function"),
) -> ODEClassifyResponse:
    return ode_classify_post(
        ODEClassifyRequest(
            equation=equation,
            variable=variable,
            function=function,
        )
    )


@router.post(
    "/check", response_model=ODECheckResponse, summary="Verify an ODE solution"
)
def ode_check_post(req: ODECheckRequest) -> ODECheckResponse:
    """Verifies whether a candidate solution satisfies a differential equation."""
    try:
        is_valid = solver.check_solution(
            req.equation,
            req.solution,
            var=req.variable,
            func=req.function,
        )
        return ODECheckResponse(
            equation=req.equation,
            solution=req.solution,
            variable=req.variable,
            function=req.function,
            is_valid=is_valid,
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/check",
    response_model=ODECheckResponse,
    summary="Verify an ODE solution (GET query)",
)
def ode_check_get(
    equation: str = Query(..., description="Original differential equation"),
    solution: str = Query(..., description="Candidate solution to verify"),
    variable: str = Query("x", description="Independent variable"),
    function: str = Query("y", description="Dependent function"),
) -> ODECheckResponse:
    return ode_check_post(
        ODECheckRequest(
            equation=equation,
            solution=solution,
            variable=variable,
            function=function,
        )
    )
