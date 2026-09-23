from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mathstore.api.routes import (
    algebra_router,
    calculus_router,
    matrix_router,
    statistics_router,
    study_router,
)


def create_app() -> FastAPI:
    """Creates and configures the MathStore FastAPI application."""
    app = FastAPI(
        title="MathStore API",
        description=(
            "Clean, modular mathematical API toolkit for university students, educators, "
            "and STEM applications. Provides symbolic calculus, step-by-step derivations, "
            "linear algebra, probability, statistics, reference cheat sheets, and active-recall practice."
        ),
        version="0.1.1a2",
        root_path="/math",
    )

    # Enable CORS for cross-origin and remote frontend calling
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core math router with all mathematical endpoints
    math_router = APIRouter()

    # Register sub-routers
    math_router.include_router(calculus_router)
    math_router.include_router(algebra_router)
    math_router.include_router(matrix_router)
    math_router.include_router(statistics_router)
    math_router.include_router(study_router)

    # Mount mathematical endpoints directly at root: math/diff, math/integrate, etc.
    app.include_router(math_router)

    @app.get("/health", summary="Global health check", include_in_schema=False)
    def global_health() -> dict[str, Any]:
        return {"status": "ok", "service": "mathstore", "version": app.version}

    return app


app = create_app()


def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Runs the FastAPI server using uvicorn."""
    uvicorn.run("mathstore.api.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run()
