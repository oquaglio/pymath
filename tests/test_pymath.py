"""Tests that double as worked examples — every one is a question with a known answer."""

from __future__ import annotations

import math

import pytest
import sympy as sp

from pymath import (
    algebra,
    calculus,
    geometry,
    linalg,
    numbertheory,
    rpn,
    sequences,
    stats,
    trig,
)
from pymath.symbols import n, x, y

# --- algebra -----------------------------------------------------------------

def test_solve_quadratic():
    assert algebra.solve("x^2 - 5x + 6 = 0") == [2, 3]


def test_solve_discards_complex_when_real_only():
    assert algebra.solve("x^2 + 1 = 0", domain="real") == []
    assert algebra.solve("x^2 + 1 = 0") == [-sp.I, sp.I]


def test_solve_system():
    assert algebra.solve_system(["2x + y = 5", "x - y = 1"]) == {x: 2, y: 1}


def test_quadratic_analysis():
    q = algebra.quadratic(1, -4, 3)
    assert q["discriminant"] == 4
    assert q["vertex"] == (2, -1)
    assert q["roots"] == [1, 3]
    assert q["opens"] == "upwards"


def test_completed_square_matches_original():
    q = algebra.quadratic(2, 8, 3)
    assert sp.expand(q["completed_square"] - q["expression"]) == 0


def test_polynomial_division():
    d = algebra.divide("x^3 - 2x + 5", "x - 2")
    assert d["quotient"] == x**2 + 2 * x + 2
    assert d["remainder"] == 9


def test_inequality():
    result = algebra.solve_inequality("x^2 - 4 > 0")
    assert result == sp.Union(sp.Interval.open(-sp.oo, -2), sp.Interval.open(2, sp.oo))


def test_calculator_shorthand_parses():
    assert algebra.expand("(x+2)^2") == x**2 + 4 * x + 4
    assert algebra.simplify("2x + 3x") == 5 * x


# --- calculus ----------------------------------------------------------------

def test_first_principles_limit():
    assert calculus.limit("sin(x)/x", to=0) == 1


def test_one_sided_limits_differ():
    assert calculus.limit("1/x", to=0, direction="+") == sp.oo
    assert calculus.limit("1/x", to=0, direction="-") == -sp.oo


def test_product_rule():
    assert sp.expand(calculus.diff("x^2*sin(x)") - (x**2 * sp.cos(x) + 2 * x * sp.sin(x))) == 0


def test_definite_integral():
    assert calculus.integrate("x^2", lower=0, upper=3) == 9


def test_improper_integral():
    assert calculus.integrate("exp(-x)", lower=0, upper="oo") == 1


def test_tangent_line():
    assert calculus.tangent("x^2", 3) == 6 * x - 9


def test_normal_is_perpendicular_to_tangent():
    m_tangent = calculus.gradient_at("x^2", 3)
    m_normal = sp.diff(calculus.normal("x^2", 3), x)
    assert sp.simplify(m_tangent * m_normal) == -1


def test_stationary_points_classified():
    pts = calculus.stationary_points("x^3 - 3x")
    assert [(p["x"], p["nature"]) for p in pts] == [(-1, "maximum"), (1, "minimum")]


def test_inflection_point():
    assert [p["x"] for p in calculus.inflection_points("x^3")] == [0]


def test_analyse_finds_asymptotes():
    info = calculus.analyse("1/(x - 2)")
    assert info["vertical_asymptotes"] == [2]
    assert info["horizontal_asymptotes"] == [0]


def test_maclaurin_series():
    assert calculus.taylor("exp(x)", order=4) == x**3 / 6 + x**2 / 2 + x + 1


def test_area_between_curves():
    assert calculus.area_between("x", "x^2") == sp.Rational(1, 6)


def test_volume_of_revolution_cone():
    # y = x from 0 to 1 sweeps a cone of radius 1, height 1: V = pi/3
    assert calculus.volume_of_revolution("x", 0, 1) == sp.pi / 3


def test_infinite_geometric_series():
    assert calculus.series_sum("1/2^n", n, 0, "oo") == 2


def test_ode_solution():
    sol = calculus.solve_ode("Derivative(y(x), x) = y(x)")
    assert "exp(x)" in str(sol)


def test_numeric_fallbacks_agree_with_exact():
    assert calculus.nintegrate("x^2", 0, 3) == pytest.approx(9.0)
    assert calculus.nderivative("x^2", 3) == pytest.approx(6.0, abs=1e-5)
    assert calculus.nsolve("cos(x) - x", 1) == pytest.approx(0.7390851, abs=1e-6)


def test_gaussian_integral_has_no_elementary_form_but_integrates_numerically():
    assert calculus.nintegrate("exp(-x^2)", -6, 6) == pytest.approx(math.sqrt(math.pi), abs=1e-6)


# --- trigonometry ------------------------------------------------------------

def test_exact_trig_values_in_degrees():
    assert trig.evaluate("sin(30)", deg=True) == sp.Rational(1, 2)
    assert trig.evaluate("cos(pi/4)") == sp.sqrt(2) / 2


def test_trig_equation_over_degree_domain():
    assert trig.solve_trig("sin(x) = 1/2", lower=0, upper=360, deg=True) == [30, 150]


def test_trig_equation_over_radian_domain():
    assert trig.solve_trig("cos(x) = 0", lower=0, upper=2 * sp.pi) == [sp.pi / 2, 3 * sp.pi / 2]


def test_pythagorean_identity():
    assert trig.identity_check("sin(x)^2 + cos(x)^2", "1")


def test_double_angle_identity():
    assert trig.identity_check("sin(2*x)", "2*sin(x)*cos(x)")


def test_harmonic_form():
    h = trig.harmonic_form(3, 4)
    assert h["R"] == 5
    assert h["alpha_approx"] == pytest.approx(53.13010, abs=1e-4)


def test_solve_triangle_sss():
    t = trig.solve_triangle(a=3, b=4, c=5)
    assert t["C"] == pytest.approx(90.0)
    assert t["area"] == pytest.approx(6.0)


def test_solve_triangle_sas():
    t = trig.solve_triangle(a=3, b=4, C=90)
    assert t["c"] == pytest.approx(5.0)
    assert t["A"] == pytest.approx(36.8698976, abs=1e-6)


def test_solve_triangle_sas_obtuse():
    t = trig.solve_triangle(a=5, b=7, C=120)
    assert t["c"] == pytest.approx(math.sqrt(25 + 49 + 35))
    assert t["A"] + t["B"] + t["C"] == pytest.approx(180.0)


def test_solve_triangle_asa():
    t = trig.solve_triangle(a=10, A=30, B=45)
    assert t["b"] == pytest.approx(14.1421356, abs=1e-6)
    assert t["C"] == pytest.approx(105.0)


def test_cosine_rule_both_directions():
    assert trig.cosine_rule(a_=3, b_=4, C=90) == pytest.approx(5.0)
    assert trig.cosine_rule(a_=3, b_=4, c_=5) == pytest.approx(90.0)


# --- geometry ----------------------------------------------------------------

def test_distance_and_midpoint():
    assert geometry.distance((0, 0), (3, 4)) == 5
    assert geometry.midpoint((0, 0), (4, 6)) == (2, 3)


def test_line_from_two_points():
    ln = geometry.line((0, 1), (2, 5))
    assert ln["gradient"] == 2
    assert ln["y="] == 2 * x + 1


def test_horizontal_line_x_intercepts():
    assert geometry.line((0, 3), slope=0)["x_intercept"] is sp.EmptySet
    assert geometry.line((0, 0), slope=0)["x_intercept"] is sp.S.Reals


def test_perpendicular_gradients_multiply_to_minus_one():
    perp = geometry.perpendicular_through((0, 0), 2)
    assert sp.diff(perp, x) * 2 == -1


def test_circle_from_general_form():
    c = geometry.circle_from_general("x^2 + y^2 - 2x - 4y - 4")
    assert c["centre"] == (1, 2)
    assert c["radius"] == 3


def test_shoelace_area():
    assert geometry.polygon_area([(0, 0), (4, 0), (4, 3)]) == 6


def test_solid_volumes():
    assert geometry.solid("sphere", r=3)["volume"] == 36 * sp.pi
    assert geometry.solid("cone", r=3, h=4)["slant_height"] == 5


def test_sector():
    s = geometry.arc(6, 60)
    assert s["sector_area"] == 6 * sp.pi
    assert s["arc_length"] == 2 * sp.pi


def test_vectors():
    v1, v2 = geometry.vector(1, 0, 0), geometry.vector(0, 1, 0)
    assert geometry.dot(v1, v2) == 0
    assert geometry.angle_between(v1, v2) == 90
    assert list(geometry.cross(v1, v2)) == [0, 0, 1]
    assert geometry.magnitude(geometry.vector(3, 4)) == 5


def test_bearing_is_clockwise_from_north():
    assert geometry.bearing((0, 0), (0, 1)) == pytest.approx(0.0)
    assert geometry.bearing((0, 0), (1, 0)) == pytest.approx(90.0)


# --- linear algebra ----------------------------------------------------------

def test_determinant_and_inverse():
    m = [[1, 2], [3, 4]]
    assert linalg.determinant(m) == -2
    assert linalg.inverse(m) * sp.Matrix(m) == sp.eye(2)


def test_singular_matrix_has_no_inverse():
    with pytest.raises(ValueError, match="singular"):
        linalg.inverse([[1, 2], [2, 4]])


def test_solve_simultaneous_equations_by_matrix():
    assert list(linalg.solve_linear([[2, 1], [1, -1]], [5, 1])) == [2, 1]


def test_eigenvalues():
    assert linalg.eigen([[2, 0], [0, 3]])["eigenvalues"] == {2: 1, 3: 1}


def test_rotation_matrix_turns_x_axis_to_y_axis():
    rot = linalg.transform_2d("rotation", angle=90)
    assert list(rot * sp.Matrix([1, 0])) == [0, 1]


# --- statistics --------------------------------------------------------------

def test_describe():
    d = stats.describe([2, 4, 4, 4, 5, 5, 7, 9])
    assert d["mean"] == pytest.approx(5.0)
    assert d["sd_population"] == pytest.approx(2.0)
    assert d["median"] == pytest.approx(4.5)


def test_sample_and_population_sd_differ():
    d = stats.describe([1, 2, 3, 4])
    assert d["sd_sample"] > d["sd_population"]


def test_normal_distribution():
    n = stats.normal(100, 15)
    assert n["below"](115) == pytest.approx(0.8413447, abs=1e-6)
    assert n["between"](85, 115) == pytest.approx(0.6826895, abs=1e-6)
    assert n["inverse"](0.5) == pytest.approx(100.0)


def test_binomial_distribution():
    b = stats.binomial(10, 0.5)
    assert b["exactly"](5) == pytest.approx(0.2460938, abs=1e-6)
    assert b["mean"] == 5.0


def test_linear_regression_is_exact_on_a_line():
    r = stats.regression([1, 2, 3, 4], [3, 5, 7, 9])
    assert r["slope"] == pytest.approx(2.0)
    assert r["intercept"] == pytest.approx(1.0)
    assert r["r_squared"] == pytest.approx(1.0)


def test_exponential_regression():
    xs = [0, 1, 2, 3]
    ys = [2 * math.exp(0.5 * v) for v in xs]
    r = stats.regression(xs, ys, "exponential")
    assert r["r_squared"] == pytest.approx(1.0, abs=1e-9)
    assert r["predict"](4) == pytest.approx(2 * math.exp(2.0))


def test_counting():
    assert stats.nPr(5, 2) == 20
    assert stats.nCr(5, 2) == 10


def test_confidence_interval_brackets_the_mean():
    ci = stats.confidence_interval([10, 12, 11, 13, 12])
    assert ci["lower"] < ci["mean"] < ci["upper"]


# --- sequences & complex numbers ---------------------------------------------

def test_arithmetic_sequence():
    seq = sequences.arithmetic(3, 5)
    assert seq["nth_term"] == 5 * n - 2
    assert seq["first_terms"][:3] == [3, 8, 13]


def test_geometric_sum_to_infinity():
    assert sequences.geometric(1, sp.Rational(1, 2))["sum_to_infinity"] == 2


def test_divergent_geometric_has_no_infinite_sum():
    assert sequences.geometric(1, 2)["sum_to_infinity"] is None


def test_pattern_detection():
    assert sequences.from_terms([3, 8, 13, 18])["type"] == "arithmetic"
    assert sequences.from_terms([2, 6, 18, 54])["type"] == "geometric"
    assert "polynomial" in sequences.from_terms([1, 4, 9, 16, 25])["type"]


def test_recurrence():
    assert sequences.recurrence("2*T(n-1)", {1: 1}, terms=5) == [1, 2, 4, 8, 16]


def test_complex_polar_form():
    z = sequences.complex_form(1 + sp.I)
    assert z["modulus"] == sp.sqrt(2)
    assert z["argument_deg"] == 45


def test_de_moivre():
    assert sequences.de_moivre(sp.I, 2)["result"] == -1


def test_cube_roots_of_unity():
    roots = sequences.roots_of_unity(3)
    assert len(roots) == 3
    assert all(sp.simplify(r**3) == 1 for r in roots)


# --- number theory -----------------------------------------------------------

def test_prime_factorisation():
    f = numbertheory.factorise_int(360)
    assert f["prime_factors"] == {2: 3, 3: 2, 5: 1}
    assert f["divisor_count"] == 24


def test_gcd_lcm():
    assert numbertheory.gcd(12, 18, 24) == 6
    assert numbertheory.lcm(4, 6) == 12


def test_bases_round_trip():
    assert numbertheory.to_base(255, 16) == "ff"
    assert numbertheory.from_base("ff", 16) == 255
    assert numbertheory.to_base(0, 2) == "0"


def test_decimal_to_exact_fraction():
    assert numbertheory.fraction(0.375)["fraction"] == sp.Rational(3, 8)


def test_surd_rationalises_denominator():
    assert numbertheory.surd("1/sqrt(2)") == sp.sqrt(2) / 2


def test_continued_fraction_of_pi():
    assert numbertheory.continued_fraction(sp.pi, 4) == [3, 7, 15, 1]


# --- RPN ---------------------------------------------------------------------

def test_rpn_basic_evaluation():
    assert rpn.evaluate("3 4 + 2 *") == 14
    assert rpn.evaluate("5 1 2 + 4 * + 3 -") == 14
    assert rpn.evaluate("2 10 ^") == 1024


def test_rpn_operand_order_is_not_symmetric():
    assert rpn.evaluate("5 3 -") == 2  # 5 - 3, not 3 - 5
    assert rpn.evaluate("6 2 /") == 3


def test_rpn_keeps_values_exact():
    assert rpn.evaluate("2 sqrt") == sp.sqrt(2)
    assert rpn.evaluate("1 2 / 1 3 / +") == sp.Rational(5, 6)
    assert rpn.evaluate("pi 6 / sin") == sp.Rational(1, 2)


def test_rpn_handles_symbols():
    assert rpn.evaluate("x 2 ^ x 3 * + expand") == x**2 + 3 * x


def test_rpn_stack_operations():
    assert rpn.Calculator().push("3 dup *").x == 9
    assert rpn.Calculator().push("1 2 swap -").x == 1  # 2 - 1
    assert rpn.Calculator().push("1 2 3 sum").x == 6
    assert rpn.Calculator().push("2 3 4 prod").x == 24
    assert rpn.Calculator().push("1 2 drop").x == 1


def test_rpn_empty_stack_is_an_error():
    with pytest.raises(rpn.RPNError, match="empty"):
        rpn.evaluate("3 +")


def test_rpn_leftover_operands_is_an_error():
    with pytest.raises(rpn.RPNError, match="expected one value"):
        rpn.evaluate("1 2 3 +")


def test_shunting_yard_respects_precedence():
    assert rpn.to_rpn("3 + 4 * 2") == "3 4 2 * +"
    assert rpn.to_rpn("(3 + 4) * 2") == "3 4 + 2 *"


def test_shunting_yard_power_is_right_associative():
    # 2^(3^2) = 512, not (2^3)^2 = 64
    assert rpn.evaluate(rpn.to_rpn("2 ^ 3 ^ 2")) == 512


def test_shunting_yard_unary_minus_binds_tighter_than_binary():
    assert rpn.evaluate(rpn.to_rpn("-3 + 4")) == 1  # (-3) + 4, not -(3 + 4)
    assert rpn.evaluate(rpn.to_rpn("2 ^ -3")) == sp.Rational(1, 8)


def test_shunting_yard_subtraction_is_left_associative():
    assert rpn.evaluate(rpn.to_rpn("10 - 2 - 3")) == 5
    assert rpn.evaluate(rpn.to_rpn("10 - (2 - 3)")) == 11


@pytest.mark.parametrize("infix", [
    "(3 + 4) * 2", "3 + 4 * 2", "2 ^ 3 ^ 2", "(1 + 2) * (3 - 4)",
    "sqrt(16) + 1", "-3 + 4", "-3 * 4", "2 ^ -3", "10 - 2 - 3",
    "10 - (2 - 3)", "2 * (3 + 4) / 7", "-(2 + 3) * 4",
])
def test_rpn_round_trip_matches_sympy(infix):
    """infix → RPN → value must equal what SymPy makes of the original."""
    value = rpn.evaluate(rpn.to_rpn(infix))
    assert sp.simplify(value - sp.sympify(infix.replace("^", "**"))) == 0


@pytest.mark.parametrize("infix", [
    "(3 + 4) * 2", "3 + 4 * 2", "(1 + 2) * (3 - 4)", "10 - (2 - 3)", "2 * (3 + 4) / 7",
])
def test_infix_rebuilt_from_rpn_is_equivalent(infix):
    rebuilt = rpn.to_infix(rpn.to_rpn(infix))
    assert sp.sympify(rebuilt.replace("^", "**")) == sp.sympify(infix.replace("^", "**"))


def test_unbalanced_parentheses_rejected():
    with pytest.raises(rpn.RPNError, match="unbalanced"):
        rpn.to_rpn("(3 + 4")


def test_cpython_bytecode_is_rpn():
    """(a + b) * c compiles to LOAD a, LOAD b, +, LOAD c, * — the RPN order."""
    listing = rpn.bytecode("(a + b) * c")
    positions = [listing.index(s) for s in ("(a)", "(b)", "(+)", "(c)", "(*)")]
    assert positions == sorted(positions)
