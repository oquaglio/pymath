# %% [markdown]
# # 2. Algebra and functions
#
# Solving, factorising, and reading a function's shape off its equation.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Linear and quadratic equations
#
# `solve()` returns *exact* roots — surds and fractions stay as surds and
# fractions.

# %%
print(solve("3x + 7 = 22"))
print(solve("x^2 - 5x + 6 = 0"))
print(solve("x^2 - 2 = 0"))  # exact surds
print(solve("x^2 + x - 1 = 0"))  # the golden ratio appears

# %% [markdown]
# ## The discriminant decides everything
#
# For `ax² + bx + c`, `Δ = b² - 4ac`:
#
# * `Δ > 0` → two distinct real roots (curve cuts the x-axis twice)
# * `Δ = 0` → one repeated root (curve touches the axis)
# * `Δ < 0` → no real roots (curve misses the axis entirely)

# %%
for coeffs in [(1, -4, 3), (1, -4, 4), (1, -4, 8)]:
    q = quadratic(*coeffs)
    print(f"{q['expression']}: Δ = {q['discriminant']}, roots = {q['roots']}")

# %%
show(quadratic(2, -8, 3))

# %% [markdown]
# Completing the square is what gives you the vertex — and `completed_square`
# above is algebraically identical to the original expression:

# %%
q = quadratic(2, -8, 3)
print(expand(q["completed_square"]) == expand(q["expression"]))

# %%
plot("2x^2 - 8x + 3", domain=(-2, 6), title="Vertex at (2, -5)")

# %% [markdown]
# ## Simultaneous equations
#
# Two unknowns need two equations; three need three.

# %%
print(solve_system(["2x + y = 5", "x - y = 1"]))
print(solve_system(["x + y + z = 6", "2x - y + z = 3", "x + 2y - z = 2"]))

# %% [markdown]
# Non-linear systems work too — a line meeting a circle:

# %%
print(solve_system(["x^2 + y^2 = 25", "y = x + 1"]))

# %%
plot_implicit("x^2 + y^2 = 25", title="Circle and line")

# %% [markdown]
# ## Polynomials
#
# The factor theorem says `(x - a)` is a factor exactly when `f(a) = 0`.

# %%
p = polynomial("x^3 - 6x^2 + 11x - 6")
show(p)

# %% [markdown]
# Long division, when a root isn't obvious. `remainder = 0` confirms a factor:

# %%
print(divide("x^3 - 2x + 5", "x - 2"))
print(divide("x^3 - 6x^2 + 11x - 6", "x - 1"))

# %% [markdown]
# ## Inequalities
#
# The answer is a *set*, not a number — note the interval notation.

# %%
print(solve_inequality("x^2 - 4 > 0"))
print(solve_inequality("(x - 1)*(x + 2) <= 0"))
print(solve_inequality("1/x < 2"))  # watch the discontinuity at 0

# %% [markdown]
# ## Rearranging formulas
#
# "Make r the subject" — two answers, because squaring lost a sign.

# %%
print(make_subject("A = pi*r^2", r))
print(make_subject("v^2 = u^2 + 2*a*s", s))

# %% [markdown]
# ## Indices, logs and exponentials
#
# The log laws: `log(ab) = log a + log b`, `log(a^n) = n log a`.

# %%
print(logexp("log(x*y)"))
print(logexp("log(x^3)"))
print(solve("2^x = 8"))
print(solve("log(x) + log(x - 3) = log(4)"))

# %% [markdown]
# Exponential growth and decay — the shape behind compound interest and
# half-lives:

# %%
plot("2^x", "exp(x)", "(1/2)^x", domain=(-3, 3), title="Growth and decay")

# %% [markdown]
# ## Partial fractions
#
# Splitting one fraction into simpler ones. You'll need this again in
# integration.

# %%
print(apart("1/(x^2 - 1)"))
print(apart("(3*x + 5)/((x + 1)*(x - 2))"))

# %% [markdown]
# ## Transformations of graphs
#
# `f(x) + a` shifts up, `f(x - a)` shifts right, `a*f(x)` stretches vertically,
# `f(a*x)` compresses horizontally, and a minus sign reflects.

# %%
plot("x^2", "x^2 + 2", "(x - 2)^2", "-x^2",
     labels=["f(x)", "f(x) + 2", "f(x - 2)", "-f(x)"],
     domain=(-4, 5), title="Transformations of y = x²")
