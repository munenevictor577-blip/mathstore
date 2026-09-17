"""Linear algebra and matrix analysis toolkit for university mathematics."""

import ast
from typing import Any

import sympy as sp


class MatrixAnalyzer:
    """Handles matrix operations and linear algebra computations."""

    def parse_matrix(self, matrix_input: Any) -> sp.Matrix:
        """
        Parses various matrix formats into a SymPy Matrix.

        Supported input types:
          - sympy.Matrix
          - list / tuple of lists / tuples: [[1, 2], [3, 4]]
          - string in list format: '[[1, 2], [3, 4]]'
          - string in MATLAB/semicolon format: '1, 2; 3, 4' or '1 2; 3 4'

        Raises:
            ValueError: If input format is invalid, empty, or non-rectangular.
        """
        if isinstance(matrix_input, sp.Matrix):
            return matrix_input

        if isinstance(matrix_input, (list, tuple)):
            try:
                mat = sp.Matrix(matrix_input)
                if mat.rows == 0 or mat.cols == 0:
                    raise ValueError("Matrix cannot be empty.")
                return mat
            except Exception as e:  # noqa: BLE001
                raise ValueError(f"Failed to parse matrix from collection: {e}")

        if isinstance(matrix_input, str):
            raw = matrix_input.strip()
            if not raw:
                raise ValueError("Matrix input string cannot be empty.")

            # Try parsing Python nested list syntax
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    data = ast.literal_eval(raw)
                    mat = sp.Matrix(data)
                    if mat.rows == 0 or mat.cols == 0:
                        raise ValueError("Matrix cannot be empty.")
                    return mat
                except Exception:  # noqa: BLE001, S110
                    pass

            # Try parsing semicolon-separated row format: "1, 2; 3, 4" or "1 2; 3 4"
            try:
                row_strs = [r.strip() for r in raw.split(";") if r.strip()]
                if not row_strs:
                    raise ValueError("Matrix input contains no rows.")

                data = []
                for row_str in row_strs:
                    items = [
                        sp.sympify(part.strip())
                        for part in row_str.replace(",", " ").split()
                        if part.strip()
                    ]
                    if not items:
                        raise ValueError("Encountered an empty row in matrix input.")
                    data.append(items)

                mat = sp.Matrix(data)
                return mat
            except Exception as e:  # noqa: BLE001
                raise ValueError(f"Failed to parse matrix string '{matrix_input}': {e}")

        raise ValueError(f"Unsupported matrix input type: {type(matrix_input).__name__}")

    def _format_expr(self, expr: Any, format: str = "str") -> str:
        """Format an expression or matrix into str, latex, or pretty format."""
        if format == "latex":
            return sp.latex(expr)
        if format == "pretty":
            return sp.pretty(expr, use_unicode=True)
        return str(expr)

    def determinant(self, matrix_input: Any, format: str = "str") -> str:
        """
        Calculates the determinant of a square matrix.

        Raises:
            ValueError: If the matrix is not square.
        """
        mat = self.parse_matrix(matrix_input)
        if mat.rows != mat.cols:
            raise ValueError(
                f"Matrix must be square to compute determinant (got {mat.rows}x{mat.cols})."
            )
        det = mat.det()
        return self._format_expr(det, format=format)

    def inverse(self, matrix_input: Any, format: str = "str") -> str:
        """
        Computes the inverse of a square non-singular matrix.

        Raises:
            ValueError: If matrix is not square or is singular (det = 0).
        """
        mat = self.parse_matrix(matrix_input)
        if mat.rows != mat.cols:
            raise ValueError(
                f"Matrix must be square to compute inverse (got {mat.rows}x{mat.cols})."
            )
        det = mat.det()
        if det == 0:
            raise ValueError("Matrix is singular (determinant = 0) and cannot be inverted.")

        inv_mat = mat.inv()
        return self._format_expr(inv_mat, format=format)

    def rref(self, matrix_input: Any, format: str = "str") -> str:
        """
        Computes the Reduced Row Echelon Form (RREF) of a matrix.
        """
        mat = self.parse_matrix(matrix_input)
        rref_mat, pivots = mat.rref()

        if format == "latex":
            return f"\\text{{RREF}} = {sp.latex(rref_mat)}, \\quad \\text{{Pivots}} = {pivots}"
        if format == "pretty":
            return (
                f"RREF:\n{sp.pretty(rref_mat, use_unicode=True)}\nPivot columns: {list(pivots)}"
            )
        return f"RREF:\n{rref_mat}\nPivot columns: {list(pivots)}"

    def eigenvalues(self, matrix_input: Any, format: str = "str") -> str:
        """
        Calculates the eigenvalues and their algebraic multiplicities.

        Raises:
            ValueError: If matrix is not square.
        """
        mat = self.parse_matrix(matrix_input)
        if mat.rows != mat.cols:
            raise ValueError(
                f"Matrix must be square to compute eigenvalues (got {mat.rows}x{mat.cols})."
            )
        eigenvals = mat.eigenvals()

        if format == "latex":
            items = [
                f"\\lambda_{{{i + 1}}} = {sp.latex(val)} \\; (\\text{{mult: }} {mult})"
                for i, (val, mult) in enumerate(eigenvals.items())
            ]
            return ", \\quad ".join(items) if items else r"\emptyset"

        if format == "pretty":
            lines = [
                f"λ = {sp.pretty(val, use_unicode=True)} (multiplicity: {mult})"
                for val, mult in eigenvals.items()
            ]
            return "\n".join(lines)

        return str(eigenvals)

    def eigenvectors(self, matrix_input: Any, format: str = "str") -> str:
        """
        Calculates eigenvalues, multiplicities, and corresponding eigenvector bases.

        Raises:
            ValueError: If matrix is not square.
        """
        mat = self.parse_matrix(matrix_input)
        if mat.rows != mat.cols:
            raise ValueError(
                f"Matrix must be square to compute eigenvectors (got {mat.rows}x{mat.cols})."
            )
        eigenvects = mat.eigenvects()

        if format == "latex":
            parts = []
            for val, mult, basis in eigenvects:
                basis_latex = ", ".join(sp.latex(v) for v in basis)
                parts.append(
                    f"\\lambda = {sp.latex(val)} \\; (m={mult}): \\text{{span}}\\left\\{{ {basis_latex} \\right\\}}"
                )
            return "\\\\\n".join(parts)

        if format == "pretty":
            sections = []
            for val, mult, basis in eigenvects:
                v_str = "\n".join(sp.pretty(v, use_unicode=True) for v in basis)
                sections.append(
                    f"Eigenvalue λ = {sp.pretty(val, use_unicode=True)} (mult {mult}):\n{v_str}"
                )
            return "\n\n".join(sections)

        results = []
        for val, mult, basis in eigenvects:
            results.append(
                f"λ = {val} (mult {mult}), vectors: {[list(v) for v in basis]}"
            )
        return "\n".join(results)

    def rank(self, matrix_input: Any) -> int:
        """Calculates the rank of a matrix (dimension of column space)."""
        mat = self.parse_matrix(matrix_input)
        return int(mat.rank())

    def nullity(self, matrix_input: Any) -> int:
        """Calculates the nullity of a matrix (dimension of null space)."""
        mat = self.parse_matrix(matrix_input)
        return int(mat.cols - mat.rank())

    def trace(self, matrix_input: Any, format: str = "str") -> str:
        """
        Calculates the trace (sum of diagonal entries) of a square matrix.

        Raises:
            ValueError: If matrix is not square.
        """
        mat = self.parse_matrix(matrix_input)
        if mat.rows != mat.cols:
            raise ValueError(
                f"Matrix must be square to compute trace (got {mat.rows}x{mat.cols})."
            )
        tr = mat.trace()
        return self._format_expr(tr, format=format)

    def transpose(self, matrix_input: Any, format: str = "str") -> str:
        """Computes the transpose of a matrix."""
        mat = self.parse_matrix(matrix_input)
        t_mat = mat.T
        return self._format_expr(t_mat, format=format)

    def characteristic_polynomial(
        self, matrix_input: Any, var: str = "lambda", format: str = "str"
    ) -> str:
        """
        Computes the characteristic polynomial det(λI - A).

        Raises:
            ValueError: If matrix is not square.
        """
        mat = self.parse_matrix(matrix_input)
        if mat.rows != mat.cols:
            raise ValueError(
                f"Matrix must be square to compute characteristic polynomial (got {mat.rows}x{mat.cols})."
            )
        symbol = sp.Symbol(var)
        poly = mat.charpoly(symbol).as_expr()
        return self._format_expr(poly, format=format)
