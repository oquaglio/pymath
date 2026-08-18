# %% [markdown]
# # 4. Differentiation
#
# The derivative is the gradient of the tangent — the instantaneous rate of
# change.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## From first principles
#
# The definition is a limit: `f'(x) = lim(h→0) [f(x+h) - f(x)] / h`. Watch it
# collapse to `2x` for `f(x) = x²`:

# %%
import sympy as sp

h = sp.Symbol("h", positive=True)
quotient = ((x + h) ** 2 - x**2) / h
print("difference quotient:", sp.simplify(quotient))
print("limit as h → 0:     ", sp.limit(quotient, h, 0))

# %% [markdown]
# ## Limits in their own right
#
# Some limits exist even where the function doesn't.

# %%
print(limit("sin(x)/x", to=0))  # the famous one — needs radians
print(limit("(1 + 1/x)^x", to="oo"))  # this is e
print(limit("1/x", to=0, direction="+"))  # from above: +∞
print(limit("1/x", to=0, direction="-"))  # from below: -∞
print(limit("1/x", to=0))  # two-sided: no limit

# %% [markdown]
# ## The rules
#
# `diff` applies all of them; the point is to recognise which rule each example
# needs.

# %%
print("power rule:   ", diff("x^5"))
print("chain rule:   ", diff("(3x + 1)^4"))
print("product rule: ", diff("x^2*sin(x)"))
print("quotient rule:", diff("sin(x)/x"))
print("exponential:  ", diff("exp(2*x)"))
print("logarithm:    ", diff("log(x)"))
print("trig:         ", diff("tan(x)"))

# %% [markdown]
# Higher derivatives — differentiate again:

# %%
print(diff("x^4", order=1))
print(diff("x^4", order=2))
print(diff("x^4", order=3))

# %% [markdown]
# ## Tangents and normals
#
# The tangent has gradient `f'(a)`; the normal is perpendicular, so its gradient
# is `-1/f'(a)`.

# %%
print("gradient at x=3:", gradient_at("x^2", 3))
print("tangent:        ", tangent("x^2", 3))
print("normal:         ", normal_line("x^2", 3))

# %%
plot_tangent("x^2", 3, domain=(-2, 6))

# %% [markdown]
# ## Stationary points
#
# Set `f'(x) = 0`, then use `f''` to classify:
# positive → minimum, negative → maximum, zero → look closer.

# %%
for pt in stationary_points("x^3 - 3x"):
    print(pt)

# %%
plot_analysis("x^3 - 3x", domain=(-3, 3))

# %% [markdown]
# ## The full curve sketch
#
# Intercepts, turning points, inflections, asymptotes, domain — everything an
# exam wants you to "show clearly".

# %%
show(analyse("x^3 - 6x^2 + 9x"))

# %%
plot_analysis("x^3 - 6x^2 + 9x", domain=(-1, 5))

# %% [markdown]
# A rational function, where the asymptotes matter:

# %%
show(analyse("(x^2 + 1)/(x - 2)"))

# %%
plot_analysis("(x^2 + 1)/(x - 2)", domain=(-6, 10))

# %% [markdown]
# ## Optimisation
#
# The real use of calculus: find the input that makes something largest or
# smallest.
#
# **Problem.** A farmer has 100 m of fencing for a rectangular pen against a
# straight wall (so only three sides need fence). What dimensions give the
# largest area?

# %%
# width w, depth d; fencing used: w + 2d = 100, so d = (100 - w)/2
area = x * (100 - x) / 2  # x is the width
print("area(w) =", expand(area))
for pt in stationary_points(area):
    print(pt)
print("so width =", stationary_points(area)[0]["x"],
      "m, depth =", (100 - stationary_points(area)[0]["x"]) / 2, "m")

# %%
plot_analysis(area, domain=(0, 100), title="Pen area against width")

# %% [markdown]
# ## Related rates
#
# Chain rule with time: `dV/dt = dV/dr × dr/dt`.
#
# **Problem.** A spherical balloon inflates at 100 cm³/s. How fast is the radius
# growing when r = 5 cm?

# %%
import sympy as sp

r_sym = sp.Symbol("r", positive=True)
V = sp.Rational(4, 3) * pi * r_sym**3
dV_dr = sp.diff(V, r_sym)
dr_dt = 100 / dV_dr
print("dV/dr =", dV_dr)
print("dr/dt at r=5:", sp.simplify(dr_dt.subs(r_sym, 5)), "≈",
      float(dr_dt.subs(r_sym, 5)), "cm/s")

# %% [markdown]
# ## When there's no exact answer
#
# Plenty of real functions have no tidy derivative or root. Fall back to
# numbers — this is exactly what a physical calculator does internally.

# %%
print("numeric derivative:", nderivative("exp(-x^2)*sin(x)", 1.2))
print("numeric root:      ", nsolve("cos(x) - x", guess=1))

# %%
plot("cos(x) - x", domain=(-2, 3), title="Root near x = 0.739")
