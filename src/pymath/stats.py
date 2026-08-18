"""Statistics and probability — the ClassWiz Statistics and Distribution modes."""

from __future__ import annotations

import math
from itertools import combinations, permutations

import numpy as np
import pandas as pd
from scipy import stats as _st


def describe(data) -> dict:
    """Every summary statistic a stats question asks for, in one call.

    Note ``sd_sample`` (divide by n-1) vs ``sd_population`` (divide by n) —
    the σ and s keys on a calculator. Use the sample version for sampled data.

    >>> round(describe([2, 4, 4, 4, 5, 5, 7, 9])["mean"], 3)
    5.0
    """
    arr = np.asarray(data, dtype=float)
    q1, q2, q3 = np.percentile(arr, [25, 50, 75])
    return {
        "n": arr.size,
        "sum": float(arr.sum()),
        "mean": float(arr.mean()),
        "median": float(q2),
        "mode": [float(m) for m in pd.Series(arr).mode().tolist()],
        "min": float(arr.min()),
        "max": float(arr.max()),
        "range": float(arr.max() - arr.min()),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "variance_sample": float(arr.var(ddof=1)) if arr.size > 1 else float("nan"),
        "variance_population": float(arr.var(ddof=0)),
        "sd_sample": float(arr.std(ddof=1)) if arr.size > 1 else float("nan"),
        "sd_population": float(arr.std(ddof=0)),
        "skew": float(_st.skew(arr)),
        "outliers": [float(v) for v in arr[(arr < q1 - 1.5 * (q3 - q1))
                                           | (arr > q3 + 1.5 * (q3 - q1))]],
    }


def frequency_table(data, bins: int | None = None) -> pd.DataFrame:
    """Frequency, relative frequency and cumulative frequency.

    Pass ``bins`` to group continuous data into class intervals.
    """
    s = pd.Series(data)
    grouped = s.value_counts().sort_index() if bins is None else \
        pd.cut(s, bins=bins).value_counts().sort_index()
    df = pd.DataFrame({"frequency": grouped})
    df["relative"] = df["frequency"] / df["frequency"].sum()
    df["cumulative"] = df["frequency"].cumsum()
    return df


def normal(mean=0.0, sd=1.0) -> dict:
    """A normal distribution with the calculator's P/Q/R functions attached.

    ``below(v)`` = P(X < v), ``above(v)`` = P(X > v), ``between(a, b)``,
    ``inverse(p)`` = the value with probability p below it.

    >>> n = normal(100, 15)
    >>> round(float(n["below"](115)), 4)
    0.8413
    """
    dist = _st.norm(loc=mean, scale=sd)
    return {
        "dist": dist,
        "mean": mean,
        "sd": sd,
        "pdf": dist.pdf,
        "below": dist.cdf,
        "above": dist.sf,
        "between": lambda lo, hi: float(dist.cdf(hi) - dist.cdf(lo)),
        "inverse": dist.ppf,
        "z": lambda v: (v - mean) / sd,
    }


def binomial(n: int, p: float) -> dict:
    """Binomial distribution: n independent trials, each with success chance p.

    >>> b = binomial(10, 0.5)
    >>> round(float(b["exactly"](5)), 4)
    0.2461
    """
    dist = _st.binom(n, p)
    return {
        "dist": dist,
        "mean": n * p,
        "variance": n * p * (1 - p),
        "sd": math.sqrt(n * p * (1 - p)),
        "exactly": dist.pmf,
        "at_most": dist.cdf,
        "at_least": lambda k: float(dist.sf(k - 1)),
        "inverse": dist.ppf,
    }


def poisson(rate: float) -> dict:
    """Poisson distribution: count of events in a fixed interval, mean = rate."""
    dist = _st.poisson(rate)
    return {
        "dist": dist,
        "mean": rate,
        "variance": rate,
        "sd": math.sqrt(rate),
        "exactly": dist.pmf,
        "at_most": dist.cdf,
        "at_least": lambda k: float(dist.sf(k - 1)),
    }


def regression(xs, ys, kind: str = "linear") -> dict:
    """Fit a model to paired data and report how well it fits.

    Kinds: linear, quadratic, cubic, exponential, logarithmic, power — the
    same menu as the calculator's regression mode.

    ``r`` is the correlation coefficient (linear only); ``r_squared`` is the
    fraction of variation the model explains.

    >>> round(regression([1, 2, 3], [2, 4, 6])["slope"], 6)
    2.0
    """
    X = np.asarray(xs, dtype=float)
    Y = np.asarray(ys, dtype=float)

    if kind == "linear":
        res = _st.linregress(X, Y)
        return {
            "kind": "linear",
            "slope": float(res.slope),
            "intercept": float(res.intercept),
            "equation": f"y = {res.slope:.6g}x + {res.intercept:.6g}",
            "r": float(res.rvalue),
            "r_squared": float(res.rvalue**2),
            "p_value": float(res.pvalue),
            "std_err": float(res.stderr),
            "predict": lambda v: res.slope * np.asarray(v, dtype=float) + res.intercept,
        }

    match kind:
        case "quadratic" | "cubic":
            degree = 2 if kind == "quadratic" else 3
            coeffs = np.polyfit(X, Y, degree)
            model = np.poly1d(coeffs)
            fitted = model(X)
            equation = str(model)
        case "exponential":  # y = a·e^(bx)  -> fit log y linearly
            b, log_a = np.polyfit(X, np.log(Y), 1)
            a = math.exp(log_a)
            def model(v, a=a, b=b):
                return a * np.exp(b * np.asarray(v, dtype=float))
            fitted = model(X)
            equation = f"y = {a:.6g}·e^({b:.6g}x)"
            coeffs = (a, b)
        case "logarithmic":  # y = a + b·ln x
            b, a = np.polyfit(np.log(X), Y, 1)
            def model(v, a=a, b=b):
                return a + b * np.log(np.asarray(v, dtype=float))
            fitted = model(X)
            equation = f"y = {a:.6g} + {b:.6g}·ln x"
            coeffs = (a, b)
        case "power":  # y = a·x^b
            b, log_a = np.polyfit(np.log(X), np.log(Y), 1)
            a = math.exp(log_a)
            def model(v, a=a, b=b):
                return a * np.asarray(v, dtype=float) ** b
            fitted = model(X)
            equation = f"y = {a:.6g}·x^{b:.6g}"
            coeffs = (a, b)
        case _:
            raise ValueError(f"unknown regression kind: {kind}")

    ss_res = float(((Y - fitted) ** 2).sum())
    ss_tot = float(((Y - Y.mean()) ** 2).sum())
    return {
        "kind": kind,
        "coefficients": coeffs,
        "equation": equation,
        "r_squared": 1 - ss_res / ss_tot if ss_tot else float("nan"),
        "predict": model,
    }


def correlation(xs, ys) -> dict:
    """Pearson (linear) and Spearman (rank) correlation with p-values."""
    pear = _st.pearsonr(xs, ys)
    spear = _st.spearmanr(xs, ys)
    return {
        "pearson_r": float(pear.statistic),
        "pearson_p": float(pear.pvalue),
        "spearman_r": float(spear.statistic),
        "spearman_p": float(spear.pvalue),
    }


def confidence_interval(data, confidence: float = 0.95) -> dict:
    """Confidence interval for the mean, using the t-distribution.

    >>> ci = confidence_interval([10, 12, 11, 13, 12])
    >>> round(ci["mean"], 2)
    11.6
    """
    arr = np.asarray(data, dtype=float)
    n = arr.size
    mean = float(arr.mean())
    sem = float(_st.sem(arr))
    margin = sem * _st.t.ppf((1 + confidence) / 2, n - 1)
    return {
        "mean": mean,
        "lower": mean - margin,
        "upper": mean + margin,
        "margin_of_error": float(margin),
        "confidence": confidence,
        "n": n,
    }


def hypothesis_test(sample_a, sample_b=None, popmean: float | None = None, paired: bool = False):
    """t-test: one-sample (give ``popmean``), two-sample, or paired.

    A small p-value (< 0.05 by convention) is evidence against the null
    hypothesis that the means are equal.
    """
    if sample_b is None:
        if popmean is None:
            raise ValueError("one-sample test needs popmean")
        res = _st.ttest_1samp(sample_a, popmean)
        kind = "one-sample"
    elif paired:
        res = _st.ttest_rel(sample_a, sample_b)
        kind = "paired"
    else:
        res = _st.ttest_ind(sample_a, sample_b)
        kind = "two-sample"
    return {
        "kind": kind,
        "t": float(res.statistic),
        "p_value": float(res.pvalue),
        "significant_at_5pct": bool(res.pvalue < 0.05),
    }


# --- counting ----------------------------------------------------------------

def nPr(n: int, r: int) -> int:
    """Permutations: ordered selections of r from n.

    >>> nPr(5, 2)
    20
    """
    return math.perm(n, r)


def nCr(n: int, r: int) -> int:
    """Combinations: unordered selections of r from n.

    >>> nCr(5, 2)
    10
    """
    return math.comb(n, r)


def factorial(n: int) -> int:
    """n! — the number of ways to order n things."""
    return math.factorial(n)


def list_permutations(items, r: int | None = None) -> list[tuple]:
    """Actually list the permutations, for small sets."""
    return list(permutations(items, r))


def list_combinations(items, r: int) -> list[tuple]:
    """Actually list the combinations, for small sets."""
    return list(combinations(items, r))


__all__ = [
    "binomial",
    "confidence_interval",
    "correlation",
    "describe",
    "factorial",
    "frequency_table",
    "hypothesis_test",
    "list_combinations",
    "list_permutations",
    "nCr",
    "nPr",
    "normal",
    "poisson",
    "regression",
]
