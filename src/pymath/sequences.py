"""Sequences, series and complex numbers."""

from __future__ import annotations

from itertools import pairwise

import sympy as sp

from .symbols import n, sym


def arithmetic(first, difference, terms: int = 10) -> dict:
    """Arithmetic sequence: add the same amount each time.

    ``Tn = a + (n-1)d`` and ``Sn = n/2 (2a + (n-1)d)``.

    >>> arithmetic(3, 5)["nth_term"]
    5*n - 2
    """
    a, d = sp.nsimplify(first), sp.nsimplify(difference)
    nth = sp.simplify(a + (n - 1) * d)
    return {
        "nth_term": nth,
        "sum_to_n": sp.simplify(n * (2 * a + (n - 1) * d) / 2),
        "first_terms": [sp.simplify(nth.subs(n, i)) for i in range(1, terms + 1)],
        "first": a,
        "difference": d,
    }


def geometric(first, ratio, terms: int = 10) -> dict:
    """Geometric sequence: multiply by the same amount each time.

    ``Tn = a·r^(n-1)``. The infinite sum exists only when |r| < 1.

    >>> geometric(1, sp.Rational(1, 2))["sum_to_infinity"]
    2
    """
    a, r = sp.nsimplify(first), sp.nsimplify(ratio)
    nth = sp.simplify(a * r ** (n - 1))
    converges = sp.Abs(r) < 1
    return {
        "nth_term": nth,
        "sum_to_n": sp.simplify(a * (1 - r**n) / (1 - r)) if r != 1 else a * n,
        "sum_to_infinity": sp.simplify(a / (1 - r)) if converges else None,
        "converges": bool(converges),
        "first_terms": [sp.simplify(nth.subs(n, i)) for i in range(1, terms + 1)],
        "first": a,
        "ratio": r,
    }


def from_terms(values: list) -> dict:
    """Work out the rule from the first few terms.

    Detects arithmetic and geometric patterns and falls back to fitting a
    polynomial through the terms.

    >>> from_terms([3, 8, 13, 18])["type"]
    'arithmetic'
    """
    vals = [sp.nsimplify(v) for v in values]
    if len(vals) < 3:
        raise ValueError("need at least 3 terms")

    diffs = [b - a for a, b in pairwise(vals)]
    if len(set(diffs)) == 1:
        return {"type": "arithmetic", **arithmetic(vals[0], diffs[0], len(vals))}

    if all(v != 0 for v in vals[:-1]):
        ratios = [sp.simplify(b / a) for a, b in pairwise(vals)]
        if len(set(ratios)) == 1:
            return {"type": "geometric", **geometric(vals[0], ratios[0], len(vals))}

    # Fit the lowest-degree polynomial that passes through every term.
    for degree in range(2, len(vals)):
        coeffs = sp.symbols(f"c0:{degree + 1}")
        poly = sum(c * n**i for i, c in enumerate(coeffs))
        eqs = [sp.Eq(poly.subs(n, i + 1), v) for i, v in enumerate(vals)]
        sol = sp.solve(eqs, coeffs, dict=True)
        if sol:
            fitted = sp.expand(poly.subs(sol[0]))
            if all(fitted.subs(n, i + 1) == v for i, v in enumerate(vals)):
                return {"type": f"polynomial (degree {degree})", "nth_term": fitted}

    return {"type": "unknown", "nth_term": None}


def recurrence(rule: str, initial: dict, terms: int = 10) -> list:
    """Generate terms from a recurrence like ``"2*T(n-1) + 1"``.

    ``initial`` maps index to value, e.g. ``{1: 3}``.

    >>> recurrence("2*T(n-1)", {1: 1}, terms=5)
    [1, 2, 4, 8, 16]
    """
    T = sp.Function("T")
    expr = sp.sympify(rule, locals={"T": T, "n": n})
    values = {int(k): sp.nsimplify(v) for k, v in initial.items()}
    start = max(values) + 1
    for idx in range(start, start + terms - len(values)):
        current = expr.subs(n, idx)
        current = current.replace(
            lambda node: isinstance(node, sp.Function) and node.func == T,
            lambda node: values[int(node.args[0])],
        )
        values[idx] = sp.simplify(current)
    return [values[i] for i in sorted(values)][:terms]


def limit_of_sequence(expr: str | sp.Expr, var: sp.Symbol = n):
    """Where a sequence heads as n → ∞.

    >>> limit_of_sequence("(2*n + 1)/n")
    2
    """
    return sp.limit(sym(expr), var, sp.oo)


def converges(expr: str | sp.Expr, var: sp.Symbol = n, start: int = 1) -> dict:
    """Does the infinite series Σ expr converge, and to what?

    >>> converges("1/2^n", start=0)["sum"]
    2
    """
    e = sym(expr)
    total = sp.summation(e, (var, start, sp.oo))
    is_finite = total.is_finite
    return {
        "sum": sp.simplify(total) if is_finite else sp.oo,
        "converges": bool(is_finite) if is_finite is not None else None,
        "term_limit": sp.limit(e, var, sp.oo),  # must be 0 to converge
    }


# --- complex numbers ---------------------------------------------------------

def complex_form(z) -> dict:
    """Every representation of a complex number at once.

    >>> complex_form(1 + sp.I)["modulus"]
    sqrt(2)
    """
    zz = sp.sympify(z)
    modulus = sp.simplify(sp.Abs(zz))
    argument = sp.simplify(sp.arg(zz))
    return {
        "cartesian": sp.simplify(zz),
        "real": sp.re(zz),
        "imaginary": sp.im(zz),
        "modulus": modulus,
        "argument_rad": argument,
        "argument_deg": sp.simplify(sp.deg(argument)),
        "polar": f"{modulus}·(cos({argument}) + i·sin({argument}))",
        "exponential": modulus * sp.exp(sp.I * argument),
        "conjugate": sp.conjugate(zz),
    }


def de_moivre(z, power) -> dict:
    """``(r·cis θ)^n = r^n·cis(nθ)`` — powers and roots of complex numbers.

    A fractional power gives one root; use :func:`roots_of_unity` for all of them.

    >>> de_moivre(sp.I, 2)["result"]
    -1
    """
    zz = sp.sympify(z)
    p = sp.nsimplify(power)
    result = sp.simplify(sp.expand(zz**p))
    return {"result": result, **complex_form(result)}


def roots_of_unity(k: int, of=1) -> list:
    """All k complex k-th roots of a number, evenly spaced around a circle.

    >>> len(roots_of_unity(3))
    3
    """
    target = sp.sympify(of)
    zsym = sp.Symbol("z")
    return sorted(sp.solve(sp.Eq(zsym**k, target), zsym), key=lambda s: (sp.arg(s), sp.Abs(s)))


__all__ = [
    "arithmetic",
    "complex_form",
    "converges",
    "de_moivre",
    "from_terms",
    "geometric",
    "limit_of_sequence",
    "recurrence",
    "roots_of_unity",
]
