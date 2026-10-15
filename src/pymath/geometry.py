"""Coordinate geometry, mensuration and vectors.

Points are plain tuples, so ``(3, 4)`` and ``(1, 2, 3)`` both work.
"""

from __future__ import annotations

import math

import sympy as sp

from .symbols import x, y


def distance(p1, p2):
    """Straight-line distance between two points, in any dimension.

    >>> distance((0, 0), (3, 4))
    5
    """
    return sp.simplify(sp.sqrt(sum((sp.nsimplify(b) - sp.nsimplify(a)) ** 2
                                   for a, b in zip(p1, p2, strict=True))))


def midpoint(p1, p2) -> tuple:
    """Midpoint of a segment.

    >>> midpoint((0, 0), (4, 6))
    (2, 3)
    """
    return tuple(sp.simplify((sp.nsimplify(a) + sp.nsimplify(b)) / 2)
                 for a, b in zip(p1, p2, strict=True))


def gradient(p1, p2):
    """Gradient (slope) of the line through two points; ``oo`` if vertical.

    >>> gradient((0, 0), (2, 6))
    3
    """
    dx = sp.nsimplify(p2[0]) - sp.nsimplify(p1[0])
    dy = sp.nsimplify(p2[1]) - sp.nsimplify(p1[1])
    return sp.oo if dx == 0 else sp.simplify(dy / dx)


def line(p1, p2=None, slope=None) -> dict:
    """Equation of a line from two points, or a point and a gradient.

    ``x_intercept`` is a single value for a sloped line, ``Reals`` for the
    x-axis (every x) and ``EmptySet`` for any other horizontal line.

    >>> line((0, 1), slope=2)["y="]
    2*x + 1
    >>> line((0, 3), slope=0)["x_intercept"]
    EmptySet
    """
    if p2 is not None:
        m = gradient(p1, p2)
    elif slope is not None:
        m = sp.nsimplify(slope)
    else:
        raise ValueError("give a second point or a slope")
    x0, y0 = sp.nsimplify(p1[0]), sp.nsimplify(p1[1])
    if m is sp.oo:
        return {"y=": None, "general": sp.Eq(x, x0), "gradient": sp.oo, "vertical": True}
    expr = sp.simplify(m * (x - x0) + y0)
    if m == 0:
        # Horizontal: either the x-axis itself (every x) or nowhere.
        x_intercept = sp.S.Reals if y0 == 0 else sp.EmptySet
    else:
        x_intercept = sp.solve(sp.Eq(expr, 0), x)[0]
    return {
        "y=": expr,
        "general": sp.Eq(sp.simplify(sp.together(y - expr)), 0),
        "gradient": m,
        "y_intercept": expr.subs(x, 0),
        "x_intercept": x_intercept,
        "vertical": False,
    }


def perpendicular_through(p, slope) -> sp.Expr:
    """Line through ``p`` perpendicular to one of gradient ``slope``.

    Perpendicular gradients multiply to -1.

    >>> perpendicular_through((0, 0), 2)
    -x/2
    """
    m = sp.nsimplify(slope)
    if m == 0:
        raise ValueError(f"perpendicular to a horizontal line is vertical: x = {p[0]}")
    return sp.simplify(-1 / m * (x - sp.nsimplify(p[0])) + sp.nsimplify(p[1]))


def circle(centre=(0, 0), radius=1) -> dict:
    """Circle from centre and radius, with its expanded general form.

    >>> circle((1, 2), 3)["equation"]
    Eq((x - 1)**2 + (y - 2)**2, 9)
    """
    h, kk, rr = sp.nsimplify(centre[0]), sp.nsimplify(centre[1]), sp.nsimplify(radius)
    eq = sp.Eq((x - h) ** 2 + (y - kk) ** 2, rr**2)
    return {
        "equation": eq,
        "general": sp.Eq(sp.expand((x - h) ** 2 + (y - kk) ** 2 - rr**2), 0),
        "centre": (h, kk),
        "radius": rr,
        "area": sp.pi * rr**2,
        "circumference": 2 * sp.pi * rr,
    }


def circle_from_general(expr: str | sp.Expr) -> dict:
    """Complete the square on ``x² + y² + Dx + Ey + F = 0`` to find centre and radius.

    >>> circle_from_general("x^2 + y^2 - 2x - 4y - 4")["radius"]
    3
    """
    from .symbols import sym

    e = sp.expand(sym(expr))
    poly = sp.Poly(e, x, y)
    D = poly.coeff_monomial(x)
    E = poly.coeff_monomial(y)
    F = poly.coeff_monomial(1)
    h, kk = sp.simplify(-D / 2), sp.simplify(-E / 2)
    r2 = sp.simplify(h**2 + kk**2 - F)
    if r2 < 0:
        raise ValueError("no real circle: radius squared is negative")
    return {"centre": (h, kk), "radius": sp.sqrt(r2), "equation": circle((h, kk), sp.sqrt(r2))}


def polygon_area(points) -> sp.Expr:
    """Area of any simple polygon from its vertices (the shoelace formula).

    >>> polygon_area([(0, 0), (4, 0), (4, 3)])
    6
    """
    pts = [(sp.nsimplify(px), sp.nsimplify(py)) for px, py in points]
    total = sum(
        pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
        for i in range(len(pts))
    )
    return sp.simplify(sp.Abs(total) / 2)


def solid(shape: str, **dims) -> dict:
    """Surface area and volume of a standard solid.

    Shapes: sphere(r), cylinder(r, h), cone(r, h), cube(a), cuboid(a, b, c),
    pyramid(base, height) — ``base`` being the base area.

    >>> solid("sphere", r=3)["volume"]
    36*pi
    """
    d = {kk: sp.nsimplify(v) for kk, v in dims.items()}
    match shape:
        case "sphere":
            return {"volume": sp.Rational(4, 3) * sp.pi * d["r"] ** 3,
                    "surface_area": 4 * sp.pi * d["r"] ** 2}
        case "cylinder":
            return {"volume": sp.pi * d["r"] ** 2 * d["h"],
                    "surface_area": 2 * sp.pi * d["r"] * (d["r"] + d["h"])}
        case "cone":
            slant = sp.sqrt(d["r"] ** 2 + d["h"] ** 2)
            return {"volume": sp.pi * d["r"] ** 2 * d["h"] / 3,
                    "surface_area": sp.pi * d["r"] * (d["r"] + slant),
                    "slant_height": slant}
        case "cube":
            return {"volume": d["a"] ** 3, "surface_area": 6 * d["a"] ** 2}
        case "cuboid":
            return {"volume": d["a"] * d["b"] * d["c"],
                    "surface_area": 2 * (d["a"] * d["b"] + d["b"] * d["c"] + d["a"] * d["c"])}
        case "pyramid":
            return {"volume": d["base"] * d["height"] / 3}
        case _:
            raise ValueError(f"unknown shape: {shape}")


def arc(radius, angle, deg: bool = True) -> dict:
    """Arc length and sector area for a given central angle.

    >>> arc(6, 60)["sector_area"]
    6*pi
    """
    r_, ang = sp.nsimplify(radius), sp.nsimplify(angle)
    rad = sp.rad(ang) if deg else ang
    return {
        "arc_length": sp.simplify(r_ * rad),
        "sector_area": sp.simplify(r_**2 * rad / 2),
        "chord_length": sp.simplify(2 * r_ * sp.sin(rad / 2)),
        "segment_area": sp.simplify(r_**2 * (rad - sp.sin(rad)) / 2),
    }


# --- vectors -----------------------------------------------------------------

def vector(*components) -> sp.Matrix:
    """Build a column vector.

    >>> vector(3, 4).T
    Matrix([[3, 4]])
    """
    return sp.Matrix([sp.nsimplify(c) for c in components])


def magnitude(v) -> sp.Expr:
    """Length of a vector.

    >>> magnitude(vector(3, 4))
    5
    """
    return sp.simplify(sp.Matrix(v).norm())


def unit(v) -> sp.Matrix:
    """Unit vector in the same direction."""
    mv = sp.Matrix(v)
    return sp.simplify(mv / mv.norm())


def dot(v1, v2) -> sp.Expr:
    """Dot product. Zero means the vectors are perpendicular.

    >>> dot(vector(1, 2), vector(3, 4))
    11
    """
    return sp.simplify(sp.Matrix(v1).dot(sp.Matrix(v2)))


def cross(v1, v2) -> sp.Matrix:
    """Cross product (3D only) — perpendicular to both inputs.

    >>> cross(vector(1, 0, 0), vector(0, 1, 0)).T
    Matrix([[0, 0, 1]])
    """
    return sp.Matrix(v1).cross(sp.Matrix(v2))


def angle_between(v1, v2, deg: bool = True):
    """Angle between two vectors, from cos θ = (a·b)/(|a||b|).

    >>> angle_between(vector(1, 0), vector(0, 1))
    90
    """
    m1, m2 = sp.Matrix(v1), sp.Matrix(v2)
    cos_theta = sp.simplify(m1.dot(m2) / (m1.norm() * m2.norm()))
    ang = sp.acos(cos_theta)
    return sp.simplify(sp.deg(ang)) if deg else sp.simplify(ang)


def projection(v1, v2) -> sp.Matrix:
    """Vector projection of ``v1`` onto ``v2`` — the shadow v1 casts on v2."""
    m1, m2 = sp.Matrix(v1), sp.Matrix(v2)
    return sp.simplify(m2 * (m1.dot(m2) / m2.dot(m2)))


def bearing(from_point, to_point) -> float:
    """Compass bearing in degrees: 0 = north, measured clockwise.

    >>> bearing((0, 0), (1, 1))
    45.0
    """
    dx = float(to_point[0]) - float(from_point[0])
    dy = float(to_point[1]) - float(from_point[1])
    return math.degrees(math.atan2(dx, dy)) % 360


__all__ = [
    "angle_between",
    "arc",
    "bearing",
    "circle",
    "circle_from_general",
    "cross",
    "distance",
    "dot",
    "gradient",
    "line",
    "magnitude",
    "midpoint",
    "perpendicular_through",
    "polygon_area",
    "projection",
    "solid",
    "unit",
    "vector",
]
