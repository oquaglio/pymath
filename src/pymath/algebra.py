"""Algebra: solving, factoring, expanding, simplifying.

The ClassWiz "Equation" and "Polynomial" modes, but symbolic — you get exact
surds and fractions, not decimals.
"""

from __future__ import annotations

import sympy as sp

from .symbols import equation, sym, x


def solve(eq: str | sp.Expr, var: sp.Symbol = x, domain: str = "complex") -> list:
    """Solve an equation exactly.

    ``domain="real"`` throws away complex solutions, which is usually what you
    want at Year 12 level.

    >>> solve("x^2 - 5x + 6 = 0")
    [2, 3]
    >>> solve("x^2 + 1 = 0", domain="real")
    []
    """
    eqn = equation(eq)
    if domain != "real" and var.assumptions0.get("real"):
        # The project's symbols are declared real, which makes SymPy drop
        # complex roots entirely. Swap in an unrestricted symbol first so
        # x^2 + 1 = 0 gives ±i rather than nothing.
        unrestricted = sp.Symbol(var.name)
        eqn, var = eqn.subs(var, unrestricted), unrestricted
    sols = sp.solve(eqn, var, dict=False)
    if domain == "real":
        sols = [s for s in sols if s.is_real]
    return sorted(sols, key=lambda s: (sp.re(s), sp.im(s)))


def solve_system(eqs: list[str | sp.Expr], vars_: list[sp.Symbol] | None = None) -> dict | list:
    """Solve simultaneous equations.

    >>> from .symbols import x, y
    >>> solve_system(["2x + y = 5", "x - y = 1"])
    {x: 2, y: 1}
    """
    parsed = [equation(e) for e in eqs]
    if vars_ is None:
        vars_ = sorted({s for e in parsed for s in e.free_symbols}, key=str)
    return sp.solve(parsed, vars_, dict=False)


def solve_inequality(ineq: str | sp.Expr, var: sp.Symbol = x):
    """Solve an inequality, returning an interval or union of intervals.

    >>> solve_inequality("x^2 - 4 > 0")
    Union(Interval.open(-oo, -2), Interval.open(2, oo))
    """
    return sp.solveset(sym(ineq), var, domain=sp.S.Reals)


def factorise(expr: str | sp.Expr) -> sp.Expr:
    """Factorise over the rationals.

    >>> factorise("x^2 - 5x + 6")
    (x - 3)*(x - 2)
    """
    return sp.factor(sym(expr))


def expand(expr: str | sp.Expr) -> sp.Expr:
    """Multiply everything out.

    >>> expand("(x + 2)^3")
    x**3 + 6*x**2 + 12*x + 8
    """
    return sp.expand(sym(expr))


def simplify(expr: str | sp.Expr) -> sp.Expr:
    """Try hard to find a simpler equivalent form."""
    return sp.simplify(sym(expr))


def apart(expr: str | sp.Expr, var: sp.Symbol = x) -> sp.Expr:
    """Split into partial fractions — the setup step for many integrals.

    >>> apart("1/(x^2 - 1)")
    -1/(2*(x + 1)) + 1/(2*(x - 1))
    """
    return sp.apart(sym(expr), var)


def quadratic(a_: float, b_: float, c_: float) -> dict:
    """Full analysis of ``a x^2 + b x + c``: roots, discriminant, vertex, form.

    The discriminant tells you the root count before you solve:
    ``> 0`` two real roots, ``= 0`` one repeated, ``< 0`` none real.

    >>> quadratic(1, -4, 3)["vertex"]
    (2, -1)
    """
    A, B, C = sp.nsimplify(a_), sp.nsimplify(b_), sp.nsimplify(c_)
    if A == 0:
        raise ValueError("a must be non-zero for a quadratic")
    disc = sp.simplify(B**2 - 4 * A * C)
    h = sp.simplify(-B / (2 * A))
    kk = sp.simplify(C - B**2 / (4 * A))
    expr = A * x**2 + B * x + C
    return {
        "expression": expr,
        "discriminant": disc,
        "real_roots": disc >= 0,
        "roots": sorted(sp.solve(sp.Eq(expr, 0), x), key=lambda s: (sp.re(s), sp.im(s))),
        "vertex": (h, kk),
        "axis_of_symmetry": h,
        "completed_square": sp.simplify(A * (x - h) ** 2 + kk),
        "factored": sp.factor(expr),
        "opens": "upwards" if A > 0 else "downwards",
    }


def polynomial(expr: str | sp.Expr, var: sp.Symbol = x) -> dict:
    """Degree, coefficients, exact roots (with multiplicity) and factorisation.

    >>> polynomial("x^3 - 6x^2 + 11x - 6")["roots"]  # {root: multiplicity}
    {3: 1, 2: 1, 1: 1}
    """
    e = sp.Poly(sp.expand(sym(expr)), var)
    return {
        "degree": e.degree(),
        "coefficients": e.all_coeffs(),
        "roots": sp.roots(e),  # {root: multiplicity}
        "factored": sp.factor(e.as_expr()),
        "leading_coefficient": e.LC(),
    }


def divide(numerator: str | sp.Expr, denominator: str | sp.Expr, var: sp.Symbol = x) -> dict:
    """Polynomial long division: ``num = q * den + r``.

    >>> d = divide("x^3 - 2x + 5", "x - 2")
    >>> d["quotient"], d["remainder"]
    (x**2 + 2*x + 2, 9)
    """
    q, rem = sp.div(sym(numerator), sym(denominator), var)
    return {"quotient": sp.expand(q), "remainder": sp.expand(rem)}


def substitute(expr: str | sp.Expr, **values) -> sp.Expr:
    """Substitute values in, e.g. ``substitute("x^2 + y", x=3, y=1)``."""
    e = sym(expr)
    mapping = {sp.Symbol(name, real=True): sp.nsimplify(val) for name, val in values.items()}
    return sp.simplify(e.subs(mapping))


def make_subject(eq: str | sp.Expr, var: sp.Symbol) -> list:
    """Rearrange a formula to make ``var`` the subject.

    >>> from .symbols import r
    >>> make_subject("A = pi*r^2", r)
    [-sqrt(A)/sqrt(pi), sqrt(A)/sqrt(pi)]
    """
    return sp.solve(equation(eq), var)


def logexp(expr: str | sp.Expr) -> sp.Expr:
    """Apply log/index laws to expand or combine logs and exponentials.

    >>> logexp("log(x*y)")
    log(x) + log(y)
    """
    e = sym(expr)
    return sp.expand_log(sp.powsimp(e, force=True), force=True)


__all__ = [
    "apart",
    "divide",
    "expand",
    "factorise",
    "logexp",
    "make_subject",
    "polynomial",
    "quadratic",
    "simplify",
    "solve",
    "solve_inequality",
    "solve_system",
    "substitute",
]
