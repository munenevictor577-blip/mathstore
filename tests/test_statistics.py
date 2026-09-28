import math

import pytest

from mathstore.statistics.analyzer import StatsAnalyzer


@pytest.fixture
def stats() -> StatsAnalyzer:
    return StatsAnalyzer()


class TestStatsAnalyzer:
    """Tests for StatsAnalyzer probability, descriptive statistics, and inference."""

    def test_parse_data_variants(self, stats: StatsAnalyzer):
        """Parse various valid data representations."""
        assert stats.parse_data([1, 2, 3]) == [1.0, 2.0, 3.0]
        assert stats.parse_data((4, 5, 6)) == [4.0, 5.0, 6.0]
        assert stats.parse_data("1, 2, 3") == [1.0, 2.0, 3.0]
        assert stats.parse_data("10 20 30") == [10.0, 20.0, 30.0]
        assert stats.parse_data("[1.5, 2.5]") == [1.5, 2.5]

    def test_parse_data_errors(self, stats: StatsAnalyzer):
        """Empty or non-numeric inputs raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            stats.parse_data([])
        with pytest.raises(ValueError, match="empty"):
            stats.parse_data("")
        with pytest.raises(ValueError):
            stats.parse_data("a, b, c")
        with pytest.raises(ValueError, match="Unsupported data input type"):
            stats.parse_data(12345)
        # Lines 30-31: Non-numeric elements in list/tuple
        with pytest.raises(ValueError, match="All data points must be numeric"):
            stats.parse_data([1, "non_numeric", 3])
        # Line 44: String containing brackets or delimiters but no numbers
        with pytest.raises(ValueError, match="Dataset contains no numeric values"):
            stats.parse_data("[   ]")
        with pytest.raises(ValueError, match="Dataset contains no numeric values"):
            stats.parse_data("   , , ,   ")

    def test_mean(self, stats: StatsAnalyzer):
        """Compute arithmetic mean."""
        assert stats.mean([2, 4, 6, 8]) == 5.0
        assert stats.mean("10, 20, 30") == 20.0

    def test_median(self, stats: StatsAnalyzer):
        """Compute median for odd and even datasets."""
        assert stats.median([1, 3, 5]) == 3.0
        assert stats.median([1, 2, 3, 4]) == 2.5

    def test_mode(self, stats: StatsAnalyzer):
        """Compute unimodal and multimodal datasets."""
        assert stats.mode([1, 2, 2, 3]) == [2.0]
        assert stats.mode([1, 1, 2, 2, 3]) == [1.0, 2.0]

    def test_variance_and_std_dev(self, stats: StatsAnalyzer):
        """Compute sample and population variance and standard deviation."""
        data = [2, 4, 4, 4, 5, 5, 7, 9]
        # Population variance: 4.0
        assert stats.variance(data, sample=False) == 4.0
        assert stats.std_dev(data, sample=False) == 2.0

        # Sample variance
        assert stats.variance([1, 2, 3], sample=True) == 1.0
        assert stats.std_dev([1, 2, 3], sample=True) == 1.0

        # Sample size < 2 raises error for sample variance
        with pytest.raises(ValueError, match="at least 2"):
            stats.variance([5], sample=True)

    def test_percentile(self, stats: StatsAnalyzer):
        """Compute percentiles with linear interpolation."""
        data = [10, 20, 30, 40, 50]
        assert stats.percentile(data, 0) == 10.0
        assert stats.percentile(data, 50) == 30.0
        assert stats.percentile(data, 100) == 50.0
        assert stats.percentile(data, 25) == 20.0
        assert stats.percentile(data, 75) == 40.0

        # Single value
        assert stats.percentile([42], 50) == 42.0

        with pytest.raises(ValueError, match="between 0 and 100"):
            stats.percentile(data, 105)

    def test_summary_formats(self, stats: StatsAnalyzer):
        """Generate statistical summary in str, latex, and pretty formats."""
        data = [10, 12, 14, 15, 18, 20, 22]
        summary_str = stats.summary(data, format="str")
        assert "Mean:" in summary_str
        assert "IQR:" in summary_str

        summary_latex = stats.summary(data, format="latex")
        assert r"\begin{tabular}" in summary_latex
        assert r"\textbf{Statistic}" in summary_latex

        summary_pretty = stats.summary(data, format="pretty")
        assert "┌─────────────┬──────────┐" in summary_pretty
        assert "Mean" in summary_pretty

    def test_normal_pdf_and_cdf(self, stats: StatsAnalyzer):
        """Evaluate standard normal distribution PDF, CDF, and z-scores."""
        # Standard normal peak at x=0
        peak = stats.normal_pdf(0, mu=0, sigma=1)
        assert math.isclose(peak, 1.0 / math.sqrt(2 * math.pi), rel_tol=1e-5)

        # Standard normal CDF at 0 is 0.5
        assert math.isclose(stats.normal_cdf(0, mu=0, sigma=1), 0.5, rel_tol=1e-5)

        # 95% within ~1.96 std devs
        p_val = stats.normal_cdf(1.96, mu=0, sigma=1)
        assert math.isclose(p_val, 0.975, rel_tol=1e-3)

        # z-score
        assert stats.z_score(115, mu=100, sigma=15) == 1.0

        with pytest.raises(ValueError, match="positive"):
            stats.normal_pdf(0, mu=0, sigma=0)
        with pytest.raises(ValueError, match="positive"):
            stats.normal_cdf(0, mu=0, sigma=-1)
        with pytest.raises(ValueError, match="positive"):
            stats.z_score(0, mu=0, sigma=0)

    def test_binomial_pmf_and_cdf(self, stats: StatsAnalyzer):
        """Evaluate Binomial distribution PMF and CDF."""
        # Flip coin 4 times: P(2 heads) = 6/16 = 0.375
        assert math.isclose(stats.binomial_pmf(2, 4, 0.5), 0.375, rel_tol=1e-5)
        assert math.isclose(stats.binomial_cdf(4, 4, 0.5), 1.0, rel_tol=1e-5)
        assert 0.0 < stats.binomial_cdf(2, 4, 0.5) < 1.0
        assert stats.binomial_pmf(5, 4, 0.5) == 0.0
        assert stats.binomial_cdf(-1, 4, 0.5) == 0.0

        with pytest.raises(ValueError, match="between 0 and 1"):
            stats.binomial_pmf(2, 4, 1.5)
        with pytest.raises(ValueError, match="non-negative"):
            stats.binomial_pmf(-1, 4, 0.5)

    def test_poisson_pmf_and_cdf(self, stats: StatsAnalyzer):
        """Evaluate Poisson distribution PMF and CDF."""
        # lambda = 2, P(X = 0) = e^(-2)
        expected_0 = math.exp(-2)
        assert math.isclose(stats.poisson_pmf(0, 2.0), expected_0, rel_tol=1e-5)
        assert 0.0 < stats.poisson_cdf(2, 2.0) < 1.0
        assert stats.poisson_cdf(-1, 2.0) == 0.0

        with pytest.raises(ValueError, match="positive"):
            stats.poisson_pmf(0, -1.0)
        with pytest.raises(ValueError, match="non-negative"):
            stats.poisson_pmf(-2, 2.0)

    def test_confidence_interval(self, stats: StatsAnalyzer):
        """Compute confidence intervals for sample mean."""
        data = [10, 12, 11, 14, 13]
        lower, upper, margin = stats.confidence_interval(data, confidence=0.95)
        assert lower < 12.0 < upper
        assert math.isclose(12.0 - lower, margin, rel_tol=1e-3)

        # Formatting
        ci_latex = stats.confidence_interval(data, confidence=0.95, format="latex")
        assert r"95\% \text{ CI}" in ci_latex

        ci_pretty = stats.confidence_interval(data, confidence=0.95, format="pretty")
        assert "95% CI:" in ci_pretty

        # High confidence hitting bisection expansion (lines 266-267)
        ci_high = stats.confidence_interval([1.0, 2.0], confidence=0.99999)
        assert ci_high[0] < ci_high[1]

        with pytest.raises(ValueError, match="between 0 and 1"):
            stats.confidence_interval(data, confidence=1.5)
        with pytest.raises(ValueError, match="at least 2"):
            stats.confidence_interval([5], confidence=0.95)

    def test_t_critical_adaptive_small_df(self, stats: StatsAnalyzer):
        """Verify numerical accuracy in t-critical for small df and high confidence."""
        # df = 1, 99.9% confidence has true t* ~ 636.62
        t_crit = stats._t_critical(0.999, df=1)
        assert t_crit > 600.0
        assert abs(t_crit - 636.62) < 1.0

    def test_one_sample_t_test(self, stats: StatsAnalyzer):
        """Perform one-sample Student's t-test."""
        data = [10.2, 9.8, 10.5, 10.1, 9.9, 10.3]
        res = stats.one_sample_t_test(data, pop_mean=10.0, alternative="two-sided")
        assert "t_statistic" in res
        assert 0.0 <= res["p_value"] <= 1.0

        # Greater and less alternatives
        res_gt = stats.one_sample_t_test(data, pop_mean=10.0, alternative="greater")
        assert 0.0 <= res_gt["p_value"] <= 1.0

        res_lt = stats.one_sample_t_test(data, pop_mean=10.0, alternative="less")
        assert 0.0 <= res_lt["p_value"] <= 1.0

        # Zero variance: sample mean matches hypothesized mean (lines 344-345)
        res_zero_var = stats.one_sample_t_test([5.0, 5.0, 5.0], pop_mean=5.0)
        assert res_zero_var["t_statistic"] == 0.0

        # Zero variance: sample mean differs (lines 347-350)
        with pytest.raises(ValueError, match="Sample variance is zero"):
            stats.one_sample_t_test([5.0, 5.0, 5.0], pop_mean=10.0)

        # Formatting
        latex_out = stats.one_sample_t_test(data, pop_mean=10.0, format="latex")
        assert r"\bar{x}" in latex_out

        pretty_out = stats.one_sample_t_test(data, pop_mean=10.0, format="pretty")
        assert "t-statistic:" in pretty_out

        with pytest.raises(ValueError, match="Invalid alternative"):
            stats.one_sample_t_test(data, pop_mean=10.0, alternative="unknown")
        with pytest.raises(ValueError, match="at least 2"):
            stats.one_sample_t_test([10], pop_mean=10.0)

    def test_z_test(self, stats: StatsAnalyzer):
        """Perform one-sample z-test."""
        res = stats.z_test(sample_mean=105, pop_mean=100, pop_std=15, n=36)
        assert "z_statistic" in res
        assert math.isclose(res["z_statistic"], 2.0, rel_tol=1e-3)
        assert res["p_value"] < 0.05

        # Greater and less alternatives
        res_gt = stats.z_test(105, 100, 15, 36, alternative="greater")
        assert math.isclose(res_gt["p_value"], 0.02275, rel_tol=1e-2)

        res_lt = stats.z_test(105, 100, 15, 36, alternative="less")
        assert math.isclose(res_lt["p_value"], 1.0 - 0.02275, rel_tol=1e-2)

        # Formatting
        latex_out = stats.z_test(105, 100, 15, 36, format="latex")
        assert "z =" in latex_out

        pretty_out = stats.z_test(105, 100, 15, 36, format="pretty")
        assert "z-statistic:" in pretty_out

        with pytest.raises(ValueError, match="positive"):
            stats.z_test(100, 100, -5, 10)
        with pytest.raises(ValueError, match="positive"):
            stats.z_test(100, 100, 5, 0)
        with pytest.raises(ValueError, match="Invalid alternative"):
            stats.z_test(100, 100, 5, 10, alternative="unknown")
