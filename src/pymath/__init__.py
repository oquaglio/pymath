"""pymath — a programmable graphics calculator for learning maths.

Quick start (one import gets you everything):

    >>> from pymath import *
    >>> solve("x^2 - 5x + 6 = 0")
    [2, 3]
    >>> diff("sin(x)*x")
    x*cos(x) + sin(x)
    >>> integrate("x^2", lower=0, upper=3)
    9

Modules, if you'd rather be explicit:

  algebra       solving, factorising, quadratics, polynomials
  calculus      limits, derivatives, integrals, series, ODEs
  trig          exact values, trig equations, triangle solving
  geometry      coordinate geometry, mensuration, vectors
  linalg        matrices, determinants, eigenvalues, transformations
  stats         descriptive stats, distributions, regression, tests
  sequences     sequences, series, complex numbers
  numbertheory  primes, factors, fractions, bases, modular arithmetic
  plotting      every kind of graph, saved as PNG or interactive HTML
  rpn           Reverse Polish Notation stack calculator over exact values
  theme         the shared chart palette

Two names are deliberately different at the top level, because the modules use
the same word for different things: ``normal_line`` is calculus' normal to a
curve, ``normal_dist`` is the statistics normal distribution.
"""

from __future__ import annotations

from . import (
    algebra,
    calculus,
    geometry,
    linalg,
    numbertheory,
    plotting,
    rpn,
    sequences,
    stats,
    theme,
    trig,
)
from .algebra import (
    apart,
    divide,
    expand,
    factorise,
    logexp,
    make_subject,
    polynomial,
    quadratic,
    simplify,
    solve,
    solve_inequality,
    solve_system,
    substitute,
)
from .calculus import (
    analyse,
    arc_length,
    area_between,
    diff,
    gradient_at,
    inflection_points,
    integrate,
    limit,
    nderivative,
    nintegrate,
    nsolve,
    series_sum,
    solve_ode,
    stationary_points,
    tangent,
    taylor,
    volume_of_revolution,
)
from .calculus import normal as normal_line
from .display import show, table
from .geometry import (
    angle_between,
    arc,
    bearing,
    circle,
    cross,
    distance,
    dot,
    gradient,
    line,
    magnitude,
    midpoint,
    polygon_area,
    projection,
    solid,
    unit,
    vector,
)
from .linalg import determinant, eigen, inverse, matrix, rref, solve_linear, transform_2d
from .numbertheory import (
    factorise_int,
    fraction,
    from_base,
    gcd,
    lcm,
    primes_up_to,
    surd,
    to_base,
)
from .plotting import (
    boxplot,
    histogram,
    interactive,
    interactive_surface,
    plot,
    plot_analysis,
    plot_contour,
    plot_implicit,
    plot_integral,
    plot_normal,
    plot_parametric,
    plot_polar,
    plot_slope_field,
    plot_surface,
    plot_tangent,
    scatter,
)
from .rpn import Calculator, to_infix, to_rpn
from .sequences import arithmetic, complex_form, converges, from_terms, geometric
from .stats import (
    binomial,
    confidence_interval,
    correlation,
    describe,
    hypothesis_test,
    nCr,
    nPr,
    poisson,
    regression,
)
from .stats import normal as normal_dist
from .symbols import (
    E,
    I,
    a,
    b,
    c,
    equation,
    func,
    k,
    m,
    n,
    oo,
    pi,
    r,
    s,
    sym,
    t,
    theta,
    x,
    y,
    z,
)
from .trig import (
    cosine_rule,
    deg2rad,
    evaluate,
    harmonic_form,
    identity_check,
    rad2deg,
    simplify_trig,
    sine_rule,
    solve_triangle,
    solve_trig,
    wave,
)

__version__ = "0.1.0"

__all__ = [
    # modules
    "algebra", "calculus", "geometry", "linalg", "numbertheory", "plotting",
    "rpn", "sequences", "stats", "theme", "trig",
    # symbols & parsing
    "x", "y", "z", "t", "a", "b", "c", "k", "m", "n", "r", "s", "theta",
    "pi", "E", "I", "oo",
    "sym", "equation", "func",
    # algebra
    "solve", "solve_system", "solve_inequality", "factorise", "expand", "simplify",
    "apart", "quadratic", "polynomial", "divide", "substitute", "make_subject", "logexp",
    # calculus
    "limit", "diff", "gradient_at", "tangent", "normal_line", "integrate",
    "stationary_points", "inflection_points", "analyse", "taylor", "series_sum",
    "area_between", "volume_of_revolution", "arc_length", "solve_ode",
    "nintegrate", "nderivative", "nsolve",
    # trigonometry
    "deg2rad", "rad2deg", "evaluate", "solve_trig", "identity_check", "simplify_trig",
    "harmonic_form", "wave", "solve_triangle", "sine_rule", "cosine_rule",
    # geometry & vectors
    "distance", "midpoint", "gradient", "line", "circle", "polygon_area", "solid", "arc",
    "vector", "magnitude", "unit", "dot", "cross", "angle_between", "projection", "bearing",
    # linear algebra
    "matrix", "determinant", "inverse", "solve_linear", "rref", "eigen", "transform_2d",
    # statistics
    "describe", "normal_dist", "binomial", "poisson", "regression", "correlation",
    "confidence_interval", "hypothesis_test", "nPr", "nCr",
    # sequences & complex numbers
    "arithmetic", "geometric", "from_terms", "converges", "complex_form",
    # numbers
    "factorise_int", "gcd", "lcm", "primes_up_to", "fraction", "to_base", "from_base", "surd",
    # plotting
    "plot", "plot_analysis", "plot_integral", "plot_tangent", "plot_parametric",
    "plot_polar", "plot_implicit", "plot_surface", "plot_contour", "plot_slope_field",
    "histogram", "boxplot", "scatter", "plot_normal", "interactive", "interactive_surface",
    # rpn
    "Calculator", "to_rpn", "to_infix",
    # display
    "show", "table",
]
