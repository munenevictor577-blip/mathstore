import pytest
from fastapi.testclient import TestClient

from mathstore.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAPIHealthAndInfo:
    """Tests for root and health check endpoints."""

    def test_root_index(self, client: TestClient):
        res = client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "MathStore API"
        assert data["prefix"] == "/api/v1/math"

    def test_global_health(self, client: TestClient):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_math_prefix_health(self, client: TestClient):
        res = client.get("/api/v1/math/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["prefix"] == "/api/v1/math"


class TestCalculusAPI:
    """Tests for /api/v1/math calculus endpoints."""

    def test_diff_post(self, client: TestClient):
        payload = {"expression": "x**3 + 2*x", "variable": "x", "order": 1, "steps": True}
        res = client.post("/api/v1/math/diff", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["derivative"] == "3*x**2 + 2"
        assert data["steps"] is not None
        assert len(data["steps"]) >= 2

    def test_diff_get(self, client: TestClient):
        res = client.get("/api/v1/math/diff?expression=sin(x)&variable=x")
        assert res.status_code == 200
        assert res.json()["derivative"] == "cos(x)"

    def test_diff_error(self, client: TestClient):
        res = client.post("/api/v1/math/diff", json={"expression": "sin("})
        assert res.status_code == 400
        assert "Calculus error" in res.json()["detail"]

    def test_integrate_post_indefinite(self, client: TestClient):
        payload = {"expression": "x**2", "variable": "x", "steps": True}
        res = client.post("/api/v1/math/integrate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["integral"] == "x**3/3"
        assert data["steps"] is not None

    def test_integrate_post_definite(self, client: TestClient):
        payload = {"expression": "x", "variable": "x", "limits": [0.0, 2.0]}
        res = client.post("/api/v1/math/integrate", json=payload)
        assert res.status_code == 200
        assert float(res.json()["integral"]) == 2.0

    def test_integrate_get(self, client: TestClient):
        res = client.get("/api/v1/math/integrate?expression=x&lower_limit=0&upper_limit=2")
        assert res.status_code == 200
        assert float(res.json()["integral"]) == 2.0

    def test_integrate_error(self, client: TestClient):
        res = client.post("/api/v1/math/integrate", json={"expression": "x +* 2"})
        assert res.status_code == 400

    def test_limit_post(self, client: TestClient):
        payload = {"expression": "sin(x)/x", "target": "0", "variable": "x"}
        res = client.post("/api/v1/math/limit", json=payload)
        assert res.status_code == 200
        assert res.json()["limit"] == "1"

    def test_limit_get(self, client: TestClient):
        res = client.get("/api/v1/math/limit?expression=sin(x)/x&target=0")
        assert res.status_code == 200
        assert res.json()["limit"] == "1"

    def test_limit_error(self, client: TestClient):
        res = client.post("/api/v1/math/limit", json={"expression": "sin(", "target": "0"})
        assert res.status_code == 400


class TestAlgebraAPI:
    """Tests for /api/v1/math algebra endpoints."""

    def test_solve_post_linear(self, client: TestClient):
        payload = {"equation": "2*x + 4 = 10", "variable": "x", "steps": True}
        res = client.post("/api/v1/math/solve", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["solutions"] == ["3"]
        assert data["steps"] is not None

    def test_solve_get(self, client: TestClient):
        res = client.get("/api/v1/math/solve?equation=3*x - 9 = 0")
        assert res.status_code == 200
        assert res.json()["solutions"] == ["3"]

    def test_solve_error(self, client: TestClient):
        res = client.post("/api/v1/math/solve", json={"equation": "invalid"})
        assert res.status_code == 400

    def test_simplify_post(self, client: TestClient):
        payload = {"expression": "2*x + 3*x + 5"}
        res = client.post("/api/v1/math/simplify", json=payload)
        assert res.status_code == 200
        assert res.json()["simplified"] == "5*x + 5"

    def test_simplify_get(self, client: TestClient):
        res = client.get("/api/v1/math/simplify", params={"expression": "x**2 + x**2"})
        assert res.status_code == 200
        assert res.json()["simplified"] == "2*x**2"

    def test_simplify_error(self, client: TestClient):
        res = client.post("/api/v1/math/simplify", json={"expression": "x +* 2"})
        assert res.status_code == 400


class TestMatrixAPI:
    """Tests for /api/v1/math/matrix endpoints."""

    def test_matrix_det(self, client: TestClient):
        payload = {"matrix": "1, 2; 3, 4"}
        res = client.post("/api/v1/math/matrix/det", json=payload)
        assert res.status_code == 200
        assert res.json()["result"] == "-2"

    def test_matrix_inv(self, client: TestClient):
        payload = {"matrix": "1, 0; 0, 1"}
        res = client.post("/api/v1/math/matrix/inv", json=payload)
        assert res.status_code == 200
        assert "Matrix" in str(res.json()["result"])

    def test_matrix_rref(self, client: TestClient):
        payload = {"matrix": "2, 4; 1, 2"}
        res = client.post("/api/v1/math/matrix/rref", json=payload)
        assert res.status_code == 200
        assert res.json()["result"] is not None

    def test_matrix_rank_and_nullity(self, client: TestClient):
        payload = {"matrix": "1, 2; 2, 4"}
        res_rank = client.post("/api/v1/math/matrix/rank", json=payload)
        assert res_rank.status_code == 200
        assert res_rank.json()["result"] == 1

        res_null = client.post("/api/v1/math/matrix/nullity", json=payload)
        assert res_null.status_code == 200
        assert res_null.json()["result"] == 1

    def test_matrix_trace_and_transpose(self, client: TestClient):
        payload = {"matrix": "3, 1; 2, 5"}
        res_tr = client.post("/api/v1/math/matrix/trace", json=payload)
        assert res_tr.status_code == 200
        assert res_tr.json()["result"] == "8"

        res_tp = client.post("/api/v1/math/matrix/transpose", json=payload)
        assert res_tp.status_code == 200

    def test_matrix_eigen(self, client: TestClient):
        payload = {"matrix": "2, 0; 0, 3"}
        res = client.post("/api/v1/math/matrix/eigen", json=payload)
        assert res.status_code == 200
        assert "2" in str(res.json()["result"]) and "3" in str(res.json()["result"])

    def test_matrix_charpoly(self, client: TestClient):
        payload = {"matrix": "1, 2; 3, 4"}
        res = client.post("/api/v1/math/matrix/charpoly", json=payload)
        assert res.status_code == 200

    def test_matrix_unsupported_op(self, client: TestClient):
        payload = {"matrix": "1, 2; 3, 4"}
        res = client.post("/api/v1/math/matrix/nonexistent", json=payload)
        assert res.status_code == 400
        assert "Unsupported matrix operation" in res.json()["detail"]


class TestStatisticsAPI:
    """Tests for /api/v1/math/stats endpoints."""

    def test_stats_summary_list(self, client: TestClient):
        payload = {"data": [10.0, 12.0, 14.0, 15.0, 18.0]}
        res = client.post("/api/v1/math/stats/summary", json=payload)
        assert res.status_code == 200
        summary = res.json()["summary"]
        assert "Mean: 13.8" in summary

    def test_stats_summary_string(self, client: TestClient):
        payload = {"data": "10, 12, 14, 15, 18"}
        res = client.post("/api/v1/math/stats/summary", json=payload)
        assert res.status_code == 200
        assert "Mean: 13.8" in res.json()["summary"]

    def test_normal_distribution_post_and_get(self, client: TestClient):
        payload = {"x": 1.96, "mu": 0.0, "sigma": 1.0}
        res = client.post("/api/v1/math/stats/normal", json=payload)
        assert res.status_code == 200
        assert round(res.json()["cdf"], 4) == 0.975

        res_get = client.get("/api/v1/math/stats/normal?x=0&mu=0&sigma=1")
        assert res_get.status_code == 200
        assert res_get.json()["cdf"] == 0.5

    def test_binomial_distribution_post_and_get(self, client: TestClient):
        payload = {"k": 2, "n": 4, "p": 0.5}
        res = client.post("/api/v1/math/stats/binomial", json=payload)
        assert res.status_code == 200
        assert round(res.json()["pmf"], 4) == 0.375

        res_get = client.get("/api/v1/math/stats/binomial?k=2&n=4&p=0.5")
        assert res_get.status_code == 200

    def test_poisson_distribution_post_and_get(self, client: TestClient):
        payload = {"k": 1, "lam": 2.0}
        res = client.post("/api/v1/math/stats/poisson", json=payload)
        assert res.status_code == 200

        res_get = client.get("/api/v1/math/stats/poisson?k=1&lam=2.0")
        assert res_get.status_code == 200

    def test_confidence_interval_post(self, client: TestClient):
        payload = {"data": [22.0, 25.0, 27.0, 24.0, 26.0], "confidence": 0.95}
        res = client.post("/api/v1/math/stats/ci", json=payload)
        assert res.status_code == 200
        assert "lower_bound" in res.json()
        assert "upper_bound" in res.json()

    def test_ttest_post(self, client: TestClient):
        payload = {"data": [10.2, 9.8, 10.5, 10.1], "pop_mean": 10.0}
        res = client.post("/api/v1/math/stats/ttest", json=payload)
        assert res.status_code == 200
        assert "t_statistic" in res.json()["result"]


class TestStudyStepsAndPracticeAPI:
    """Tests for /api/v1/math steps, practice, and reference endpoints."""

    def test_steps_diff(self, client: TestClient):
        payload = {"expression": "x**2 * sin(x)", "variable": "x", "order": 1}
        res = client.post("/api/v1/math/steps/diff", json=payload)
        assert res.status_code == 200
        assert len(res.json()["steps"]) >= 3

        res_get = client.get("/api/v1/math/steps/diff?expression=x**2")
        assert res_get.status_code == 200

    def test_steps_integrate(self, client: TestClient):
        payload = {"expression": "x * exp(x)", "variable": "x"}
        res = client.post("/api/v1/math/steps/integrate", json=payload)
        assert res.status_code == 200
        assert len(res.json()["steps"]) >= 3

        res_get = client.get("/api/v1/math/steps/integrate?expression=x**2&lower_limit=0&upper_limit=2")
        assert res_get.status_code == 200

    def test_steps_solve(self, client: TestClient):
        payload = {"equation": "2*x + 4 = 10", "variable": "x"}
        res = client.post("/api/v1/math/steps/solve", json=payload)
        assert res.status_code == 200
        assert len(res.json()["steps"]) >= 4

        res_get = client.get("/api/v1/math/steps/solve?equation=3*x - 6 = 0")
        assert res_get.status_code == 200

    def test_practice_question_and_check(self, client: TestClient):
        # Generate question
        res = client.get("/api/v1/math/practice/question?topic=derivatives&seed=42")
        assert res.status_code == 200
        q = res.json()
        assert q["topic"] == "derivatives"
        assert q["prompt"]
        assert q["hint"]

        # Check correct answer
        check_payload = {
            "user_input": "2*cos(2*x)",
            "topic": q["topic"],
            "difficulty": q["difficulty"],
            "prompt": q["prompt"],
            "expected_answer": q["expected_answer"],
            "hint": q["hint"],
            "steps": q["steps"],
            "question_type": q["question_type"],
            "correct_value": "2*cos(2*x)",
            "variable": "x",
        }
        res_check = client.post("/api/v1/math/practice/check", json=check_payload)
        assert res_check.status_code == 200
        assert res_check.json()["is_correct"] is True

        # Check incorrect answer
        check_payload["user_input"] = "wrong"
        res_wrong = client.post("/api/v1/math/practice/check", json=check_payload)
        assert res_wrong.status_code == 200
        assert res_wrong.json()["is_correct"] is False

    def test_reference_list_and_get(self, client: TestClient):
        res_list = client.get("/api/v1/math/ref")
        assert res_list.status_code == 200
        topics = res_list.json()["topics"]
        assert "derivatives" in topics

        res_get = client.get("/api/v1/math/ref/derivatives")
        assert res_get.status_code == 200
        assert "Derivatives" in res_get.json()["content"]

        res_404 = client.get("/api/v1/math/ref/nonexistent_topic")
        assert res_404.status_code == 404
