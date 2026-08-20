# %% [markdown]
# # <topic> — <date>
#
# Copy this file to start a new problem set:
# `cp workbook/_template.py workbook/calculus/quotient-rule.py`
#
# Problem 1 is filled in to show the shape. Replace it with your own.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## 1. Differentiate y = x³ + 2x
#
# **My working** — written *before* running the check below:
#
# Power rule term by term: bring the index down, drop it by one.
#
# * d/dx x³ = 3x²
# * d/dx 2x = 2
#
# Answer: `3x² + 2`

# %%
mine = sym("3x^2 + 2")

# %%
theirs = diff("x^3 + 2x")
print("theirs:", theirs)
print("mine:  ", mine)
print("match: ", simplify(mine - theirs) == 0)

# %% [markdown]
# ✅ / ❌ — if wrong, add the *cause* to `workbook/mistakes.md`, not the answer.

# %% [markdown]
# ## 2. <your question here>
#
# **My working:**
#
# Answer:

# %%
mine = sym("0")  # ← your answer

# %%
theirs = sym("0")  # ← e.g. diff("...") or integrate("...") or solve("...")
print("theirs:", theirs)
print("mine:  ", mine)
print("match: ", simplify(mine - theirs) == 0)

# %% [markdown]
# ✅ / ❌

# %% [markdown]
# ---
# ## Drill generator
#
# You have a CAS, so you can make your own practice sets instead of hunting for
# them. Run this, work the problems on paper, then reveal.

# %%
import random

problems = []
for _ in range(5):
    a, b, power = random.randint(2, 6), random.randint(1, 9), random.randint(2, 5)
    question = f"({a}x + {b})^{power}"
    problems.append((question, diff(question)))
    print("differentiate", question)

# %%
# Reveal — run only after you've attempted all five.
for question, answer in problems:
    print(f"{question:>16}  →  {answer}")
