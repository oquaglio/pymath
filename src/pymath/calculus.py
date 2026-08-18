"""Calculus: limits, derivatives, integrals, series and differential equations.

Symbolic where possible (SymPy), numeric where it must be (SciPy).
"""

from __future__ import annotations

from itertools import pairwise

import sympy as sp
from scipy import integrate as _spi
from scipy import optimize as _spo

from .symbols import equation, func, sym, x


def limit(expr: str | sp.Expr, var: sp.Symbol = x, to=0, direction: str = "+-"):
    """Limit of an expression as ``var`` approaches ``to``.

    ``direction`` is ``"+"`` (from above), ``"-"`` (from below), or ``"+-"``
    (two-sided — returns the value only if both sides agree).

    >>> limit("sin(x)/x", to=0)
    1
    >>> limit("1/x", to=0, direction="+")
    oo
    """
    e = sym(expr)
    point = sp.oo if to in ("oo", "inf") else sp.nsimplify(to)
    if direction == "+-":
        left = sp.limit(e, var, point, "-")
        right = sp.limit(e, var, point, "+")
        return right if left == right else sp.nan
    return sp.limit(e, var, point, direction)


def diff(expr: str | sp.Expr, var: sp.Symbol = x, order: int = 1) -> sp.Expr:
    """Differentiate. ``order=2`` gives the second derivative, and so on.

    >>> diff("x^3 + 2x")
    3*x**2 + 2
    >>> diff("sin(x)", order=2)
    -sin(x)
    """
    return sp.simplify(sp.diff(sym(expr), var, order))


def gradient_at(expr: str | sp.Expr, point: float, var: sp.Symbol = x):
    """Value of the derivative at a point — the gradient of the tangent there.

    >>> gradient_at("x^2", 3)
    6
    """
    return sp.simplify(sp.diff(sym(expr), var).subs(var, sp.nsimplify(point)))


def tangent(expr: str | sp.Expr, point: float, var: sp.Symbol = x) -> sp.Expr:
    """Equation of the tangent line at ``x = point`` (returned as ``y = ...``).

    >>> tangent("x^2", 3)
    6*x - 9
    """
    e = sym(expr)
    p = sp.nsimplify(point)
    y0 = e.subs(var, p)
    m = sp.diff(e, var).subs(var, p)
    return sp.simplify(m * (var - p) + y0)


def normal(expr: str | sp.Expr, point: float, var: sp.Symbol = x) -> sp.Expr:
    """Equation of the normal (perpendicular to the tangent) at ``x = point``."""
    e = sym(expr)
    p = sp.nsimplify(point)
    y0 = e.subs(var, p)
    m = sp.diff(e, var).subs(var, p)
    if m == 0:
        raise ValueError(f"tangent is horizontal, so the normal is the vertical line x = {p}")
    return sp.simplify(-1 / m * (var - p) + y0)


def integrate(expr: str | sp.Expr, var: sp.Symbol = x, lower=None, upper=None):
    """Indefinite integral (no bounds) or definite integral (with bounds).

    The ``+ C`` on an indefinite integral is left off, as SymPy does.

    >>> integrate("x^2")
    x**3/3
    >>> integrate("x^2", lower=0, upper=3)
    9
    """
    e = sym(expr)
    if lower is None and upper is None:
        return sp.simplify(sp.integrate(e, var))
    return sp.simplify(sp.integrate(e, (var, _bound(lower), _bound(upper))))


def _bound(value):
    """Read a bound, accepting ``"oo"`` / ``"-oo"`` for infinity."""
    if isinstance(value, str):
        text = value.strip().lower()
        if text in ("oo", "inf", "+oo", "+inf"):
            return sp.oo
        if text in ("-oo", "-inf"):
            return -sp.oo
    return sp.nsimplify(value)


def stationary_points(expr: str | sp.Expr, var: sp.Symbol = x) -> list[dict]:
    """Find and classify stationary points (where f'(x) = 0).

    Uses the second derivative test: f'' > 0 → minimum, f'' < 0 → maximum,
    f'' = 0 → check the sign of f' on either side (a possible inflection).

    >>> [(p["x"], p["nature"]) for p in stationary_points("x^3 - 3x")]
    [(-1, 'maximum'), (1, 'minimum')]
    """
    e = sym(expr)
    d1, d2 = sp.diff(e, var), sp.diff(e, var, 2)
    points = []
    for crit in sorted(sp.solve(sp.Eq(d1, 0), var), key=lambda s: (sp.re(s), sp.im(s))):
        if not crit.is_real:
            continue
        curvature = sp.simplify(d2.subs(var, crit))
        if curvature.is_positive:
            nature = "minimum"
        elif curvature.is_negative:
            nature = "maximum"
        else:
            h = sp.Rational(1, 100)
            before = sp.sign(d1.subs(var, crit - h))
            after = sp.sign(d1.subs(var, crit + h))
            nature = "inflection" if before == after else (
                "maximum" if before > after else "minimum"
            )
        points.append(
            {"x": crit, "y": sp.simplify(e.subs(var, crit)), "nature": nature, "f''": curvature}
        )
    return points


def inflection_points(expr: str | sp.Expr, var: sp.Symbol = x) -> list[dict]:
    """Points where concavity changes (f'' = 0 *and* the sign actually flips).

    >>> [p["x"] for p in inflection_points("x^3")]
    [0]
    """
    e = sym(expr)
    d2 = sp.diff(e, var, 2)
    out = []
    for cand in sorted(sp.solve(sp.Eq(d2, 0), var), key=lambda s: (sp.re(s), sp.im(s))):
        if not cand.is_real:
            continue
        h = sp.Rational(1, 100)
        if sp.sign(d2.subs(var, cand - h)) != sp.sign(d2.subs(var, cand + h)):
            out.append({"x": cand, "y": sp.simplify(e.subs(var, cand))})
    return out


def analyse(expr: str | sp.Expr, var: sp.Symbol = x) -> dict:
    """Full curve sketch: intercepts, turning points, asymptotes, end behaviour.

    This is the checklist a Year 12 "sketch the graph of f" question wants.
    """
    e = sym(expr)
    return {
        "expression": e,
        "f'": sp.simplify(sp.diff(e, var)),
        "f''": sp.simplify(sp.diff(e, var, 2)),
        "y_intercept": sp.simplify(e.subs(var, 0)) if e.subs(var, 0).is_finite else None,
        "x_intercepts": [s for s in sp.solve(sp.Eq(e, 0), var) if s.is_real],
        "stationary_points": stationary_points(e, var),
        "inflection_points": inflection_points(e, var),
        "vertical_asymptotes": _vertical_asymptotes(e, var),
        "horizontal_asymptotes": _horizontal_asymptotes(e, var),
        "domain": sp.calculus.util.continuous_domain(e, var, sp.S.Reals),
    }


def _vertical_asymptotes(e: sp.Expr, var: sp.Symbol) -> list:
    denom = sp.denom(sp.together(e))
    if denom.has(var):
        return [s for s in sp.solve(sp.Eq(denom, 0), var) if s.is_real]
    return []


def _horizontal_asymptotes(e: sp.Expr, var: sp.Symbol) -> list:
    out = []
    for direction in (sp.oo, -sp.oo):
        lim = sp.limit(e, var, direction)
        if lim.is_finite:
            out.append(lim)
    return sorted(set(out), key=str)


def taylor(expr: str | sp.Expr, var: sp.Symbol = x, about=0, order: int = 6) -> sp.Expr:
    """Taylor/Maclaurin polynomial — a polynomial that hugs the curve near a point.

    ``about=0`` gives the Maclaurin series.

    >>> taylor("exp(x)", order=4)
    x**3/6 + x**2/2 + x + 1
    """
    return sp.series(sym(expr), var, sp.nsimplify(about), order).removeO()


def series_sum(expr: str | sp.Expr, var: sp.Symbol, lower, upper):
    """Evaluate a sigma-notation sum, including infinite ones.

    >>> from .symbols import n
    >>> series_sum("1/2^n", n, 0, "oo")
    2
    """
    hi = sp.oo if upper in ("oo", "inf") else sp.nsimplify(upper)
    return sp.simplify(sp.summation(sym(expr), (var, sp.nsimplify(lower), hi)))


def area_between(f1: str | sp.Expr, f2: str | sp.Expr, lower=None, upper=None, var=x):
    """Area enclosed between two curves.

    With no bounds, the curves' intersection points are used. The absolute
    difference is integrated, so it works when the curves cross.

    >>> area_between("x", "x^2")
    1/6
    """
    a_expr, b_expr = sym(f1), sym(f2)
    crossings = sorted(
        [s for s in sp.solve(sp.Eq(a_expr, b_expr), var) if s.is_real],
        key=lambda s: float(s),
    )
    if lower is None or upper is None:
        if len(crossings) < 2:
            raise ValueError("curves meet fewer than twice; pass explicit bounds")
        lower, upper = crossings[0], crossings[-1]
    lo, hi = _bound(lower), _bound(upper)

    # SymPy won't integrate Abs(...) directly, so split at every crossing inside
    # the range and add the magnitude of each piece. That handles curves that
    # swap over partway through.
    cuts = [lo, *[c for c in crossings if lo < c < hi], hi]
    total = sum(
        sp.Abs(sp.integrate(a_expr - b_expr, (var, left, right)))
        for left, right in pairwise(cuts)
    )
    return sp.simplify(total)


def volume_of_revolution(expr: str | sp.Expr, lower, upper, axis: str = "x", var=x):
    """Volume swept when a curve is rotated about an axis (disc method).

    About x: ``V = pi * ∫ y^2 dx``. About y: ``V = 2*pi * ∫ x*y dx`` (shells).

    >>> volume_of_revolution("x", 0, 1)
    pi/3
    """
    e = sym(expr)
    lo, hi = sp.nsimplify(lower), sp.nsimplify(upper)
    if axis == "x":
        return sp.simplify(sp.pi * sp.integrate(e**2, (var, lo, hi)))
    return sp.simplify(2 * sp.pi * sp.integrate(var * e, (var, lo, hi)))


def arc_length(expr: str | sp.Expr, lower, upper, var: sp.Symbol = x):
    """Length of a curve: ``∫ sqrt(1 + (dy/dx)^2) dx``."""
    e = sym(expr)
    integrand = sp.sqrt(1 + sp.diff(e, var) ** 2)
    return sp.simplify(sp.integrate(integrand, (var, sp.nsimplify(lower), sp.nsimplify(upper))))


def solve_ode(eq: str | sp.Expr, dependent: str = "y", independent: sp.Symbol = x):
    """Solve a differential equation.

    Write derivatives with `Derivative`, e.g. ``"Derivative(y(x), x) = y(x)"``.

    >>> solve_ode("Derivative(y(x), x) - y(x) = 0")
    Eq(y(x), C1*exp(x))
    """
    f = sp.Function(dependent)
    local = {dependent: f, str(independent): independent}
    if isinstance(eq, sp.Basic):
        parsed = eq
    elif "=" in str(eq):
        lhs, rhs = str(eq).split("=", 1)
        parsed = sp.Eq(sp.sympify(lhs, locals=local), sp.sympify(rhs, locals=local))
    else:
        parsed = sp.sympify(str(eq), locals=local)
    return sp.dsolve(parsed, f(independent))


# --- numeric fallbacks: when SymPy can't find a closed form -------------------

def nintegrate(expr: str | sp.Expr, lower: float, upper: float, var: sp.Symbol = x) -> float:
    """Numeric definite integral (SciPy quadrature). Always returns a float.

    Use this when the integral has no elementary antiderivative, e.g. e^(-x^2).

    >>> round(nintegrate("exp(-x^2)", -5, 5), 6)
    1.772454
    """
    f = func(expr, var)
    value, _err = _spi.quad(f, float(lower), float(upper))
    return value


def nderivative(expr: str | sp.Expr, point: float, var: sp.Symbol = x, h: float = 1e-6) -> float:
    """Numeric derivative via a central difference — what a physical calculator does.

    >>> round(nderivative("x^2", 3), 6)
    6.0
    """
    f = func(expr, var)
    return (f(point + h) - f(point - h)) / (2 * h)


def nsolve(eq: str | sp.Expr, guess: float = 0.0, var: sp.Symbol = x) -> float:
    """Numeric root near ``guess`` (Newton-style), for equations with no exact form.

    >>> round(nsolve("cos(x) - x", 1), 6)
    0.739085
    """
    e = equation(eq)
    f = func(e.lhs - e.rhs, var)
    return float(_spo.fsolve(f, float(guess))[0])


__all__ = [
    "analyse",
    "arc_length",
    "area_between",
    "diff",
    "gradient_at",
    "inflection_points",
    "integrate",
    "limit",
    "nderivative",
    "nintegrate",
    "normal",
    "nsolve",
    "series_sum",
    "solve_ode",
    "stationary_points",
    "tangent",
    "taylor",
    "volume_of_revolution",
]
