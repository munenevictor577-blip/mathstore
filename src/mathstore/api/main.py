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
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
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

    def math_root_info() -> dict[str, Any]:
        """Root API metadata index for the Math API prefix."""
        return {
            "name": "MathStore API",
            "description": "Mathematical Toolkit API for university study and revision",
            "version": "0.1.0",
            "prefix": "/math",
            "docs_url": "/math/docs",
            "redoc_url": "/math/redoc",
            "openapi_url": "/math/openapi.json",
            "health_url": "/math/health",
        }

    def math_health_info() -> dict[str, Any]:
        """Health check endpoint for the Math API prefix."""
        return {
            "status": "healthy",
            "service": "mathstore",
            "prefix": "/math",
            "version": "0.1.0",
        }

    # Math prefix health and index endpoints
    @app.get("/math/health", summary="Math API health check")
    @app.get("/api/v1/math/health", summary="API v1 Math health check", include_in_schema=False)
    @app.get("/api/v1/health", summary="API v1 health check", include_in_schema=False)
    def math_health() -> dict[str, Any]:
        return math_health_info()

    @app.get("/math", summary="Math API Index", include_in_schema=False)
    @app.get("/math/", summary="Math API Index")
    @app.get("/api/v1/math", summary="API v1 Math Index", include_in_schema=False)
    @app.get("/api/v1/math/", summary="API v1 Math Index", include_in_schema=False)
    def math_root() -> dict[str, Any]:
        return math_root_info()

    # Documentation and schema endpoints for /math prefix
    @app.get("/math/docs", include_in_schema=False)
    def math_docs():
        from fastapi.openapi.docs import get_swagger_ui_html
        return get_swagger_ui_html(
            openapi_url="/math/openapi.json",
            title=app.title + " - Swagger UI",
            oauth2_redirect_url="/docs/oauth2-redirect",
        )


    @app.get("/math/redoc", include_in_schema=False)
    def math_redoc():
        from fastapi.openapi.docs import get_redoc_html
        return get_redoc_html(openapi_url="/math/openapi.json", title=app.title + " - ReDoc")

    @app.get("/math/openapi.json", include_in_schema=False)
    def math_openapi():
        from fastapi.responses import JSONResponse
        return JSONResponse(content=app.openapi())

    # Mount mathematical endpoints directly at root: /diff, /integrate, etc.
    app.include_router(math_router)

    # Mount mathematical endpoints under /math: /math/diff, /math/integrate, etc.
    app.include_router(math_router, prefix="/math")

    # Maintain backward compatibility for /api/v1/math and /api/v1 callers
    app.include_router(math_router, prefix="/api/v1/math", include_in_schema=False)
    app.include_router(math_router, prefix="/api/v1", include_in_schema=False)

    # Root informational routes
    @app.get("/", summary="Root API Index", include_in_schema=False)
    def root() -> dict[str, Any]:
        return math_root_info()

    @app.get("/health", summary="Global health check", include_in_schema=False)
    def global_health() -> dict[str, Any]:
        return {"status": "ok", "service": "mathstore", "version": "0.1.0"}


    return app


app = create_app()


def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Runs the FastAPI server using uvicorn."""
    uvicorn.run("mathstore.api.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run()
