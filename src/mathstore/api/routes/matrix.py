from typing import Any

from fastapi import APIRouter, HTTPException

from mathstore.api.schemas import MatrixRequest, MatrixResponse
from mathstore.core.matrix import MatrixAnalyzer

router = APIRouter(prefix="/matrix", tags=["Linear Algebra / Matrix"])
analyzer = MatrixAnalyzer()

VALID_OPERATIONS = {
    "det": analyzer.determinant,
    "inv": analyzer.inverse,
    "rref": analyzer.rref,
    "eigen": analyzer.eigenvalues,
    "eigenvects": analyzer.eigenvectors,
    "rank": analyzer.rank,
    "nullity": analyzer.nullity,
    "trace": analyzer.trace,
    "transpose": analyzer.transpose,
    "charpoly": analyzer.characteristic_polynomial,
}


@router.post(
    "/{operation}", response_model=MatrixResponse, summary="Perform matrix operation"
)
def matrix_operation(operation: str, req: MatrixRequest) -> MatrixResponse:
    """Executes a linear algebra operation on a given matrix string."""
    op_lower = operation.lower().strip()
    if op_lower not in VALID_OPERATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported matrix operation '{operation}'. Choose from: {list(VALID_OPERATIONS.keys())}",
        )
    try:
        fn = VALID_OPERATIONS[op_lower]
        # rank and nullity do not accept format parameter
        if op_lower in ("rank", "nullity"):
            res: Any = fn(req.matrix)
        else:
            res = fn(req.matrix, format=req.format)

        return MatrixResponse(
            operation=op_lower,
            matrix=req.matrix,
            result=res,
            format=req.format,
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
