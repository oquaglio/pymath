# %% [markdown]
# # Chain rule — worked example of the pattern
#
# This file exists to show the workflow, including what a *wrong* attempt looks
# like. Delete it once you've got the rhythm.
#
# The rule: `dy/dx = dy/du × du/dx`. Differentiate the outside, then multiply by
# the derivative of the inside.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## 1. Differentiate y = (3x + 1)⁵
#
# **My working:**
#
# Let u = 3x + 1, so y = u⁵.
#
# * dy/du = 5u⁴
# * du/dx = 3
# * dy/dx = 5u⁴ × 3 = 15(3x + 1)⁴
#
# Answer: `15(3x + 1)⁴`

# %%
mine = sym("15*(3x + 1)^4")

# %%
theirs = diff("(3x + 1)^5")
print("theirs:", theirs)
print("mine:  ", mine)
print("match: ", simplify(mine - theirs) == 0)

# %% [markdown]
# ✅ Correct — and here `==` would also have worked, because SymPy tidies simple
# products into the same internal form.
#
# It doesn't always. Write your answer factored while SymPy writes it expanded,
# or reach for a trig identity, and `==` says False on maths that is identical:

# %%
for a, b in [("x*(x + 4)", "x^2 + 4x"), ("sin(2x)", "2*sin(x)*cos(x)")]:
    A, B = sym(a), sym(b)
    print(f"{a:12} vs {b:20}  == says {A == B},  simplify says {simplify(A - B) == 0}")

# %% [markdown]
# That's why the check below is always `simplify(mine - theirs) == 0`. It costs
# nothing when `==` would have worked, and saves you from marking a correct
# answer wrong.

# %% [markdown]
# ## 2. Differentiate y = sin(x²)
#
# **My working:**
#
# Let u = x², so y = sin u.
#
# * dy/du = cos u
# * du/dx = 2x
# * dy/dx = cos(x²) × 2x = 2x·cos(x²)
#
# Answer: `2x cos(x²)`

# %%
mine = sym("2x*cos(x^2)")

# %%
theirs = diff("sin(x^2)")
print("theirs:", theirs)
print("match: ", simplify(mine - theirs) == 0)

# %% [markdown]
# ✅ Correct.

# %% [markdown]
# ## 3. Differentiate y = e^(3x²)
#
# **My working:**
#
# Let u = 3x², so y = eᵘ.
#
# * dy/du = eᵘ
# * du/dx = 6x
# * dy/dx = e^(3x²)
#
# Answer: `e^(3x²)`  ← deliberately wrong, to show what a miss looks like

# %%
mine = sym("exp(3x^2)")

# %%
theirs = diff("exp(3x^2)")
print("theirs:", theirs)
print("mine:  ", mine)
print("match: ", simplify(mine - theirs) == 0)

# %% [markdown]
# ❌ Wrong — I wrote down `du/dx = 6x` and then never multiplied by it.
#
# The cause isn't "I don't know the chain rule", it's **stopping one step
# early on the outer derivative**. That goes in `mistakes.md` under its cause,
# where it can join the other times I do the same thing.

# %%
corrected = sym("6x*exp(3x^2)")
print("match:", simplify(corrected - theirs) == 0)

# %%
