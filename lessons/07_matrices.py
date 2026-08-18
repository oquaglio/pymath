# %% [markdown]
# # 7. Matrices and linear algebra
#
# A matrix is a grid of numbers — and, more usefully, a *transformation* of
# space.

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## The basics

# %%
A = matrix([[1, 2], [3, 4]])
B = matrix([[0, 1], [1, 0]])
print(A)
print("A + B =", (A + B).tolist())
print("A × B =", (A * B).tolist())
print("B × A =", (B * A).tolist(), "← order matters!")

# %% [markdown]
# ## Determinant and inverse
#
# The determinant is the area scale factor of the transformation. Zero means the
# transformation squashes space flat — and cannot be undone, so there's no
# inverse.

# %%
print("det A =", determinant(A))
print("A⁻¹ =", inverse(A).tolist())
print("A⁻¹A =", (inverse(A) * A).tolist())

# %%
print("det of a singular matrix:", determinant([[1, 2], [2, 4]]))
try:
    inverse([[1, 2], [2, 4]])
except ValueError as err:
    print("→", err)

# %% [markdown]
# ## Simultaneous equations as matrices
#
# `2x + y = 5` and `x - y = 1` becomes `Ax = b`, solved by `x = A⁻¹b`.

# %%
solution = solve_linear([[2, 1], [1, -1]], [5, 1])
print("x, y =", list(solution))

# %% [markdown]
# Three unknowns, same method — this is where matrices start beating
# substitution:

# %%
print(list(solve_linear([[1, 1, 1], [2, -1, 1], [1, 2, -1]], [6, 3, 2])))

# %% [markdown]
# ## Row reduction
#
# Gaussian elimination, automated. The rank tells you how many genuinely
# independent equations you have.

# %%
show(rref([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))

# %% [markdown]
# Rank 2 from three rows means one equation was redundant — the system is
# under-determined.

# %% [markdown]
# ## Matrices as transformations
#
# Multiply a point by a matrix and it moves. These are the standard ones:

# %%
import sympy as sp

point = sp.Matrix([1, 0])
for kind, params in [("rotation", {"angle": 90}), ("reflection", {"axis": "y"}),
                     ("scale", {"sx": 2, "sy": 3}), ("shear", {"kx": 1})]:
    T = transform_2d(kind, **params)
    print(f"{kind:11} {T.tolist()} maps (1,0) → {list(T * point)}")

# %% [markdown]
# Transformations compose by multiplication — and the order matters, exactly as
# it does physically:

# %%
rot = transform_2d("rotation", angle=90)
ref = transform_2d("reflection", axis="x")
print("rotate then reflect:", list(ref * rot * point))
print("reflect then rotate:", list(rot * ref * point))

# %% [markdown]
# ## Eigenvalues and eigenvectors
#
# An eigenvector is a direction the transformation doesn't turn — it only
# stretches it. The eigenvalue is the stretch factor. This is the idea behind
# PCA, PageRank, and the stability of physical systems.

# %%
show(eigen([[2, 1], [1, 2]]))

# %% [markdown]
# Read it directly: the vector (1, 1) is scaled by 3, and (1, −1) by 1.

# %%
M = matrix([[2, 1], [1, 2]])
print(list(M * sp.Matrix([1, 1])), "= 3 × (1, 1)")
print(list(M * sp.Matrix([1, -1])), "= 1 × (1, -1)")

# %% [markdown]
# ### Diagonalisation
#
# `M = P D P⁻¹` with D diagonal. Powers then become trivial: `M^n = P D^n P⁻¹`.

# %%
e = eigen([[2, 1], [1, 2]])
P, D = e["P"], e["D"]
print("P D P⁻¹ =", (P * D * P.inv()).tolist())
print("M¹⁰ =", (P * D**10 * P.inv()).tolist())

# %% [markdown]
# ## NumPy: when the matrices get big
#
# SymPy is exact but slow. For anything numeric or large, NumPy is the tool —
# and it's what every data library uses underneath.

# %%
import numpy as np

rng = np.random.default_rng(0)
big = rng.random((500, 500))
print("shape:", big.shape)
print("det (log scale):", np.linalg.slogdet(big))
print("solved 500×500 system in one call:", np.linalg.solve(big, rng.random(500))[:3], "...")

# %% [markdown]
# ### Least squares
#
# More equations than unknowns usually means no exact solution — so find the
# one with the smallest total error. This *is* linear regression.

# %%
xs = np.array([1, 2, 3, 4, 5])
ys = np.array([2.1, 3.9, 6.2, 7.8, 10.1])
design = np.column_stack([xs, np.ones_like(xs)])  # columns: x, 1
slope, intercept = np.linalg.lstsq(design, ys, rcond=None)[0]
print(f"y = {slope:.4f}x + {intercept:.4f}")

# %%
scatter(xs, ys, fit="linear", title="Least squares = solving an overdetermined system")
