"""Trigonometry: exact values, identities, equations, triangle solving.

Degrees vs radians is the classic source of wrong answers. Every function here
takes an explicit ``deg=`` flag rather than a hidden global mode.
"""

from __future__ import annotations

import math

import sympy as sp

from .symbols import sym, x


def deg2rad(d) -> sp.Expr:
    """Degrees to radians, kept exact: 30° -> pi/6."""
    return sp.rad(sp.nsimplify(d))


def rad2deg(r) -> sp.Expr:
    """Radians to degrees: pi/6 -> 30."""
    return sp.deg(sp.nsimplify(r))


def evaluate(expr: str | sp.Expr, deg: bool = False) -> sp.Expr:
    """Evaluate a trig expression exactly.

    With ``deg=True`` every bare number inside a trig function is read as degrees.

    >>> evaluate("sin(30)", deg=True)
    1/2
    >>> evaluate("cos(pi/4)")
    sqrt(2)/2
    """
    e = sym(expr)
    if deg:
        e = e.replace(
            lambda node: isinstance(node, sp.Function) and node.func in _TRIG,
            lambda node: node.func(sp.rad(node.args[0])),
        )
    return sp.simplify(sp.nsimplify(e))


_TRIG = (sp.sin, sp.cos, sp.tan, sp.sec, sp.csc, sp.cot)


def solve_trig(eq: str | sp.Expr, var: sp.Symbol = x, lower=0, upper=None, deg: bool = False):
    """Solve a trig equation over a domain — the "0 ≤ x ≤ 360°" question.

    Returns solutions in the same units you asked for.

    >>> solve_trig("sin(x) = 1/2", lower=0, upper=360, deg=True)
    [30, 150]
    """
    from .symbols import equation

    e = equation(eq)
    expr = e.lhs - e.rhs
    if deg:
        # Rewrite sin(x) as sin(rad(x)), so the *variable itself* now carries
        # degrees — which means the domain stays in degrees too.
        expr = expr.replace(
            lambda node: isinstance(node, sp.Function) and node.func in _TRIG,
            lambda node: node.func(sp.rad(node.args[0])),
        )
        lo = sp.nsimplify(lower)
        hi = sp.nsimplify(360 if upper is None else upper)
    else:
        lo = sp.nsimplify(lower)
        hi = 2 * sp.pi if upper is None else sp.nsimplify(upper)

    solset = sp.solveset(sp.Eq(expr, 0), var, domain=sp.Interval(lo, hi))
    try:
        return sorted(solset, key=lambda s: float(s))
    except TypeError:  # an infinite or symbolic solution set
        return solset


def identity_check(lhs: str | sp.Expr, rhs: str | sp.Expr) -> bool:
    """Is this trig identity true for all values?

    >>> identity_check("sin(x)^2 + cos(x)^2", "1")
    True
    """
    return sp.simplify(sp.trigsimp(sym(lhs) - sym(rhs))) == 0


def simplify_trig(expr: str | sp.Expr) -> sp.Expr:
    """Apply trig identities to shorten an expression.

    >>> simplify_trig("2*sin(x)*cos(x)")
    sin(2*x)
    """
    return sp.trigsimp(sym(expr))


def expand_trig(expr: str | sp.Expr) -> sp.Expr:
    """Expand compound angles: sin(A+B) -> sinA cosB + cosA sinB."""
    return sp.expand_trig(sym(expr))


def harmonic_form(a_coeff, b_coeff, deg: bool = True) -> dict:
    """Rewrite ``a·sin(x) + b·cos(x)`` as ``R·sin(x + alpha)``.

    The standard trick for finding the max/min of a mixed sine-cosine wave:
    R is the amplitude, alpha the phase shift.

    >>> harmonic_form(3, 4)["R"]
    5
    """
    A, B = sp.nsimplify(a_coeff), sp.nsimplify(b_coeff)
    R = sp.sqrt(A**2 + B**2)
    alpha = sp.atan2(B, A)
    alpha_out = sp.simplify(rad2deg(alpha) if deg else alpha)
    return {
        "R": sp.simplify(R),
        "alpha": alpha_out,
        "alpha_approx": float(alpha_out),  # the exact form is often unreadable
        "units": "degrees" if deg else "radians",
        "form": f"{sp.simplify(R)}*sin(x + alpha)",
        "max": sp.simplify(R),
        "min": sp.simplify(-R),
    }


def wave(amplitude=1, period=None, phase=0, vertical=0, deg: bool = False) -> dict:
    """Build ``y = A·sin(B(x - C)) + D`` from the features you care about.

    >>> wave(amplitude=2, period=180, deg=True)["expression"]
    2*sin(2*x)
    """
    A = sp.nsimplify(amplitude)
    full_turn = 360 if deg else 2 * sp.pi
    P = sp.nsimplify(full_turn if period is None else period)
    B = sp.simplify(full_turn / P) if deg else sp.simplify(2 * sp.pi / P)
    C, D = sp.nsimplify(phase), sp.nsimplify(vertical)
    return {
        "expression": sp.simplify(A * sp.sin(B * (x - C)) + D),
        "amplitude": sp.Abs(A),
        "period": P,
        "phase_shift": C,
        "vertical_shift": D,
        "max": D + sp.Abs(A),
        "min": D - sp.Abs(A),
    }


def solve_triangle(**given) -> dict:
    """Solve a triangle from any valid combination of sides and angles.

    Sides are ``a, b, c``; the angle opposite side ``a`` is ``A``, in degrees.
    Handles SSS, SAS, ASA/AAS and SSA (the ambiguous case is flagged).

    >>> t = solve_triangle(a=3, b=4, C=90)
    >>> round(t["c"], 4)
    5.0
    """
    sides = {s: given.get(s) for s in "abc"}
    angles = {A: given.get(A) for A in "ABC"}
    known_sides = {s: float(v) for s, v in sides.items() if v is not None}
    known_angles = {A: float(v) for A, v in angles.items() if v is not None}

    if len(known_sides) + len(known_angles) < 3:
        raise ValueError("need at least 3 pieces of information")
    if not known_sides:
        raise ValueError("need at least one side length (angles alone fix only the shape)")

    S, G = dict(known_sides), dict(known_angles)
    ambiguous = False

    # Third angle is free once two are known.
    if len(G) == 2:
        missing = (set("ABC") - set(G)).pop()
        G[missing] = 180.0 - sum(G.values())

    if len(S) == 3:  # SSS -> cosine rule for each angle
        a_, b_, c_ = S["a"], S["b"], S["c"]
        G["A"] = math.degrees(math.acos((b_**2 + c_**2 - a_**2) / (2 * b_ * c_)))
        G["B"] = math.degrees(math.acos((a_**2 + c_**2 - b_**2) / (2 * a_ * c_)))
        G["C"] = 180.0 - G["A"] - G["B"]
    elif len(S) == 2 and len(G) >= 1:
        (s1, s2) = sorted(S)
        included = (set("ABC") - {s1.upper(), s2.upper()}).pop()
        if included in G:  # SAS -> cosine rule for the opposite side
            v1, v2, ang = S[s1], S[s2], math.radians(G[included])
            opp = included.lower()
            S[opp] = math.sqrt(v1**2 + v2**2 - 2 * v1 * v2 * math.cos(ang))
            # Cosine rule again for the next angle: unlike arcsin it can't
            # silently return the acute twin of an obtuse angle.
            third_side = S[opp]
            G[s1.upper()] = math.degrees(
                math.acos((v2**2 + third_side**2 - v1**2) / (2 * v2 * third_side))
            )
            G[s2.upper()] = 180.0 - G[included] - G[s1.upper()]
        else:  # SSA -> sine rule, possibly two triangles
            ambiguous = True
            known_pair = next(A for A in G if A.lower() in S)
            k = S[known_pair.lower()] / math.sin(math.radians(G[known_pair]))
            other = next(s for s in S if s.upper() != known_pair)
            ratio = S[other] / k
            if abs(ratio) > 1:
                raise ValueError("no triangle exists with those measurements")
            G[other.upper()] = math.degrees(math.asin(ratio))
            third = (set("ABC") - {known_pair, other.upper()}).pop()
            G[third] = 180.0 - G[known_pair] - G[other.upper()]
            S[third.lower()] = k * math.sin(math.radians(G[third]))
    else:  # ASA / AAS -> sine rule
        known_pair = next((A for A in G if A.lower() in S), None)
        if known_pair is None:
            raise ValueError("cannot pair a known side with its opposite angle")
        k = S[known_pair.lower()] / math.sin(math.radians(G[known_pair]))
        for A in "ABC":
            S.setdefault(A.lower(), k * math.sin(math.radians(G[A])))

    for A in "ABC":
        if A not in G:
            G[A] = 180.0 - sum(G.get(o, 0.0) for o in "ABC" if o != A)

    s = sum(S.values()) / 2
    area = math.sqrt(max(0.0, s * (s - S["a"]) * (s - S["b"]) * (s - S["c"])))
    result = {**S, **G, "area": area, "perimeter": sum(S.values())}
    if ambiguous:
        result["note"] = "SSA (ambiguous case): a second triangle may exist with A' = 180 - A"
    return result


def sine_rule(**given) -> float:
    """Solve for one unknown with a/sin A = b/sin B. Pass three of the four parts.

    >>> round(sine_rule(a=10, A=30, B=45), 4)
    14.1421
    """
    pairs = [("a", "A"), ("b", "B"), ("c", "C")]
    known = [(s, A) for s, A in pairs if given.get(s) is not None and given.get(A) is not None]
    if not known:
        raise ValueError("need one complete side/opposite-angle pair")
    s0, A0 = known[0]
    k = given[s0] / math.sin(math.radians(given[A0]))
    for s, A in pairs:
        if given.get(s) is None and given.get(A) is not None:
            return k * math.sin(math.radians(given[A]))
        if given.get(A) is None and given.get(s) is not None and (s, A) != (s0, A0):
            return math.degrees(math.asin(given[s] / k))
    raise ValueError("nothing left to solve for")


def cosine_rule(a_=None, b_=None, c_=None, C=None) -> float:
    """``c² = a² + b² - 2ab·cos C``. Leave the unknown as None.

    >>> round(cosine_rule(a_=3, b_=4, C=90), 4)
    5.0
    >>> round(cosine_rule(a_=3, b_=4, c_=5), 4)
    90.0
    """
    if c_ is None:
        return math.sqrt(a_**2 + b_**2 - 2 * a_ * b_ * math.cos(math.radians(C)))
    if C is None:
        return math.degrees(math.acos((a_**2 + b_**2 - c_**2) / (2 * a_ * b_)))
    raise ValueError("leave exactly one of c_ or C as None")


__all__ = [
    "cosine_rule",
    "deg2rad",
    "evaluate",
    "expand_trig",
    "harmonic_form",
    "identity_check",
    "rad2deg",
    "simplify_trig",
    "sine_rule",
    "solve_triangle",
    "solve_trig",
    "wave",
]
