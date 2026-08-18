# %% [markdown]
# # 10. The graphing gallery
#
# Every kind of plot in the toolkit, in one place. Each call writes a file under
# `plots/` and returns the path; pass `show=True` in a notebook for inline
# output.
#
# **The chart rules this project follows** — worth absorbing, they apply to any
# chart you ever make:
#
# * curves take colours in a fixed order from a colourblind-safe palette,
#   never a random cycle;
# * two or more curves always get a legend;
# * the grid is faint — it's chrome, not data;
# * magnitude uses one hue light→dark, never a rainbow;
# * never a second y-axis (two scales on one chart mislead; use two charts).

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Basic function plots

# %%
plot("x^2", domain=(-5, 5), title="A single parabola")

# %%
plot("sin(x)", "cos(x)", "sin(2*x)", domain=(-6.3, 6.3), title="Three waves")

# %% [markdown]
# Asymptotes are detected and *not* joined by a fake vertical line — a mistake
# most naive plotting code makes:

# %%
plot("1/(x - 2)", domain=(-5, 9), title="No fake line through the asymptote")

# %%
plot("tan(x)", domain=(-6.3, 6.3), ylim=(-8, 8), title="Tangent")

# %% [markdown]
# ## Annotated analysis
#
# Roots, turning points and asymptotes marked automatically.

# %%
plot_analysis("x^3 - 6*x^2 + 9*x", domain=(-1, 5))

# %%
plot_analysis("(x^2 - 4)/(x - 1)", domain=(-8, 10))

# %% [markdown]
# ## Calculus visualised

# %%
plot_tangent("x^2", 2, domain=(-3, 5))

# %%
plot_integral("x^2", 0, 3)

# %%
plot_integral("sin(x)", 0, 6.283, title="Signed area cancels over a full period")

# %%
plot_slope_field("y*(1 - y)", xrange=(0, 6), yrange=(-0.5, 2),
                 solutions=[(0, 0.1), (0, 1.8)], title="Logistic growth")

# %% [markdown]
# ## Parametric and polar

# %%
plot_parametric("cos(t)", "sin(t)", title="Circle")

# %%
plot_parametric("sin(3*t)", "sin(4*t)", trange=(0, 6.3), title="Lissajous 3:4")

# %%
plot_polar("1 + cos(theta)", title="Cardioid")

# %%
plot_polar("cos(5*theta)", title="Five-petal rose")

# %% [markdown]
# ## Implicit relations
#
# Curves that aren't functions of x — an ellipse, or something stranger.

# %%
plot_implicit("x^2/9 + y^2/4 = 1", domain=(-4, 4), rangey=(-3, 3), title="Ellipse")

# %%
plot_implicit("x^2 - y^2 = 1", title="Hyperbola")

# %%
plot_implicit("(x^2 + y^2 - 1)^3 = x^2*y^3", domain=(-1.5, 1.5), rangey=(-1.5, 1.5),
              title="Heart curve")

# %% [markdown]
# ## 3D and contours
#
# The surface and the contour map show the same function two ways — the contour
# map is what a topographic map does for a hillside.

# %%
plot_surface("x^2 + y^2", title="Paraboloid")

# %%
plot_surface("x^2 - y^2", title="Saddle")

# %%
plot_contour("sin(x)*cos(y)", title="Contours of sin(x)cos(y)")

# %% [markdown]
# ## Statistical charts

# %%
import numpy as np

rng = np.random.default_rng(42)
sample = rng.normal(loc=170, scale=8, size=400)

# %%
histogram(sample, bins=20, title="Simulated heights", xlabel="cm")

# %%
boxplot([rng.normal(170, 8, 200), rng.normal(178, 6, 200)],
        labels=["group A", "group B"], title="Comparing two groups")

# %%
scatter([1, 2, 3, 4, 5, 6], [2.2, 4.1, 5.8, 8.3, 9.9, 12.2], fit="linear",
        title="Scatter with least-squares line")

# %%
plot_normal(0, 1, shade=(-1.96, 1.96), title="Standard normal: the middle 95%")

# %% [markdown]
# ## Interactive versions
#
# Plotly writes a standalone HTML file you can open in a browser: hover for
# exact values, drag to zoom, and rotate 3D surfaces.

# %%
interactive("x^2", "x^3", "sin(x)", domain=(-4, 4), title="Hover to read values")

# %%
interactive_surface("sin(sqrt(x^2 + y^2))", xrange=(-8, 8), yrange=(-8, 8),
                    title="Ripple — drag to rotate")

# %% [markdown]
# ## Dark mode
#
# The whole palette has a dark variant, re-stepped for a dark background rather
# than naively inverted.

# %%
theme.use("dark")
plot("sin(x)", "cos(x)", domain=(-6.3, 6.3), title="Dark mode")

# %%
theme.use("light")  # switch back

# %% [markdown]
# ## Building your own charts
#
# Under the hood it's plain Matplotlib. Take the palette and go:

# %%
import matplotlib.pyplot as plt

p = theme.palette()
xs = np.linspace(0, 10, 200)
fig, ax = plt.subplots(figsize=(8, 4.5))
for i, freq in enumerate([1, 2, 3]):
    ax.plot(xs, np.sin(freq * xs) / freq, color=p.color(i), label=f"sin({freq}x)/{freq}")
ax.set_title("Building up a square wave")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
fig.savefig("plots/custom_chart.png", facecolor=p.page, bbox_inches="tight")
print("saved plots/custom_chart.png")
