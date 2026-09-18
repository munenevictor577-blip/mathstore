"""Probability and statistics toolkit for university students."""

import math
from collections import Counter
from typing import Any

from sympy.stats import StudentT, cdf


class StatsAnalyzer:
    """Handles descriptive statistics, probability distributions, and hypothesis tests."""

    def parse_data(self, data_input: Any) -> list[float]:
        """
        Parses numeric dataset from lists, tuples, or formatted strings.

        Supported inputs:
          - list / tuple of numbers: [1, 2, 3, 4]
          - string of comma- or space-separated numbers: "1, 2, 3, 4" or "1.5 2.5 3.5"
          - stringified list: "[1, 2, 3, 4]"

        Raises:
            ValueError: If dataset is empty or values cannot be converted to floats.
        """
        if isinstance(data_input, (list, tuple)):
            if not data_input:
                raise ValueError("Dataset cannot be empty.")
            try:
                return [float(x) for x in data_input]
            except (ValueError, TypeError) as e:
                raise ValueError(f"All data points must be numeric: {e}")

        if isinstance(data_input, str):
            raw = data_input.strip()
            if not raw:
                raise ValueError("Dataset string cannot be empty.")
            # Remove enclosing brackets if present
            if raw.startswith("[") and raw.endswith("]"):
                raw = raw[1:-1].strip()

            cleaned = raw.replace(",", " ")
            tokens = cleaned.split()
            if not tokens:
                raise ValueError("Dataset contains no numeric values.")

            try:
                return [float(t) for t in tokens]
            except ValueError as e:
                raise ValueError(f"Failed to parse numeric value from '{data_input}': {e}")

        raise ValueError(f"Unsupported data input type: {type(data_input).__name__}")

    def mean(self, data_input: Any) -> float:
        """Calculates the sample mean."""
        data = self.parse_data(data_input)
        return sum(data) / len(data)

    def median(self, data_input: Any) -> float:
        """Calculates the median (50th percentile)."""
        data = sorted(self.parse_data(data_input))
        n = len(data)
        mid = n // 2
        if n % 2 == 1:
            return data[mid]
        return (data[mid - 1] + data[mid]) / 2.0

    def mode(self, data_input: Any) -> list[float]:
        """Calculates the mode(s) of the dataset."""
        data = self.parse_data(data_input)
        counts = Counter(data)
        max_freq = max(counts.values())
        return sorted([val for val, count in counts.items() if count == max_freq])

    def variance(self, data_input: Any, sample: bool = True) -> float:
        """
        Calculates variance.

        Args:
            data_input: Dataset.
            sample: True for sample variance (n-1 denominator), False for population variance (n).

        Raises:
            ValueError: If sample=True and sample size is less than 2.
        """
        data = self.parse_data(data_input)
        n = len(data)
        if sample and n < 2:
            raise ValueError("Sample variance requires at least 2 data points.")

        m = self.mean(data)
        sum_sq = sum((x - m) ** 2 for x in data)
        return sum_sq / (n - 1 if sample else n)

    def std_dev(self, data_input: Any, sample: bool = True) -> float:
        """Calculates standard deviation."""
        return math.sqrt(self.variance(data_input, sample=sample))

    def percentile(self, data_input: Any, p: float) -> float:
        """
        Computes the p-th percentile (0 <= p <= 100) using linear interpolation.
        """
        if not 0 <= p <= 100:
            raise ValueError("Percentile p must be between 0 and 100.")
        data = sorted(self.parse_data(data_input))
        n = len(data)
        if n == 1:
            return data[0]

        rank = (p / 100.0) * (n - 1)
        lower_idx = math.floor(rank)
        upper_idx = math.ceil(rank)
        fraction = rank - lower_idx

        if lower_idx == upper_idx:
            return data[lower_idx]
        return data[lower_idx] + fraction * (data[upper_idx] - data[lower_idx])

    def summary(self, data_input: Any, format: str = "str") -> dict[str, float] | str:
        """
        Generates comprehensive 5-number and distribution summary.

        Args:
            data_input: Dataset.
            format: 'str', 'latex', or 'pretty'.
        """
        data = sorted(self.parse_data(data_input))
        n = len(data)
        m = self.mean(data)
        var = self.variance(data) if n >= 2 else 0.0
        s = math.sqrt(var)
        q1 = self.percentile(data, 25)
        med = self.median(data)
        q3 = self.percentile(data, 75)
        iqr = q3 - q1

        stats_dict = {
            "count": float(n),
            "mean": round(m, 4),
            "std_dev": round(s, 4),
            "variance": round(var, 4),
            "min": round(data[0], 4),
            "q1": round(q1, 4),
            "median": round(med, 4),
            "q3": round(q3, 4),
            "max": round(data[-1], 4),
            "iqr": round(iqr, 4),
        }

        if format == "latex":
            return (
                "\\begin{tabular}{l|r}\n"
                "\\textbf{Statistic} & \\textbf{Value} \\\\\n"
                "\\hline\n"
                f"Sample Size ($n$) & {n} \\\\\n"
                f"Mean ($\\bar{{x}}$) & {stats_dict['mean']} \\\\\n"
                f"Std Dev ($s$) & {stats_dict['std_dev']} \\\\\n"
                f"Variance ($s^2$) & {stats_dict['variance']} \\\\\n"
                f"Min & {stats_dict['min']} \\\\\n"
                f"Q1 (25\\%) & {stats_dict['q1']} \\\\\n"
                f"Median ($Q2$) & {stats_dict['median']} \\\\\n"
                f"Q3 (75\\%) & {stats_dict['q3']} \\\\\n"
                f"Max & {stats_dict['max']} \\\\\n"
                f"IQR & {stats_dict['iqr']} \\\\\n"
                "\\end{tabular}"
            )

        if format == "pretty":
            return (
                "┌─────────────┬──────────┐\n"
                "│ Statistic   │ Value    │\n"
                "├─────────────┼──────────┤\n"
                f"│ Count (n)   │ {n:<8} │\n"
                f"│ Mean (x̄)    │ {stats_dict['mean']:<8} │\n"
                f"│ Std Dev (s) │ {stats_dict['std_dev']:<8} │\n"
                f"│ Variance    │ {stats_dict['variance']:<8} │\n"
                f"│ Min         │ {stats_dict['min']:<8} │\n"
                f"│ Q1 (25%)    │ {stats_dict['q1']:<8} │\n"
                f"│ Median      │ {stats_dict['median']:<8} │\n"
                f"│ Q3 (75%)    │ {stats_dict['q3']:<8} │\n"
                f"│ Max         │ {stats_dict['max']:<8} │\n"
                f"│ IQR         │ {stats_dict['iqr']:<8} │\n"
                "└─────────────┴──────────┘"
            )

        lines = [
            f"Count: {n}",
            f"Mean: {stats_dict['mean']}",
            f"Std Dev: {stats_dict['std_dev']}",
            f"Variance: {stats_dict['variance']}",
            f"Min: {stats_dict['min']}",
            f"Q1: {stats_dict['q1']}",
            f"Median: {stats_dict['median']}",
            f"Q3: {stats_dict['q3']}",
            f"Max: {stats_dict['max']}",
            f"IQR: {stats_dict['iqr']}",
        ]
        return "\n".join(lines)

    # --- Distributions ---

    def normal_pdf(self, x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Probability Density Function for Normal Distribution N(mu, sigma)."""
        if sigma <= 0:
            raise ValueError("Standard deviation sigma must be strictly positive.")
        coeff = 1.0 / (sigma * math.sqrt(2 * math.pi))
        exponent = -0.5 * ((x - mu) / sigma) ** 2
        return coeff * math.exp(exponent)

    def normal_cdf(self, x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Cumulative Distribution Function P(X <= x) for N(mu, sigma)."""
        if sigma <= 0:
            raise ValueError("Standard deviation sigma must be strictly positive.")
        z = (x - mu) / (sigma * math.sqrt(2.0))
        return 0.5 * (1.0 + math.erf(z))

    def z_score(self, x: float, mu: float, sigma: float) -> float:
        """Computes standardized z-score: (x - mu) / sigma."""
        if sigma <= 0:
            raise ValueError("Standard deviation sigma must be strictly positive.")
        return (x - mu) / sigma

    def binomial_pmf(self, k: int, n: int, p: float) -> float:
        """Probability Mass Function P(X = k) for Binomial(n, p)."""
        if n < 0 or k < 0:
            raise ValueError("n and k must be non-negative integers.")
        if k > n:
            return 0.0
        if not 0.0 <= p <= 1.0:
            raise ValueError("Probability p must be between 0 and 1.")
        coeff = math.comb(n, k)
        return float(coeff * (p ** k) * ((1.0 - p) ** (n - k)))

    def binomial_cdf(self, k: int, n: int, p: float) -> float:
        """Cumulative Distribution Function P(X <= k) for Binomial(n, p)."""
        if k < 0:
            return 0.0
        if k >= n:
            return 1.0
        return sum(self.binomial_pmf(i, n, p) for i in range(k + 1))

    def poisson_pmf(self, k: int, lambda_: float) -> float:
        """Probability Mass Function P(X = k) for Poisson(lambda)."""
        if k < 0:
            raise ValueError("k must be a non-negative integer.")
        if lambda_ <= 0:
            raise ValueError("Rate parameter lambda must be strictly positive.")
        return float((lambda_ ** k) * math.exp(-lambda_) / math.factorial(k))

    def poisson_cdf(self, k: int, lambda_: float) -> float:
        """Cumulative Distribution Function P(X <= k) for Poisson(lambda)."""
        if k < 0:
            return 0.0
        return sum(self.poisson_pmf(i, lambda_) for i in range(k + 1))

    # --- Inference & Hypothesis Testing ---

    def _t_critical(self, confidence: float, df: int) -> float:
        """Helper to find two-tailed t critical value t* using bisection."""
        target_p = 1.0 - (1.0 - confidence) / 2.0
        t_dist = StudentT("T", df)
        t_cdf = cdf(t_dist)

        low = 0.0
        high = 10.0
        while float(t_cdf(high)) < target_p and high < 1e6:
            low = high
            high *= 4.0

        for _ in range(40):
            mid = (low + high) / 2.0
            val = float(t_cdf(mid))
            if val < target_p:
                low = mid
            else:
                high = mid
        return (low + high) / 2.0

    def confidence_interval(
        self, data_input: Any, confidence: float = 0.95, format: str = "str"
    ) -> tuple[float, float, float] | str:
        """
        Calculates Student's t confidence interval for the population mean.

        Returns:
            (lower_bound, upper_bound, margin_of_error)
        """
        if not 0.0 < confidence < 1.0:
            raise ValueError("Confidence level must be between 0 and 1 (e.g. 0.95).")

        data = self.parse_data(data_input)
        n = len(data)
        if n < 2:
            raise ValueError("Confidence interval calculation requires at least 2 data points.")

        m = self.mean(data)
        s = self.std_dev(data)
        df = n - 1
        t_crit = self._t_critical(confidence, df)
        margin = t_crit * (s / math.sqrt(n))
        lower = m - margin
        upper = m + margin

        if format == "latex":
            pct = int(confidence * 100)
            return (
                f"{pct}\\% \\text{{ CI}}: \\; \\bar{{x}} \\pm E = "
                f"{m:.4f} \\pm {margin:.4f} = [{lower:.4f}, \\; {upper:.4f}]"
            )

        if format == "pretty":
            pct = int(confidence * 100)
            return (
                f"{pct}% CI: x̄ ± E = {m:.4f} ± {margin:.4f} = [{lower:.4f}, {upper:.4f}]"
            )

        return (round(lower, 4), round(upper, 4), round(margin, 4))

    def one_sample_t_test(
        self,
        data_input: Any,
        pop_mean: float,
        alternative: str = "two-sided",
        format: str = "str",
    ) -> dict[str, float] | str:
        """
        Performs one-sample Student's t-test comparing sample mean to pop_mean.

        Args:
            data_input: Dataset.
            pop_mean: Null hypothesis population mean mu_0.
            alternative: 'two-sided', 'greater', or 'less'.
            format: 'str', 'latex', or 'pretty'.
        """
        data = self.parse_data(data_input)
        n = len(data)
        if n < 2:
            raise ValueError("t-test requires at least 2 data points.")

        m = self.mean(data)
        s = self.std_dev(data)
        df = n - 1
        se = s / math.sqrt(n)
        if se == 0:
            if m == pop_mean:
                t_stat = 0.0
            else:
                raise ValueError(
                    "Sample variance is zero, but sample mean differs from hypothesized population mean; "
                    "t-statistic cannot be computed."
                )
        else:
            t_stat = (m - pop_mean) / se

        t_dist = StudentT("T", df)
        t_cdf = cdf(t_dist)
        t_prob = float(t_cdf(t_stat))

        if alternative == "two-sided":
            p_val = 2.0 * (1.0 - float(t_cdf(abs(t_stat))))
        elif alternative == "greater":
            p_val = 1.0 - t_prob
        elif alternative == "less":
            p_val = t_prob
        else:
            raise ValueError(
                f"Invalid alternative hypothesis '{alternative}'. Choose from 'two-sided', 'greater', 'less'."
            )

        results = {
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_val, 6),
            "df": float(df),
            "sample_mean": round(m, 4),
            "pop_mean": float(pop_mean),
        }

        if format == "latex":
            return (
                f"t = {results['t_statistic']}, \\quad p = {results['p_value']}, "
                f"\\quad df = {int(df)}, \\quad \\bar{{x}} = {results['sample_mean']}"
            )
        if format == "pretty":
            return (
                f"t-statistic: {results['t_statistic']}\n"
                f"p-value:     {results['p_value']}\n"
                f"Degrees of freedom: {int(df)}\n"
                f"Sample mean: {results['sample_mean']}"
            )

        return results

    def z_test(
        self,
        sample_mean: float,
        pop_mean: float,
        pop_std: float,
        n: int,
        alternative: str = "two-sided",
        format: str = "str",
    ) -> dict[str, float] | str:
        """
        Performs one-sample z-test given known population standard deviation.
        """
        if pop_std <= 0:
            raise ValueError("Population standard deviation must be positive.")
        if n <= 0:
            raise ValueError("Sample size n must be positive.")

        se = pop_std / math.sqrt(n)
        z_stat = (sample_mean - pop_mean) / se

        z_cdf = self.normal_cdf(z_stat, mu=0, sigma=1)
        if alternative == "two-sided":
            p_val = 2.0 * (1.0 - self.normal_cdf(abs(z_stat), mu=0, sigma=1))
        elif alternative == "greater":
            p_val = 1.0 - z_cdf
        elif alternative == "less":
            p_val = z_cdf
        else:
            raise ValueError(
                f"Invalid alternative hypothesis '{alternative}'. Choose from 'two-sided', 'greater', 'less'."
            )

        results = {
            "z_statistic": round(z_stat, 4),
            "p_value": round(p_val, 6),
            "sample_mean": round(sample_mean, 4),
            "pop_mean": float(pop_mean),
        }

        if format == "latex":
            return f"z = {results['z_statistic']}, \\quad p = {results['p_value']}"
        if format == "pretty":
            return f"z-statistic: {results['z_statistic']}\np-value:     {results['p_value']}"
        return results
