# %% [markdown]
# # 5. Integration
#
# Differentiation run backwards — and the tool for measuring area, volume and
# accumulated change.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Indefinite integrals (antiderivatives)
#
# SymPy leaves off the `+ C`. Remember it's there.

# %%
print(integrate("x^2"))
print(integrate("1/x"))
print(integrate("exp(x)"))
print(integrate("sin(x)"))
print(integrate("1/(1 + x^2)"))  # gives arctan

# %% [markdown]
# Integration undoes differentiation — worth confirming once:

# %%
print(diff(integrate("x^3 + 2*x")))

# %% [markdown]
# ## Definite integrals = signed area
#
# Area below the axis counts as negative. That's why `∫sin` over a full period
# is zero even though the curve clearly encloses area.

# %%
print(integrate("x^2", lower=0, upper=3))
print(integrate("sin(x)", lower=0, upper=pi))
print(integrate("sin(x)", lower=0, upper=2 * pi))  # zero: the halves cancel

# %%
plot_integral("sin(x)", 0, 6.283, title="Positive and negative area cancel")

# %%
plot_integral("x^2", 0, 3)

# %% [markdown]
# ## Techniques
#
# ### Substitution — reverse chain rule

# %%
print(integrate("2*x*exp(x^2)"))
print(integrate("x*sqrt(x^2 + 1)"))

# %% [markdown]
# ### By parts — reverse product rule, `∫u dv = uv - ∫v du`

# %%
print(integrate("x*exp(x)"))
print(integrate("x*sin(x)"))
print(integrate("log(x)"))

# %% [markdown]
# ### Partial fractions — split first, then integrate term by term

# %%
print(apart("1/(x^2 - 1)"))
print(integrate("1/(x^2 - 1)"))

# %% [markdown]
# ## Improper integrals
#
# Infinite bounds are fine — as long as the area converges.

# %%
print(integrate("exp(-x)", lower=0, upper="oo"))
print(integrate("1/x^2", lower=1, upper="oo"))  # converges
print(integrate("1/x", lower=1, upper="oo"))  # diverges: ∞

# %% [markdown]
# ## Area between curves
#
# With no bounds given, the intersection points are used automatically.

# %%
print(area_between("x", "x^2"))
print(area_between("sin(x)", "cos(x)", lower=0, upper=pi / 4))

# %%
plot("x", "x^2", domain=(-0.5, 1.5), title="Area between y = x and y = x²")

# %% [markdown]
# ## Volumes of revolution
#
# Spin a curve about an axis and you sweep out a solid: `V = π∫y² dx`.
#
# A straight line gives a cone; a semicircle gives a sphere. Both classic
# formulas fall straight out:

# %%
print("cone (y = x, 0→1):", volume_of_revolution("x", 0, 1), "= πr²h/3 with r = h = 1")
print("sphere (y = √(1-x²), -1→1):", volume_of_revolution("sqrt(1 - x^2)", -1, 1), "= 4π/3")

# %% [markdown]
# ## Arc length
#
# `L = ∫√(1 + (dy/dx)²) dx`. Most arc lengths have no elementary form, so this
# is often a numeric job.

# %%
print(arc_length("x^2", 0, 1))
print(float(arc_length("x^2", 0, 1)))

# %% [markdown]
# ## When there is no elementary antiderivative
#
# `e^(-x²)` has none — no combination of standard functions differentiates to
# it. The area still exists, so integrate it numerically.

# %%
print(integrate("exp(-x^2)"))  # SymPy answers with the error function
print(nintegrate("exp(-x^2)", -5, 5))
import math

print("compare √π =", math.sqrt(math.pi))

# %%
plot_integral("exp(-x^2)", -3, 3, title="The Gaussian, integrated numerically")

# %% [markdown]
# ## The trapezoidal rule, by hand
#
# Worth building once to see what "numeric integration" actually means: chop the
# area into trapezia and add them up.

# %%
import numpy as np


def trapezoid(expr, lower, upper, strips):
    f = func(expr)
    xs = np.linspace(lower, upper, strips + 1)
    ys = f(xs)
    width = (upper - lower) / strips
    return width * (ys[0] / 2 + ys[1:-1].sum() + ys[-1] / 2)

for strips in [4, 10, 100, 10_000]:
    print(f"{strips:>6} strips: {trapezoid('x^2', 0, 3, strips):.8f}")
print(" exact       :", integrate("x^2", lower=0, upper=3))

# %% [markdown]
# NumPy and SciPy ship the same idea, better implemented:

# %%
from scipy import integrate as spi

xs = np.linspace(0, 3, 1001)
print("np.trapezoid:", np.trapezoid(xs**2, xs))
print("scipy.quad:  ", spi.quad(lambda v: v**2, 0, 3))  # (value, error estimate)

# %% [markdown]
# ## Differential equations
#
# An equation involving a derivative. Solving one means finding the *function*
# that satisfies it — with a constant of integration fixed by initial
# conditions.

# %%
print(solve_ode("Derivative(y(x), x) = y(x)"))  # exponential growth
print(solve_ode("Derivative(y(x), x) = -2*y(x)"))  # decay
print(solve_ode("Derivative(y(x), x, 2) + y(x) = 0"))  # simple harmonic motion

# %% [markdown]
# A slope field shows every solution at once: each dash is the gradient a
# solution must have at that point, and the curves thread through them.

# %%
plot_slope_field("x - y", solutions=[(0, 0), (0, 2), (0, -2)],
                 title="dy/dx = x - y")
