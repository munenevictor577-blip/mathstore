from typing import Any

from fastapi import APIRouter, HTTPException, Query

from mathstore.api.schemas import (
    BinomialRequest,
    ConfidenceIntervalRequest,
    NormalRequest,
    PoissonRequest,
    StatsSummaryRequest,
    TTestRequest,
)
from mathstore.statistics.analyzer import StatsAnalyzer

router = APIRouter(prefix="/stats", tags=["Statistics & Probability"])
analyzer = StatsAnalyzer()


def _format_data_input(data: str | list[float]) -> str:
    if isinstance(data, list):
        return ", ".join(str(x) for x in data)
    return str(data)


@router.post("/summary", summary="Compute descriptive summary statistics")
def stats_summary(req: StatsSummaryRequest) -> dict[str, Any]:
    """Calculates five-number summary, mean, standard deviation, IQR, and distribution shape."""
    try:
        data_str = _format_data_input(req.data)
        res = analyzer.summary(data_str, format=req.format)
        return {
            "data": req.data,
            "format": req.format,
            "summary": res,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/normal", summary="Normal distribution PDF, CDF, and z-score")
def normal_dist_post(req: NormalRequest) -> dict[str, Any]:
    """Calculates normal distribution probability density, cumulative probability, and z-score."""
    try:
        pdf = analyzer.normal_pdf(req.x, req.mu, req.sigma)
        cdf = analyzer.normal_cdf(req.x, req.mu, req.sigma)
        z = analyzer.z_score(req.x, req.mu, req.sigma)
        return {
            "x": req.x,
            "mu": req.mu,
            "sigma": req.sigma,
            "z_score": z,
            "pdf": pdf,
            "cdf": cdf,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/normal", summary="Normal distribution (GET query)")
def normal_dist_get(
    x: float = Query(..., description="Value to evaluate"),
    mu: float = Query(0.0, description="Mean"),
    sigma: float = Query(1.0, gt=0, description="Standard deviation"),
) -> dict[str, Any]:
    return normal_dist_post(NormalRequest(x=x, mu=mu, sigma=sigma))


@router.post("/binomial", summary="Binomial distribution PMF and CDF")
def binomial_dist_post(req: BinomialRequest) -> dict[str, Any]:
    """Calculates binomial PMF: P(X = k) and CDF: P(X <= k)."""
    try:
        pmf = analyzer.binomial_pmf(req.k, req.n, req.p)
        cdf = analyzer.binomial_cdf(req.k, req.n, req.p)
        return {
            "k": req.k,
            "n": req.n,
            "p": req.p,
            "pmf": pmf,
            "cdf": cdf,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/binomial", summary="Binomial distribution (GET query)")
def binomial_dist_get(
    k: int = Query(..., ge=0, description="Number of successes"),
    n: int = Query(..., ge=1, description="Number of trials"),
    p: float = Query(..., ge=0.0, le=1.0, description="Success probability"),
) -> dict[str, Any]:
    return binomial_dist_post(BinomialRequest(k=k, n=n, p=p))


@router.post("/poisson", summary="Poisson distribution PMF and CDF")
def poisson_dist_post(req: PoissonRequest) -> dict[str, Any]:
    """Calculates Poisson PMF: P(X = k) and CDF: P(X <= k)."""
    try:
        pmf = analyzer.poisson_pmf(req.k, req.lam)
        cdf = analyzer.poisson_cdf(req.k, req.lam)
        return {
            "k": req.k,
            "lambda": req.lam,
            "pmf": pmf,
            "cdf": cdf,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/poisson", summary="Poisson distribution (GET query)")
def poisson_dist_get(
    k: int = Query(..., ge=0, description="Number of occurrences"),
    lam: float = Query(..., gt=0, description="Rate parameter lambda"),
) -> dict[str, Any]:
    return poisson_dist_post(PoissonRequest(k=k, lam=lam))


@router.post("/ci", summary="Confidence interval for sample mean")
def confidence_interval_post(req: ConfidenceIntervalRequest) -> dict[str, Any]:
    """Computes confidence interval for sample mean using Student's t distribution."""
    try:
        data_str = _format_data_input(req.data)
        res = analyzer.confidence_interval(data_str, confidence=req.confidence, format=req.format)
        if req.format == "str":
            lower, upper, margin = res
            return {
                "confidence": req.confidence,
                "lower_bound": lower,
                "upper_bound": upper,
                "margin_of_error": margin,
                "format": req.format,
            }
        return {
            "confidence": req.confidence,
            "result": res,
            "format": req.format,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/ttest", summary="One-sample Student's t-test")
def ttest_post(req: TTestRequest) -> dict[str, Any]:
    """Executes one-sample Student's t-test against a hypothesized population mean."""
    try:
        data_str = _format_data_input(req.data)
        res = analyzer.one_sample_t_test(
            data_str, req.pop_mean, alternative=req.alternative, format=req.format
        )
        return {
            "pop_mean": req.pop_mean,
            "alternative": req.alternative,
            "result": res,
            "format": req.format,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
