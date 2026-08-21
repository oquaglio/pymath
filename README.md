# pymath

A programmable graphics calculator for learning maths — roughly the capability of
a Casio ClassWiz CG-100, except you can read the source, extend it, and it shows
exact answers instead of ten decimal places.

Two things at once: a **maths curriculum** (Year 12 → early university) and a
**tour of the Python scientific stack** (SymPy, NumPy, SciPy, Matplotlib,
Plotly, pandas).

```python
>>> from pymath import *
>>> solve("x^2 - 5x + 6 = 0")
[2, 3]
>>> integrate("x^2", lower=0, upper=3)
9
>>> stationary_points("x^3 - 3x")
[{'x': -1, 'y': 2, 'nature': 'maximum', ...}, {'x': 1, 'y': -2, 'nature': 'minimum', ...}]
>>> plot_analysis("x^3 - 3x", domain=(-3, 3))
PosixPath('plots/analysis_of_x_3_-_3_x.png')
```

## Setup

Needs [uv](https://docs.astral.sh/uv/). Everything else installs itself.

```bash
uv sync --all-extras         # create .venv and install (Jupyter + gmpy2)
uv run pytest                # 163 tests, including every docstring example
```

## Three ways to use it

### 1. The lessons

Twelve lessons in [lessons/](lessons/), each a runnable script **and** a Jupyter
notebook (they're [jupytext](https://jupytext.readthedocs.io) files, so Jupyter
opens the `.py` directly — no conversion step, no notebook JSON in git).

```bash
uv run jupyter lab lessons/     # then right-click a .py → Open With → Notebook
uv run python lessons/04_differentiation.py    # or just run it
```

| | Lesson | Covers |
|---|---|---|
| 01 | Getting started | the four libraries, exact vs numeric, your first graph |
| 02 | Algebra and functions | solving, discriminants, polynomials, logs, transformations |
| 03 | Trigonometry | exact values, identities, equations over a domain, triangles |
| 04 | Differentiation | first principles, the rules, tangents, curve sketching, optimisation |
| 05 | Integration | techniques, area, volumes of revolution, numeric methods, ODEs |
| 06 | Geometry and vectors | coordinate geometry, mensuration, dot/cross products, parametrics |
| 07 | Matrices | determinants, transformations, eigenvalues, least squares |
| 08 | Statistics | distributions, regression, confidence intervals, hypothesis tests |
| 09 | Sequences and complex numbers | series, convergence, Taylor, De Moivre |
| 10 | Graphing gallery | every plot type in one place |
| 11 | Beyond Year 12 | partial derivatives, gradient descent, Newton–Raphson, PCA, Fourier |
| 12 | High precision | `decimal`, `Fraction`, `mpmath`, `gmpy2` (GMP/MPFR), where floats break |

### 2. The terminal calculator

```bash
uv run pymath solve "x^2 - 5x + 6 = 0"
uv run pymath diff "sin(x)*x^2"
uv run pymath integrate "x^2" --from 0 --to 3
uv run pymath analyse "x^3 - 6x^2 + 9x"        # full curve sketch + graph
uv run pymath plot "x^2" "2x+1" --domain -5:5
uv run pymath plot "sin(x)" --html             # interactive, opens in a browser
uv run pymath triangle --a 3 --b 4 --C 90
uv run pymath trigsolve "sin(x) = 1/2" --from 0 --to 360
uv run pymath statistics 2 4 4 4 5 5 7 9
uv run pymath repl                             # everything pre-imported
```

`uv run pymath --help` lists the lot.

### 3. As a library

```python
from pymath import calculus, plotting     # or: from pymath import *
```

| Module | What's in it |
|---|---|
| `algebra` | solving, factorising, quadratics, polynomials, inequalities |
| `calculus` | limits, derivatives, integrals, series, ODEs, numeric fallbacks |
| `trig` | exact values, identities, trig equations, triangle solving |
| `geometry` | coordinate geometry, mensuration, vectors |
| `linalg` | matrices, determinants, eigenvalues, transformations |
| `stats` | descriptive stats, distributions, regression, tests |
| `sequences` | sequences, series, complex numbers |
| `numbertheory` | primes, factors, fractions, bases, modular arithmetic |
| `plotting` | every kind of graph |
| `theme` | the shared chart palette |

## Graphing

Plot functions write a PNG to `plots/` and return the path, so the same call
works from a terminal, a script, or a notebook (pass `show=True` for inline).

```python
plot("x^2", "2x + 1", domain=(-5, 5))         # several functions at once
plot_analysis("x^3 - 3x")                      # roots + turning points marked
plot_integral("sin(x)", 0, 3.14159)            # shaded area under a curve
plot_tangent("x^2", 3)                         # curve with its tangent
plot_parametric("cos(t)", "sin(t)")            # x = f(t), y = g(t)
plot_polar("1 + cos(theta)")                   # r = f(θ)
plot_implicit("x^2 + y^2 = 25")                # relations that aren't functions
plot_surface("x^2 - y^2")                      # 3D z = f(x, y)
plot_contour("sin(x)*cos(y)")                  # the same, from above
plot_slope_field("x - y", solutions=[(0, 0)])  # direction field for an ODE
histogram(data); boxplot(data); scatter(xs, ys, fit="linear"); plot_normal(100, 15)

interactive("x^2", "sin(x)")                   # Plotly: hover, zoom, pan
interactive_surface("x^2 - y^2")               # rotate in a browser
theme.use("dark")                              # dark palette for every later plot
```

Charts follow a fixed set of rules — a colourblind-safe palette assigned in
slot order, a legend whenever there's more than one curve, a recessive grid,
one hue light→dark for magnitude, and never a second y-axis. Lesson 10 explains
why each one matters.

## Design notes

**Exact by default.** `solve("x^2 = 2")` gives `[-√2, √2]`, not `[-1.414, 1.414]`.
Call `float()` when you want a decimal. Where no closed form exists,
`nintegrate` / `nderivative` / `nsolve` fall back to SciPy.

**Calculator shorthand.** `^` means power and `2x` means `2*x`, so you can type
expressions the way you'd write them.

**Degrees are explicit.** Every trig function takes `deg=True/False` rather than
a hidden mode setting — the most common source of wrong answers on a real
calculator.

**Precision is a choice.** Floats stop at ~17 digits. Lesson 12 covers the
ladder above that: `decimal` (C libmpdec, base 10, for money), `Fraction`
(exact, never rounds), `mpmath` (arbitrary-precision maths), and `gmpy2`
(bindings to GMP/MPFR — installed via `--extra precision`, and mpmath picks it
up automatically as a speedup).

**Symbols are real by default**, which lets SymPy simplify harder. `solve` works
around it internally so complex roots still appear when you want them.

## Development

```bash
uv run pytest              # tests + doctests
uv run ruff check .        # lint
uv add <package>           # add a dependency
make help                  # everything else
```
