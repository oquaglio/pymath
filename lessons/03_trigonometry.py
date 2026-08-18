# %% [markdown]
# # 3. Trigonometry
#
# Exact values, identities, equations over a domain, and solving triangles.
#
# **Degrees or radians?** Every function here takes an explicit `deg=` flag.
# Radians are the default, because calculus only works in radians — the rule
# `d/dx sin x = cos x` is false if x is in degrees.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Exact values
#
# The special angles come out as surds, not decimals.

# %%
for angle in [0, 30, 45, 60, 90]:
    print(f"sin {angle}° = {evaluate(f'sin({angle})', deg=True)}",
          f"  cos {angle}° = {evaluate(f'cos({angle})', deg=True)}")

# %%
print(evaluate("cos(pi/4)"), evaluate("tan(pi/3)"))
print(deg2rad(30), "radians =", rad2deg(pi / 6), "degrees")

# %% [markdown]
# ## The graphs
#
# Period 2π for sine and cosine; tan repeats every π and has asymptotes where
# cos = 0.

# %%
plot("sin(x)", "cos(x)", domain=(-6.3, 6.3), title="Sine and cosine")

# %%
plot("tan(x)", domain=(-6.3, 6.3), ylim=(-6, 6), title="Tangent, with asymptotes")

# %% [markdown]
# ## y = A sin(B(x - C)) + D
#
# * **A** amplitude — height above the centre line
# * **B** sets the period: `period = 360°/B` (or `2π/B`)
# * **C** phase shift (horizontal)
# * **D** vertical shift — the centre line

# %%
w = wave(amplitude=3, period=180, phase=0, vertical=1, deg=True)
show(w)

# %%
plot("sin(x)", "3*sin(2*x) + 1", labels=["y = sin x", "y = 3sin(2x) + 1"],
     domain=(0, 6.3), title="Amplitude, period and shift")

# %% [markdown]
# ## Identities
#
# `identity_check` tests whether two expressions are equal *for every* value.

# %%
print(identity_check("sin(x)^2 + cos(x)^2", "1"))
print(identity_check("sin(2*x)", "2*sin(x)*cos(x)"))
print(identity_check("cos(2*x)", "1 - 2*sin(x)^2"))
print(identity_check("sin(x) + cos(x)", "1"))  # false — only true at some x

# %%
print(simplify_trig("2*sin(x)*cos(x)"))
print(trig.expand_trig("sin(x + y)"))
print(trig.expand_trig("cos(2*x)"))

# %% [markdown]
# ## Trig equations over a domain
#
# The classic exam question: "solve for 0° ≤ x ≤ 360°". There are infinitely
# many solutions overall; the domain picks out the ones you want.

# %%
print(solve_trig("sin(x) = 1/2", lower=0, upper=360, deg=True))
print(solve_trig("cos(x) = -1/2", lower=0, upper=360, deg=True))
print(solve_trig("tan(x) = 1", lower=0, upper=360, deg=True))
print(solve_trig("2*sin(x)^2 - 1 = 0", lower=0, upper=360, deg=True))

# %% [markdown]
# In radians (the default):

# %%
print(solve_trig("sin(x) = 0", lower=0, upper=2 * pi))

# %% [markdown]
# ## a·sin x + b·cos x = R·sin(x + α)
#
# This rewrite is how you find the maximum of a mixed wave: it's just `R`.

# %%
h = harmonic_form(3, 4)
show(h)

# %%
plot("3*sin(x) + 4*cos(x)", "5*sin(x + 0.9273)",
     labels=["3sin x + 4cos x", "5 sin(x + α)"],
     domain=(0, 6.3), title="Same curve, two forms")

# %% [markdown]
# ## Solving triangles
#
# * **Sine rule** `a/sin A = b/sin B` — when you have a side and its opposite angle
# * **Cosine rule** `c² = a² + b² - 2ab cos C` — for SSS and SAS
#
# `solve_triangle` picks the right rule for whatever you give it.

# %%
show(solve_triangle(a=3, b=4, c=5), label="SSS — a right triangle")

# %%
show(solve_triangle(a=5, b=7, C=120), label="SAS — obtuse included angle")

# %%
show(solve_triangle(a=10, A=30, B=45), label="ASA")

# %% [markdown]
# ### The ambiguous case (SSA)
#
# Two sides and a *non-included* angle can describe two different triangles.
# The result carries a note when that happens.

# %%
show(solve_triangle(a=7, b=10, A=30))

# %% [markdown]
# ## Bearings
#
# Measured clockwise from north — the navigation convention, not the maths one.

# %%
print(bearing((0, 0), (0, 1)), "= due north")
print(bearing((0, 0), (1, 1)), "= north-east")
print(bearing((0, 0), (-1, 0)), "= due west")

# %% [markdown]
# ## Radians, arcs and sectors
#
# In radians, arc length is just `rθ` and sector area `½r²θ` — the reason
# radians exist.

# %%
show(arc(radius=6, angle=60), label="sector of radius 6, angle 60°")
