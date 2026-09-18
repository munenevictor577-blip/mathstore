from mathstore.api.routes.algebra import router as algebra_router
from mathstore.api.routes.calculus import router as calculus_router
from mathstore.api.routes.matrix import router as matrix_router
from mathstore.api.routes.statistics import router as statistics_router
from mathstore.api.routes.study import router as study_router

__all__ = [
    "algebra_router",
    "calculus_router",
    "matrix_router",
    "statistics_router",
    "study_router",
]
