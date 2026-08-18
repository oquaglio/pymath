# %% [markdown]
# # 9. Sequences, series and complex numbers

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Arithmetic sequences — add the same amount each time
#
# `Tn = a + (n−1)d`

# %%
seq = arithmetic(first=3, difference=5)
print("first terms:", seq["first_terms"])
print("nth term:   ", seq["nth_term"])
print("sum to n:   ", seq["sum_to_n"])
print("T20 =", seq["nth_term"].subs(n, 20))
print("S20 =", seq["sum_to_n"].subs(n, 20))

# %% [markdown]
# ## Geometric sequences — multiply by the same amount each time
#
# `Tn = a·r^(n−1)`. When |r| < 1 the terms shrink and the infinite sum
# converges.

# %%
import sympy as sp

g = geometric(first=1, ratio=sp.Rational(1, 2))
print("first terms:     ", g["first_terms"][:6])
print("sum to infinity: ", g["sum_to_infinity"])

# %%
diverging = geometric(first=1, ratio=2)
print("ratio 2 converges?", diverging["converges"], "→", diverging["sum_to_infinity"])

# %% [markdown]
# A recurring decimal *is* an infinite geometric series. 0.333… = 3/10 + 3/100 + …

# %%
print(geometric(sp.Rational(3, 10), sp.Rational(1, 10))["sum_to_infinity"])

# %% [markdown]
# ## Finding the rule from the terms

# %%
for terms in [[3, 8, 13, 18], [2, 6, 18, 54], [1, 4, 9, 16, 25], [2, 5, 10, 17, 26]]:
    found = from_terms(terms)
    print(f"{terms} → {found['type']}: Tn = {found['nth_term']}")

# %% [markdown]
# ## Recurrence relations
#
# Each term defined from the previous ones — how compound interest, population
# models and Fibonacci all work.

# %%
print("doubling:  ", sequences.recurrence("2*T(n-1)", {1: 1}, terms=8))
print("fibonacci: ", sequences.recurrence("T(n-1) + T(n-2)", {1: 1, 2: 1}, terms=10))
print("savings:   ", sequences.recurrence("1.05*T(n-1) + 100", {1: 1000}, terms=5))

# %% [markdown]
# ## Sigma notation and convergence
#
# `series_sum` evaluates Σ, including to infinity.

# %%
print("Σ n, 1→100:      ", series_sum("n", n, 1, 100))
print("Σ n², 1→10:      ", series_sum("n^2", n, 1, 10))
print("Σ 1/2ⁿ, 0→∞:     ", series_sum("1/2^n", n, 0, "oo"))
print("Σ 1/n², 1→∞:     ", series_sum("1/n^2", n, 1, "oo"), "← the Basel problem")

# %% [markdown]
# The harmonic series `Σ1/n` diverges, even though its terms shrink to zero.
# Terms tending to zero is necessary for convergence, but not sufficient:

# %%
show(converges("1/n", start=1))
show(converges("1/n^2", start=1))

# %% [markdown]
# ## Taylor series — every function as a polynomial
#
# Near a point, a well-behaved function is *almost* a polynomial. Add more terms
# and the match extends further.

# %%
print(calculus.taylor("exp(x)", order=6))
print(calculus.taylor("sin(x)", order=8))
print(calculus.taylor("1/(1 - x)", order=6))  # the geometric series again

# %%
plot("sin(x)", "x", "x - x^3/6", "x - x^3/6 + x^5/120",
     labels=["sin x", "1 term", "2 terms", "3 terms"],
     domain=(-6, 6), ylim=(-2.5, 2.5),
     title="Taylor polynomials closing in on sin x")

# %% [markdown]
# This is how a calculator computes `sin` — it evaluates a polynomial.

# %% [markdown]
# ## Complex numbers
#
# `i² = −1`. Every polynomial then has exactly as many roots as its degree.

# %%
print(solve("x^2 + 1 = 0"))
print(solve("x^2 + 2*x + 5 = 0"))
print(solve("x^4 - 1 = 0"))

# %% [markdown]
# ### Cartesian, polar and exponential forms
#
# Same number, three costumes. Polar form makes multiplication easy:
# multiply the moduli, add the arguments.

# %%
show(complex_form(1 + sp.I))

# %%
show(complex_form(3 + 4 * sp.I))

# %% [markdown]
# ### De Moivre's theorem
#
# `(r·cis θ)^n = rⁿ·cis(nθ)` — powers become multiplication of the angle.

# %%
print(sequences.de_moivre(sp.I, 2)["result"])
print(sequences.de_moivre(1 + sp.I, 8)["result"])

# %% [markdown]
# ### Roots of unity
#
# The n complex nth roots of 1 sit evenly spaced around the unit circle — the
# vertices of a regular n-gon.

# %%
for root in sequences.roots_of_unity(3):
    print(root, "→ modulus", sp.Abs(root), " argument", sp.deg(sp.arg(root)), "°")

# %%
import matplotlib.pyplot as plt
import numpy as np

roots = sequences.roots_of_unity(7)
pts = [complex(r) for r in roots]
p = theme.palette()
fig, ax = plt.subplots(figsize=(6, 6))
circle_t = np.linspace(0, 2 * np.pi, 400)
ax.plot(np.cos(circle_t), np.sin(circle_t), color=p.muted, linewidth=1)
ax.plot([z.real for z in pts], [z.imag for z in pts], "o", color=p.color(0),
        markersize=9, markeredgecolor=p.surface, markeredgewidth=2, linestyle="none")
ax.set_aspect("equal")
ax.set_title("The 7th roots of unity")
ax.set_xlabel("real")
ax.set_ylabel("imaginary")
fig.savefig("plots/roots_of_unity.png", facecolor=p.page, bbox_inches="tight")
print("saved plots/roots_of_unity.png")

# %% [markdown]
# ### Euler's identity
#
# `e^(iπ) + 1 = 0` — five constants, one equation.

# %%
print(sp.simplify(sp.exp(sp.I * sp.pi) + 1))
