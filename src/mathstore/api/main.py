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
        version="0.1.0",
        docs_url="/api/v1/math/docs",
        redoc_url="/redoc",
    )

    # Enable CORS for cross-origin and remote frontend calling
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core math router with the required prefix: /api/v1/math
    math_router = APIRouter(prefix="/api/v1/math")

    @math_router.get("/health", summary="Math API health check")
    def math_health() -> dict[str, Any]:
        """Health check endpoint for the Math API prefix."""
        return {
            "status": "healthy",
            "service": "mathstore",
            "prefix": "/api/v1/math",
            "version": "0.1.0",
        }

    # Register sub-routers under /api/v1/math
    math_router.include_router(calculus_router)
    math_router.include_router(algebra_router)
    math_router.include_router(matrix_router)
    math_router.include_router(statistics_router)
    math_router.include_router(study_router)

    # Mount the general math router on the app
    app.include_router(math_router)

    # Root informational routes
    @app.get("/", summary="Root API Index")
    def root() -> dict[str, Any]:
        return {
            "name": "MathStore API",
            "description": "Mathematical Toolkit API for university study and revision",
            "version": "0.1.0",
            "prefix": "/api/v1/math",
            "docs_url": "/api/v1/math/docs",
            "redoc_url": "/redoc",
            "health_url": "/api/v1/math/health",
        }

    @app.get("/health", summary="Global health check")
    def global_health() -> dict[str, Any]:
        return {"status": "ok", "service": "mathstore", "version": "0.1.0"}

    return app


app = create_app()


def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Runs the FastAPI server using uvicorn."""
    uvicorn.run("mathstore.api.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run()
