# %% [markdown]
# # 11. Beyond Year 12
#
# Where these tools go next: multivariable calculus, numerical methods, linear
# algebra in anger, and a look at how the libraries themselves work.

# %%
import numpy as np
import sympy as sp

from pymath import *  # noqa: F403

# %% [markdown]
# ## Multivariable calculus
#
# ### Partial derivatives
#
# Differentiate with respect to one variable, holding the others fixed.

# %%
f = sym("x^2*y + 3*x*y^3")
print("∂f/∂x =", sp.diff(f, x))
print("∂f/∂y =", sp.diff(f, y))
print("∂²f/∂x∂y =", sp.diff(f, x, y))

# %% [markdown]
# ### The gradient vector
#
# `∇f` points in the direction of steepest ascent — the object every
# machine-learning optimiser follows downhill.

# %%
grad = sp.Matrix([sp.diff(f, x), sp.diff(f, y)])
print("∇f =", list(grad))
print("at (1, 2):", list(grad.subs({x: 1, y: 2})))

# %%
plot_surface("x^2 + y^2", title="Bowl: the gradient points outwards and up")

# %% [markdown]
# ### Finding a minimum by gradient descent
#
# Step downhill, repeatedly. Ten lines of code, and it is genuinely how neural
# networks are trained.

# %%
surface = sym("(x - 3)^2 + (y + 1)^2")
grad_f = [sp.lambdify((x, y), sp.diff(surface, v), "numpy") for v in (x, y)]

position = np.array([0.0, 0.0])
for step in range(60):
    gradient_here = np.array([g(*position) for g in grad_f])
    position = position - 0.1 * gradient_here
print("converged to:", position.round(6), "— the true minimum is (3, -1)")

# %% [markdown]
# ### Double integrals
#
# Volume under a surface, integrating one variable then the other.

# %%
print(sp.integrate(sp.integrate(x * y, (x, 0, 1)), (y, 0, 2)))
print(sp.integrate(x**2 + y**2, (x, 0, 1), (y, 0, 1)))

# %% [markdown]
# ## Numerical methods
#
# Most real equations have no closed-form answer. These are the algorithms that
# get numbers anyway — and every one is worth implementing once yourself.
#
# ### Newton–Raphson
#
# Follow the tangent to where it crosses the axis, repeat. It roughly doubles
# the number of correct digits each step.

# %%
def newton(expr, guess, steps=6):
    fn, dfn = func(expr), func(diff(expr))
    value = float(guess)
    for _ in range(steps):
        value = value - fn(value) / dfn(value)
        print(f"  {value:.15f}")
    return value

print("root of cos(x) - x:")
newton("cos(x) - x", 1.0)
print("√2 via x² - 2:")
newton("x^2 - 2", 1.0)

# %% [markdown]
# ### Bisection
#
# Slower but unbreakable: if the sign changes across an interval, a root is
# inside it. Halve, repeat.

# %%
def bisect(expr, lower, upper, steps=40):
    fn = func(expr)
    for _ in range(steps):
        mid = (lower + upper) / 2
        if fn(lower) * fn(mid) <= 0:
            upper = mid
        else:
            lower = mid
    return (lower + upper) / 2

print(bisect("cos(x) - x", 0, 2))

# %% [markdown]
# SciPy has both, plus better ones:

# %%
from scipy import optimize

print(optimize.brentq(lambda v: np.cos(v) - v, 0, 2))
print(optimize.minimize_scalar(lambda v: (v - 3) ** 2 + 1))

# %% [markdown]
# ### Numerical integration compared
#
# Simpson's rule beats the trapezoidal rule for the same number of strips,
# because it fits parabolas instead of straight lines.

# %%
from scipy import integrate as spi

exact = float(integrate("exp(-x^2)", lower=0, upper=2))
xs = np.linspace(0, 2, 101)
ys = np.exp(-(xs**2))
print(f"exact (erf):  {exact:.12f}")
print(f"trapezoid:    {np.trapezoid(ys, xs):.12f}")
print(f"simpson:      {spi.simpson(ys, x=xs):.12f}")
print(f"adaptive quad:{spi.quad(lambda v: np.exp(-v**2), 0, 2)[0]:.12f}")

# %% [markdown]
# ### Solving ODEs numerically
#
# When `dsolve` can't find a formula, integrate step by step instead.

# %%
from scipy.integrate import solve_ivp


# Damped oscillator: y'' + 0.3y' + y = 0, written as two first-order equations.
def damped(t, state):
    displacement, velocity = state
    return [velocity, -0.3 * velocity - displacement]

sol = solve_ivp(damped, (0, 40), [1.0, 0.0], dense_output=True, max_step=0.05)

import matplotlib.pyplot as plt

p = theme.palette()
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(sol.t, sol.y[0], color=p.color(0), label="displacement")
ax.plot(sol.t, sol.y[1], color=p.color(1), label="velocity")
ax.set_title("Damped harmonic oscillator")
ax.set_xlabel("time")
ax.set_ylabel("value")
ax.legend()
fig.savefig("plots/damped_oscillator.png", facecolor=p.page, bbox_inches="tight")
print("saved plots/damped_oscillator.png")

# %% [markdown]
# ## Linear algebra, applied
#
# ### Markov chains
#
# A transition matrix raised to a power gives the long-run distribution — the
# steady state is the eigenvector for eigenvalue 1.

# %%
transition = np.array([[0.9, 0.2], [0.1, 0.8]])  # columns: from-state
state = np.array([1.0, 0.0])
for step in [1, 5, 20, 100]:
    print(f"after {step:>3} steps: {np.linalg.matrix_power(transition, step) @ state}")

values, vectors = np.linalg.eig(transition)
steady = vectors[:, np.argmin(np.abs(values - 1))]
print("steady state:", (steady / steady.sum()).real)

# %% [markdown]
# ### Principal component analysis
#
# Eigenvectors of the covariance matrix are the directions the data actually
# varies in.

# %%
rng = np.random.default_rng(0)
cloud = rng.multivariate_normal([0, 0], [[3, 2], [2, 2]], size=300)
covariance = np.cov(cloud.T)
values, vectors = np.linalg.eigh(covariance)
print("covariance:\n", covariance.round(3))
print("principal direction:", vectors[:, -1].round(3),
      "explaining", f"{values[-1] / values.sum():.1%}", "of the variance")

# %% [markdown]
# ## Fourier series
#
# Any periodic function is a sum of sines and cosines. Add more terms and a
# square wave emerges from smooth curves.

# %%
terms = [f"sin({k}*x)/{k}" for k in range(1, 10, 2)]
partial_sums = ["+".join(terms[:k]) for k in (1, 2, 5)]
plot(*partial_sums, labels=["1 term", "2 terms", "5 terms"],
     domain=(-6.3, 6.3), title="Fourier series approaching a square wave")

# %% [markdown]
# The FFT does this numerically — it's how audio, images and signal processing
# work.

# %%
sample_rate = 500
t_axis = np.linspace(0, 1, sample_rate, endpoint=False)
signal = np.sin(2 * np.pi * 50 * t_axis) + 0.5 * np.sin(2 * np.pi * 120 * t_axis)
spectrum = np.abs(np.fft.rfft(signal))
freqs = np.fft.rfftfreq(len(signal), 1 / sample_rate)
peaks = freqs[np.argsort(spectrum)[-2:]]
print("frequencies recovered from the signal:", sorted(peaks), "Hz")

# %%
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(freqs, spectrum, color=p.color(0))
ax.set_title("Frequency spectrum: two spikes, at 50 Hz and 120 Hz")
ax.set_xlabel("frequency (Hz)")
ax.set_ylabel("amplitude")
fig.savefig("plots/fft_spectrum.png", facecolor=p.page, bbox_inches="tight")
print("saved plots/fft_spectrum.png")

# %% [markdown]
# ## Where to go from here
#
# * **SymPy docs** — the CAS you've been using: <https://docs.sympy.org>
# * **SciPy lecture notes** — the numeric stack: <https://scipy-lectures.org>
# * **3Blue1Brown** — *Essence of linear algebra* and *Essence of calculus*, for
#   the geometric intuition behind everything in lessons 4–7
# * **Project Euler** — maths problems that need code: <https://projecteuler.net>
#
# And keep extending `pymath` — adding a function you needed is the fastest way
# to learn both the maths and the library.
