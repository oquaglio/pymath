# %% [markdown]
# # 6. Coordinate geometry, mensuration and vectors

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Points and lines

# %%
A, B = (1, 2), (5, 10)
print("distance:", distance(A, B))
print("midpoint:", midpoint(A, B))
print("gradient:", gradient(A, B))

# %%
show(line(A, B), label="line through (1,2) and (5,10)")

# %% [markdown]
# Parallel lines share a gradient; perpendicular gradients multiply to −1.

# %%
print(perpendicular := geometry.perpendicular_through((1, 2), 2))
print("check:", diff(perpendicular) * 2)

# %%
plot("2*x + 1", "-x/2 + 5/2", labels=["y = 2x + 1", "perpendicular"],
     domain=(-3, 5), title="Perpendicular gradients multiply to -1")

# %% [markdown]
# ## Circles
#
# `(x - h)² + (y - k)² = r²`. Expanding gives the general form; completing the
# square gets you back.

# %%
show(circle(centre=(1, 2), radius=3))

# %%
show(geometry.circle_from_general("x^2 + y^2 - 2x - 4y - 4"), label="completed square")

# %%
plot_implicit("x^2 + y^2 - 2*x - 4*y - 4 = 0", domain=(-4, 6), rangey=(-3, 6),
              title="Centre (1, 2), radius 3")

# %% [markdown]
# ## Areas and volumes
#
# The shoelace formula gets the area of *any* polygon from its vertices — no
# need to split it into triangles.

# %%
print(polygon_area([(0, 0), (4, 0), (4, 3)]))
print(polygon_area([(0, 0), (4, 0), (5, 3), (1, 4)]))

# %%
show(solid("sphere", r=3))
show(solid("cone", r=3, h=4))
show(solid("cylinder", r=2, h=7))

# %% [markdown]
# Exact answers stay in terms of π. Convert when you need a number:

# %%
v = solid("sphere", r=3)["volume"]
print(v, "≈", float(v))

# %% [markdown]
# ## Vectors
#
# A vector has magnitude *and* direction. Written as a column.

# %%
u = vector(3, 4)
v = vector(1, 2)
print("u =", list(u), " |u| =", magnitude(u))
print("u + v =", list(u + v))
print("3u =", list(3 * u))
print("unit vector:", list(unit(u)))

# %% [markdown]
# ### Dot product
#
# `a·b = |a||b|cos θ`. Zero means perpendicular — the quickest test there is.

# %%
print(dot(vector(1, 2), vector(3, 4)))
print(dot(vector(1, 0), vector(0, 1)), "→ perpendicular")
print("angle:", angle_between(vector(1, 0), vector(1, 1)), "degrees")

# %% [markdown]
# ### Cross product (3D)
#
# Gives a vector perpendicular to both — and its magnitude is the area of the
# parallelogram they span.

# %%
i_hat, j_hat = vector(1, 0, 0), vector(0, 1, 0)
print("i × j =", list(cross(i_hat, j_hat)), "= k")
print("area of parallelogram:", magnitude(cross(vector(1, 2, 0), vector(3, 1, 0))))

# %% [markdown]
# ### Projection
#
# The shadow one vector casts along another — the basis of resolving forces into
# components.

# %%
print(list(projection(vector(3, 4), vector(1, 0))))  # horizontal component

# %% [markdown]
# ## A worked problem: is this triangle right-angled?

# %%
P, Q, R = (1, 1), (4, 5), (8, 2)
PQ = vector(Q[0] - P[0], Q[1] - P[1])
QR = vector(R[0] - Q[0], R[1] - Q[1])
PR = vector(R[0] - P[0], R[1] - P[1])
print("|PQ| =", magnitude(PQ), " |QR| =", magnitude(QR), " |PR| =", magnitude(PR))
print("PQ · QR =", dot(PQ, QR), "→ right angle at Q" if dot(PQ, QR) == 0 else "→ not at Q")
print("angle at Q:", angle_between(PQ, QR), "degrees")
print("area:", polygon_area([P, Q, R]))

# %% [markdown]
# ## Parametric curves
#
# `x = f(t), y = g(t)` describes motion — where you are at time t. It can trace
# curves that fail the vertical line test.

# %%
plot_parametric("cos(t)", "sin(t)", title="Unit circle")

# %%
plot_parametric("t - sin(t)", "1 - cos(t)", trange=(0, 12.6), title="Cycloid")

# %% [markdown]
# Projectile motion is parametric: constant horizontal speed, accelerating
# vertically.

# %%
plot_parametric("20*t", "20*t - 4.9*t^2", trange=(0, 4.1),
                title="Projectile: 20 m/s at 45°")

# %% [markdown]
# ## Polar coordinates
#
# A point as (distance from origin, angle) instead of (x, y).

# %%
plot_polar("1 + cos(theta)", title="Cardioid")

# %%
plot_polar("sin(3*theta)", title="Three-petal rose")

# %%
plot_polar("theta/3", trange=(0, 18.8), title="Archimedean spiral")
