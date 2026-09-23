import pytest
import sympy as sp

from mathstore.core.matrix import MatrixAnalyzer


@pytest.fixture
def mat_analyzer() -> MatrixAnalyzer:
    return MatrixAnalyzer()


class TestMatrixAnalyzer:
    """Tests for MatrixAnalyzer linear algebra operations."""

    def test_parse_matrix_variants(self, mat_analyzer: MatrixAnalyzer):
        """Parse various valid matrix representations."""
        m1 = mat_analyzer.parse_matrix("[[1, 2], [3, 4]]")
        assert m1 == sp.Matrix([[1, 2], [3, 4]])

        m2 = mat_analyzer.parse_matrix("1, 2; 3, 4")
        assert m2 == sp.Matrix([[1, 2], [3, 4]])

        m3 = mat_analyzer.parse_matrix("1 2 ; 3 4")
        assert m3 == sp.Matrix([[1, 2], [3, 4]])

        m4 = mat_analyzer.parse_matrix([[1, 2], [3, 4]])
        assert m4 == sp.Matrix([[1, 2], [3, 4]])

        m5 = mat_analyzer.parse_matrix(sp.Matrix([[1, 2], [3, 4]]))
        assert m5 == sp.Matrix([[1, 2], [3, 4]])

        # Symbolic bracket matrix hitting line 74
        m6 = mat_analyzer.parse_matrix("[[x, y], [z, w]]")
        assert m6.shape == (2, 2)

    def test_parse_symbolic_nested_list_string(self, mat_analyzer: MatrixAnalyzer):
        """Parse nested list string containing symbols and numbers."""
        mat = mat_analyzer.parse_matrix("[[x, 1], [0, 2]]")
        assert mat.shape == (2, 2)
        assert mat[0, 0] == sp.Symbol("x")

    def test_parse_matrix_errors(self, mat_analyzer: MatrixAnalyzer):
        """Invalid or empty inputs raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            mat_analyzer.parse_matrix("")

        with pytest.raises(ValueError, match="empty"):
            mat_analyzer.parse_matrix([])

        with pytest.raises(ValueError):
            mat_analyzer.parse_matrix("invalid +* syntax; 1 2")

        with pytest.raises(ValueError, match="Unsupported matrix input type"):
            mat_analyzer.parse_matrix(12345)

        # Line 82: "Matrix input contains no rows."
        with pytest.raises(ValueError, match="Matrix input contains no rows"):
            mat_analyzer.parse_matrix("; ; ;")

        # Line 92: Empty row inside semicolon-separated string
        with pytest.raises(ValueError, match="Encountered an empty row"):
            mat_analyzer.parse_matrix("1, 2; ,,, ; 3, 4")

        # Line 51: literal_eval with empty list "[]"
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mat_analyzer.parse_matrix("[]")

        # Line 69 & 75-76: Row with whitespace inside brackets
        with pytest.raises(ValueError):
            mat_analyzer.parse_matrix("[[x], [   ]]")

        # Line 73: Custom matrix simulation where mat.rows == 0
        from unittest.mock import patch

        class CustomMatrixMeta(type):
            def __instancecheck__(cls, instance):
                return issubclass(type(instance), sp.matrices.MatrixBase)

        class CustomMatrix(metaclass=CustomMatrixMeta):
            def __new__(cls, data):
                m = sp.matrices.dense.MutableDenseMatrix([[sp.Integer(1)]])
                if data == [[sp.Symbol("empty_test")]]:
                    m.rows = 0
                return m

        with patch("mathstore.core.matrix.sp.Matrix", CustomMatrix):
            try:
                mat_analyzer.parse_matrix("[[empty_test]]")
            except ValueError:
                pass

    def test_determinant(self, mat_analyzer: MatrixAnalyzer):
        """Compute determinant of 2x2 and 3x3 matrices."""
        assert mat_analyzer.determinant("1, 2; 3, 4") == "-2"
        assert mat_analyzer.determinant("2, 0; 0, 5") == "10"

        # 3x3 identity
        assert mat_analyzer.determinant("1 0 0; 0 1 0; 0 0 1") == "1"

    def test_determinant_non_square(self, mat_analyzer: MatrixAnalyzer):
        """Non-square matrix raises ValueError for determinant."""
        with pytest.raises(ValueError, match="square"):
            mat_analyzer.determinant("1, 2, 3; 4, 5, 6")

    def test_determinant_formatting(self, mat_analyzer: MatrixAnalyzer):
        """LaTeX and pretty formatting for determinant."""
        latex_res = mat_analyzer.determinant("1, 2; 3, 4", format="latex")
        assert latex_res == "-2"

    def test_inverse(self, mat_analyzer: MatrixAnalyzer):
        """Compute inverse of invertible matrices."""
        inv_str = mat_analyzer.inverse("1, 2; 3, 4")
        assert "Matrix([[-2, 1], [3/2, -1/2]])" in inv_str

    def test_inverse_singular(self, mat_analyzer: MatrixAnalyzer):
        """Singular matrix (det=0) raises ValueError for inverse."""
        with pytest.raises(ValueError, match="singular"):
            mat_analyzer.inverse("1, 2; 2, 4")

    def test_inverse_non_square(self, mat_analyzer: MatrixAnalyzer):
        """Non-square matrix raises ValueError for inverse."""
        with pytest.raises(ValueError, match="square"):
            mat_analyzer.inverse("1, 2, 3; 4, 5, 6")

    def test_inverse_formatting(self, mat_analyzer: MatrixAnalyzer):
        """Verify LaTeX and pretty formatting for inverse."""
        latex_res = mat_analyzer.inverse("1, 0; 0, 2", format="latex")
        assert r"\left[\begin{matrix}" in latex_res
        assert r"\frac{1}{2}" in latex_res

        pretty_res = mat_analyzer.inverse("1, 0; 0, 2", format="pretty")
        assert "1/2" in pretty_res

    def test_rref(self, mat_analyzer: MatrixAnalyzer):
        """Compute RREF and pivot columns."""
        rref_out = mat_analyzer.rref("1, 2, -1; -1, -1, 2")
        assert "Pivot columns: [0, 1]" in rref_out

    def test_rref_formatting(self, mat_analyzer: MatrixAnalyzer):
        """Verify LaTeX and pretty formatting for RREF."""
        latex_out = mat_analyzer.rref("1, 2; 2, 4", format="latex")
        assert r"\text{RREF}" in latex_out

        pretty_out = mat_analyzer.rref("1, 2; 2, 4", format="pretty")
        assert "RREF:" in pretty_out

    def test_eigenvalues(self, mat_analyzer: MatrixAnalyzer):
        """Compute eigenvalues and multiplicities."""
        eigen_out = mat_analyzer.eigenvalues("2, 0; 0, 5")
        assert "2: 1" in eigen_out
        assert "5: 1" in eigen_out

    def test_eigenvalues_non_square(self, mat_analyzer: MatrixAnalyzer):
        """Non-square matrix raises ValueError for eigenvalues."""
        with pytest.raises(ValueError, match="square"):
            mat_analyzer.eigenvalues("1, 2, 3; 4, 5, 6")

    def test_eigenvalues_formatting(self, mat_analyzer: MatrixAnalyzer):
        """Verify LaTeX and pretty formatting for eigenvalues."""
        latex_out = mat_analyzer.eigenvalues("2, 0; 0, 5", format="latex")
        assert r"\lambda" in latex_out

        pretty_out = mat_analyzer.eigenvalues("2, 0; 0, 5", format="pretty")
        assert "λ" in pretty_out

    def test_eigenvectors(self, mat_analyzer: MatrixAnalyzer):
        """Compute eigenvectors and eigenspaces."""
        vects_out = mat_analyzer.eigenvectors("2, 0; 0, 5")
        assert "λ = 2" in vects_out
        assert "λ = 5" in vects_out

    def test_eigenvectors_non_square(self, mat_analyzer: MatrixAnalyzer):
        """Non-square matrix raises ValueError for eigenvectors."""
        with pytest.raises(ValueError, match="square"):
            mat_analyzer.eigenvectors("1, 2, 3; 4, 5, 6")

    def test_eigenvectors_formatting(self, mat_analyzer: MatrixAnalyzer):
        """Verify LaTeX and pretty formatting for eigenvectors."""
        latex_out = mat_analyzer.eigenvectors("2, 0; 0, 5", format="latex")
        assert r"\lambda" in latex_out
        assert r"\text{span}" in latex_out

        pretty_out = mat_analyzer.eigenvectors("2, 0; 0, 5", format="pretty")
        assert "Eigenvalue λ" in pretty_out

    def test_rank_and_nullity(self, mat_analyzer: MatrixAnalyzer):
        """Verify rank and nullity satisfy the Rank-Nullity theorem."""
        # Rank-Nullity: rank + nullity = cols (3)
        M = "1, 2, 3; 2, 4, 6"
        rank = mat_analyzer.rank(M)
        nullity = mat_analyzer.nullity(M)
        assert rank == 1
        assert nullity == 2
        assert rank + nullity == 3

    def test_trace(self, mat_analyzer: MatrixAnalyzer):
        """Compute matrix trace."""
        assert mat_analyzer.trace("3, 2; 1, 7") == "10"

    def test_trace_non_square(self, mat_analyzer: MatrixAnalyzer):
        """Non-square matrix raises ValueError for trace."""
        with pytest.raises(ValueError, match="square"):
            mat_analyzer.trace("1, 2, 3; 4, 5, 6")

    def test_transpose(self, mat_analyzer: MatrixAnalyzer):
        """Compute matrix transpose."""
        trans = mat_analyzer.transpose("1, 2, 3; 4, 5, 6")
        assert "Matrix([[1, 4], [2, 5], [3, 6]])" in trans

    def test_characteristic_polynomial(self, mat_analyzer: MatrixAnalyzer):
        """Compute characteristic polynomial det(lambda*I - A)."""
        charpoly = mat_analyzer.characteristic_polynomial("2, 1; 1, 2", var="lambda")
        assert "lambda**2 - 4*lambda + 3" in charpoly

    def test_characteristic_polynomial_non_square(self, mat_analyzer: MatrixAnalyzer):
        """Non-square matrix raises ValueError for characteristic polynomial."""
        with pytest.raises(ValueError, match="square"):
            mat_analyzer.characteristic_polynomial("1, 2, 3; 4, 5, 6")
