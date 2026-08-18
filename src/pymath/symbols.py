"""Common symbols and parsing helpers.

Everything symbolic in SymPy starts with a `Symbol`. Rather than declaring
`x = sympy.Symbol("x")` in every script, grab them from here.
"""

from __future__ import annotations

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

# Real-valued symbols. Telling SymPy `real=True` lets it simplify things like
# sqrt(x**2) -> Abs(x) instead of leaving them alone for the complex case.
x, y, z, t, u, v = sp.symbols("x y z t u v", real=True)
a, b, c, d, m, r, s, theta = sp.symbols("a b c d m r s theta", real=True)

# Integer symbols, for sequences and series.
n, k, i, j = sp.symbols("n k i j", integer=True)

# Positive symbols, handy for logs/surds where the domain matters.
p, q = sp.symbols("p q", positive=True)

pi = sp.pi
E = sp.E
oo = sp.oo
I = sp.I

_TRANSFORMS = (
    *standard_transformations,
    implicit_multiplication_application,  # "2x" and "sin x" work
    convert_xor,  # "x^2" means x**2, like a calculator
)

_LOCALS = {
    "x": x, "y": y, "z": z, "t": t, "u": u, "v": v,
    "a": a, "b": b, "c": c, "d": d, "m": m, "r": r, "s": s, "theta": theta,
    "n": n, "k": k, "pi": pi, "e": E, "i": I, "I": I, "oo": oo,
}


def sym(expr: str | sp.Expr) -> sp.Expr:
    """Turn calculator-style text into a SymPy expression.

    Accepts the shorthand a physical calculator accepts: ``^`` for powers and
    implicit multiplication.

    >>> sym("2x^2 + 3x - 5")
    2*x**2 + 3*x - 5
    >>> sym("sin(2x)")  # exact values are evaluated on sight
    sin(2*x)
    """
    if isinstance(expr, sp.Basic):
        return expr
    return parse_expr(str(expr), local_dict=_LOCALS, transformations=_TRANSFORMS)


def equation(expr: str | sp.Expr) -> sp.Eq:
    """Parse ``"lhs = rhs"`` into a SymPy equation.

    A bare expression is read as ``expr = 0``, which is what you want when
    solving.

    >>> equation("2x + 1 = 7")
    Eq(2*x + 1, 7)
    """
    if isinstance(expr, sp.Eq):
        return expr
    # evaluate=False matters: with real symbols SymPy would collapse
    # Eq(x**2 + 1, 0) straight to `False` (no real solution exists) and there
    # would be nothing left to solve for the complex roots.
    if isinstance(expr, sp.Basic):
        return sp.Eq(expr, 0, evaluate=False)
    text = str(expr)
    if "=" in text and "==" not in text:
        lhs, rhs = text.split("=", 1)
        return sp.Eq(sym(lhs), sym(rhs), evaluate=False)
    return sp.Eq(sym(text), 0, evaluate=False)


def func(expr: str | sp.Expr, *vars_: sp.Symbol):
    """Compile an expression into a fast numeric function (a `lambdify`).

    SymPy expressions are slow to evaluate one point at a time. `lambdify`
    converts them into plain Python/NumPy, which is what the plotting code uses.

    >>> f = func("x^2 + 1")
    >>> f(3)
    10
    """
    e = sym(expr)
    variables = vars_ or tuple(sorted(e.free_symbols, key=str)) or (x,)
    return sp.lambdify(variables, e, modules=["numpy"])


__all__ = [
    "E",
    "I",
    "a",
    "b",
    "c",
    "d",
    "equation",
    "func",
    "i",
    "j",
    "k",
    "m",
    "n",
    "oo",
    "p",
    "pi",
    "q",
    "r",
    "s",
    "sym",
    "t",
    "theta",
    "u",
    "v",
    "x",
    "y",
    "z",
]
