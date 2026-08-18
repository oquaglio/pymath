# %% [markdown]
# # 1. Getting started — the four libraries you actually need
#
# Almost all Python maths runs on four packages. Knowing *which one to reach for*
# is most of the skill:
#
# | Library | What it's for | The mental model |
# |---|---|---|
# | **SymPy** | exact, symbolic maths | a CAS — it does algebra the way you do it on paper |
# | **NumPy** | arrays of numbers, fast | a spreadsheet column that does arithmetic all at once |
# | **SciPy** | numeric algorithms | integration, root-finding, statistics, optimisation |
# | **Matplotlib / Plotly** | graphs | static PNG / interactive HTML |
#
# `pymath` wraps all four so you can start with maths and pick up the libraries
# underneath as you go.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Exact vs approximate — the difference that trips people up
#
# A calculator gives you `0.7071067812`. SymPy gives you `sqrt(2)/2`, which is
# *exactly* right and can be simplified further. Both are useful; know which
# one you're holding.

# %%
exact = integrate("1/(1 + x^2)", lower=0, upper=1)
print("exact:      ", exact)
print("approximate:", float(exact))
print("pi/4:       ", float(pi / 4))

# %% [markdown]
# ## Typing maths
#
# `sym()` accepts calculator shorthand: `^` for powers and implicit
# multiplication, so `2x^2` means what you'd expect.

# %%
print(sym("2x^2 + 3x - 5"))
print(sym("sin(pi/6)"), "=", evaluate("sin(pi/6)"))

# %% [markdown]
# Symbols come pre-declared: `x, y, z, t, a, b, c, n, k, theta`. They're declared
# **real**, which lets SymPy simplify more aggressively.

# %%
print(factorise("x^2 - 5x + 6"))
print(expand("(x + 2)^3"))
print(solve("x^2 - 5x + 6 = 0"))

# %% [markdown]
# ## Under the hood: what `pymath` is actually calling
#
# Nothing here is magic. Every helper is a thin wrapper — read the source when
# you want to learn the real API.

# %%
import sympy as sp

print(sp.solve(sp.Eq(x**2 - 5 * x + 6, 0), x))  # what solve() does
print(sp.diff(sp.sin(x) * x, x))  # what diff() does

# %% [markdown]
# ## NumPy: the same maths, thousands of times at once
#
# SymPy is exact but slow. To *plot* something you need thousands of values, so
# `func()` compiles a SymPy expression into a NumPy function (`lambdify`).

# %%
import numpy as np

f = func("x^2 + 1")
xs = np.linspace(-3, 3, 7)
print(xs)
print(f(xs))  # the whole array at once, no loop

# %% [markdown]
# ## Your first graph
#
# Plot functions return the path of the file they wrote. In a notebook, pass
# `show=True` to display inline instead.

# %%
plot("x^2", "2x + 1", domain=(-5, 5), title="Parabola meets line")

# %% [markdown]
# ## Displaying results nicely
#
# `show()` prints exact form then decimal, like a calculator's S⇔D key.
# Anything returning a dict of results prints as a table.

# %%
show(solve("x^2 = 2"), label="roots of x² = 2")
show(quadratic(1, -4, 3))

# %% [markdown]
# ## Where to go next
#
# * `02` algebra · `03` trigonometry · `04`–`05` calculus
# * `06` geometry & vectors · `07` matrices · `08` statistics
# * `09` sequences & complex numbers · `10` the graph gallery
# * `11` beyond Year 12
#
# There is also a terminal calculator: `uv run pymath --help`.
