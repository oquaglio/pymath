"""Graphing — the part a graphics calculator is actually for.

Every function returns the path of the PNG it wrote (under ``plots/``), so the
same call works in a terminal, a script or a notebook. Pass ``show=True`` in a
notebook to display inline instead.

Conventions kept throughout, from the project's chart rules:
  * curves take categorical colours in fixed slot order, never cycled;
  * two or more curves always get a legend;
  * the grid is recessive — it is chrome, not data;
  * there is never a second y-axis.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from . import theme
from .symbols import func, sym, x

PLOT_DIR = Path("plots")


def _slug(text: str) -> str:
    """Make a filename that is safe on every platform.

    Titles are maths, so they contain ``/``, ``*``, ``^`` and spaces — all of
    which either break paths or create surprise subdirectories.
    """
    keep = [ch if (ch.isalnum() or ch in "-_") else "_" for ch in text.lower().strip()]
    slug = "".join(keep).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug[:60] or "plot"


def _finish(fig, ax, title=None, xlabel="x", ylabel="y", legend=False,
            save: str | Path | None = None, show: bool = False):
    """Apply the shared chrome and write the file."""
    p = theme.palette()
    if title:
        ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if legend:
        ax.legend(loc="best")
    ax.set_axisbelow(True)
    if show:
        plt.show()
        return None
    if save:
        path = Path(save)
    else:
        # Fall back to whatever title the caller already set on the axes, so
        # every chart gets its own file instead of overwriting plot.png.
        # Titles are left-aligned by rcParams, and get_title() reads the centre
        # slot by default — so check every slot before giving up.
        existing = next((ax.get_title(loc) for loc in ("left", "center", "right")
                         if ax.get_title(loc)), "")
        path = PLOT_DIR / f"{_slug(title or existing or 'plot')}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor=p.page)
    plt.close(fig)
    return path


def _axes(figsize=(8, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


def _sample(expr, lo, hi, points=2000, var=x):
    """Evaluate an expression across a range, masking blow-ups near asymptotes.

    Without the mask, matplotlib draws a vertical line joining +inf to -inf
    across an asymptote — the classic fake line on a 1/x graph.
    """
    f = func(expr, var)
    xs = np.linspace(float(lo), float(hi), points)
    with np.errstate(all="ignore"):
        ys = np.asarray(f(xs), dtype=float) * np.ones_like(xs)
    ys[~np.isfinite(ys)] = np.nan
    finite = ys[np.isfinite(ys)]
    if finite.size:
        # Break the line wherever it jumps by more than half the visible spread.
        spread = np.percentile(finite, 99) - np.percentile(finite, 1)
        if spread > 0:
            jumps = np.abs(np.diff(ys)) > max(spread * 5, 1e-9)
            ys[1:][jumps] = np.nan
    return xs, ys


def plot(*exprs, domain=(-10, 10), labels=None, title=None, points=2000,
         ylim=None, save=None, show=False, var=x):
    """Plot one or more functions of x on the same axes.

    >>> plot("x^2", "2x + 1", domain=(-4, 4), title="Parabola vs line")  # doctest: +SKIP
    PosixPath('plots/parabola_vs_line.png')
    """
    fig, ax = _axes()
    p = theme.palette()
    lo, hi = domain
    for i, e in enumerate(exprs):
        xs, ys = _sample(e, lo, hi, points, var)
        label = labels[i] if labels else f"y = {sp.sstr(sym(e))}"
        ax.plot(xs, ys, color=p.color(i), label=label)
    _axis_lines(ax)
    if ylim:
        ax.set_ylim(*ylim)
    else:
        _autoscale_y(ax, exprs, lo, hi, var)
    return _finish(fig, ax, title or "plot", legend=len(exprs) > 1, save=save, show=show)


def _axis_lines(ax):
    """Draw the x and y axes through the origin, in axis (not series) ink."""
    p = theme.palette()
    ax.axhline(0, color=p.axis, linewidth=1.0, zorder=1)
    ax.axvline(0, color=p.axis, linewidth=1.0, zorder=1)


def _autoscale_y(ax, exprs, lo, hi, var):
    """Clip the y-range to where the interesting behaviour is.

    A single pole would otherwise stretch the axis to ±1e6 and flatten the curve.
    """
    samples = []
    for e in exprs:
        _, ys = _sample(e, lo, hi, 800, var)
        samples.append(ys[np.isfinite(ys)])
    values = np.concatenate([s for s in samples if s.size]) if any(s.size for s in samples) else None
    if values is None or values.size == 0:
        return
    low, high = np.percentile(values, [1, 99])
    if high - low <= 0:
        return
    pad = (high - low) * 0.15
    ax.set_ylim(low - pad, high + pad)


def plot_analysis(expr, domain=(-10, 10), title=None, save=None, show=False, var=x):
    """Plot a curve with its roots, turning points and asymptotes marked.

    This is the "sketch the graph, showing all key features" answer, drawn.
    """
    from .calculus import analyse

    info = analyse(expr, var)
    p = theme.palette()
    fig, ax = _axes()
    xs, ys = _sample(expr, *domain, var=var)
    ax.plot(xs, ys, color=p.color(0), label=f"y = {sp.sstr(sym(expr))}", zorder=3)
    _axis_lines(ax)
    _autoscale_y(ax, [expr], *domain, var)

    for root in info["x_intercepts"]:
        if root.is_real and domain[0] <= float(root) <= domain[1]:
            ax.plot(float(root), 0, "o", color=p.color(0), markersize=7,
                    markeredgecolor=p.surface, markeredgewidth=2, zorder=5)
            ax.annotate(f"({sp.nsimplify(root)}, 0)", (float(root), 0),
                        textcoords="offset points", xytext=(0, -18),
                        ha="center", fontsize=8, color=p.ink_secondary)

    for pt in info["stationary_points"]:
        if not pt["x"].is_real or not domain[0] <= float(pt["x"]) <= domain[1]:
            continue
        ax.plot(float(pt["x"]), float(pt["y"]), "o", color=p.color(1), markersize=7,
                markeredgecolor=p.surface, markeredgewidth=2, zorder=5)
        ax.annotate(pt["nature"], (float(pt["x"]), float(pt["y"])),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=8, color=p.ink_secondary)

    for asym in info["vertical_asymptotes"]:
        if asym.is_real and domain[0] <= float(asym) <= domain[1]:
            ax.axvline(float(asym), color=p.muted, linestyle="--", linewidth=1.0, zorder=2)
    for asym in info["horizontal_asymptotes"]:
        ax.axhline(float(asym), color=p.muted, linestyle="--", linewidth=1.0, zorder=2)

    return _finish(fig, ax, title or f"Analysis of {sp.sstr(sym(expr))}",
                   legend=True, save=save, show=show)


def plot_integral(expr, lower, upper, domain=None, title=None, save=None, show=False, var=x):
    """Shade the area a definite integral measures, and label its value.

    Area below the axis is shaded in the "negative" colour, since the integral
    counts it as negative.
    """
    from .calculus import integrate

    p = theme.palette()
    lo, hi = float(lower), float(upper)
    span = hi - lo
    domain = domain or (lo - span * 0.4, hi + span * 0.4)
    fig, ax = _axes()
    xs, ys = _sample(expr, *domain, var=var)
    ax.plot(xs, ys, color=p.color(0), label=f"y = {sp.sstr(sym(expr))}", zorder=3)

    shade_x = np.linspace(lo, hi, 800)
    shade_y = np.asarray(func(expr, var)(shade_x), dtype=float) * np.ones_like(shade_x)
    ax.fill_between(shade_x, 0, shade_y, where=shade_y >= 0, color=p.color(0),
                    alpha=0.22, zorder=2, label="positive area")
    if (shade_y < 0).any():
        ax.fill_between(shade_x, 0, shade_y, where=shade_y < 0, color=p.color(1),
                        alpha=0.22, zorder=2, label="negative area")
    _axis_lines(ax)
    value = integrate(expr, var, lower, upper)
    exact = sp.sstr(value)
    # Show the exact form only when it stays readable — a decimal bound turns
    # it into things like 1 - cos(314159/100000).
    shown = f"{exact}  ≈ {float(value):.6g}" if len(exact) <= 24 else f"{float(value):.6g}"
    ax.set_title(f"∫ {sp.sstr(sym(expr))} dx  from {lower} to {upper}  =  {shown}")
    return _finish(fig, ax, None, legend=True,
                   save=save or PLOT_DIR / f"{_slug('integral of ' + sp.sstr(sym(expr)))}.png",
                   show=show)


def plot_tangent(expr, point, domain=(-10, 10), title=None, save=None, show=False, var=x):
    """Plot a curve with its tangent at a point — derivative as gradient, visually."""
    from .calculus import tangent

    p = theme.palette()
    tan = tangent(expr, point, var)
    fig, ax = _axes()
    xs, ys = _sample(expr, *domain, var=var)
    ax.plot(xs, ys, color=p.color(0), label=f"y = {sp.sstr(sym(expr))}", zorder=3)
    txs, tys = _sample(tan, *domain, var=var)
    ax.plot(txs, tys, color=p.color(1), label=f"tangent: y = {sp.sstr(tan)}", zorder=3)
    y0 = float(sym(expr).subs(var, sp.nsimplify(point)))
    ax.plot(float(point), y0, "o", color=p.color(1), markersize=8,
            markeredgecolor=p.surface, markeredgewidth=2, zorder=5)
    _axis_lines(ax)
    _autoscale_y(ax, [expr], *domain, var)
    return _finish(fig, ax, title or f"Tangent at x = {point}", legend=True, save=save, show=show)


def plot_parametric(x_expr, y_expr, trange=(0, 2 * np.pi), title=None, points=1500,
                    save=None, show=False, param=None):
    """Plot ``x = f(t), y = g(t)`` — curves that fail the vertical line test.

    >>> plot_parametric("cos(t)", "sin(t)", title="Unit circle")  # doctest: +SKIP
    """
    from .symbols import t as default_t

    param = param or default_t
    p = theme.palette()
    ts = np.linspace(float(trange[0]), float(trange[1]), points)
    fx, fy = func(x_expr, param), func(y_expr, param)
    xs = np.asarray(fx(ts), dtype=float) * np.ones_like(ts)
    ys = np.asarray(fy(ts), dtype=float) * np.ones_like(ts)
    fig, ax = _axes(figsize=(6, 6))
    ax.plot(xs, ys, color=p.color(0), label=f"({sp.sstr(sym(x_expr))}, {sp.sstr(sym(y_expr))})")
    ax.set_aspect("equal", adjustable="datalim")
    _axis_lines(ax)
    return _finish(fig, ax, title or "Parametric curve", save=save, show=show)


def plot_polar(expr, trange=(0, 2 * np.pi), title=None, points=1500, save=None,
               show=False, param=None):
    """Plot ``r = f(θ)`` on polar axes — roses, cardioids, spirals.

    >>> plot_polar("1 + cos(theta)", title="Cardioid")  # doctest: +SKIP
    """
    from .symbols import theta as default_theta

    param = param or default_theta
    p = theme.palette()
    ths = np.linspace(float(trange[0]), float(trange[1]), points)
    rs = np.asarray(func(expr, param)(ths), dtype=float) * np.ones_like(ths)
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    ax.plot(ths, rs, color=p.color(0))
    ax.set_facecolor(p.surface)
    ax.grid(color=p.grid, linewidth=0.8)
    ax.tick_params(colors=p.muted)
    ax.set_title(title or f"r = {sp.sstr(sym(expr))}", color=p.ink, loc="left", pad=16)
    return _finish(fig, ax, None, xlabel="", ylabel="", save=save, show=show)


def plot_implicit(eq, domain=(-5, 5), rangey=(-5, 5), title=None, points=400,
                  save=None, show=False):
    """Plot an implicit relation like ``x^2 + y^2 = 25`` (a contour at level 0).

    >>> plot_implicit("x^2 + y^2 = 25")  # doctest: +SKIP
    """
    from .symbols import equation
    from .symbols import y as ysym

    p = theme.palette()
    e = equation(eq)
    expr = e.lhs - e.rhs
    f = sp.lambdify((x, ysym), expr, "numpy")
    xs = np.linspace(*domain, points)
    ys = np.linspace(*rangey, points)
    X, Y = np.meshgrid(xs, ys)
    with np.errstate(all="ignore"):
        Z = f(X, Y) * np.ones_like(X)
    fig, ax = _axes(figsize=(6, 6))
    ax.contour(X, Y, Z, levels=[0], colors=[p.color(0)], linewidths=1.8)
    ax.set_aspect("equal", adjustable="box")
    _axis_lines(ax)
    return _finish(fig, ax, title or f"{sp.sstr(e.lhs)} = {sp.sstr(e.rhs)}",
                   save=save, show=show)


def plot_surface(expr, xrange=(-5, 5), yrange=(-5, 5), title=None, points=80,
                 save=None, show=False):
    """3D surface ``z = f(x, y)``, drawn with a single-hue sequential ramp.

    Magnitude is a sequential encoding — one hue, light to dark. Never a rainbow.

    >>> plot_surface("x^2 + y^2")  # doctest: +SKIP
    """
    from matplotlib.colors import LinearSegmentedColormap

    from .symbols import y as ysym

    p = theme.palette()
    blues = LinearSegmentedColormap.from_list(
        "seq_blue", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#0d366b"]
    )
    f = sp.lambdify((x, ysym), sym(expr), "numpy")
    X, Y = np.meshgrid(np.linspace(*xrange, points), np.linspace(*yrange, points))
    with np.errstate(all="ignore"):
        Z = f(X, Y) * np.ones_like(X)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(X, Y, Z, cmap=blues, linewidth=0, antialiased=True, alpha=0.95)
    ax.set_facecolor(p.surface)
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.set_pane_color((0, 0, 0, 0))
    ax.set_zlabel("z", color=p.ink_secondary)
    ax.set_title(title or f"z = {sp.sstr(sym(expr))}", color=p.ink, loc="left")
    return _finish(fig, ax, None, save=save, show=show)


def plot_contour(expr, xrange=(-5, 5), yrange=(-5, 5), title=None, levels=14,
                 points=300, save=None, show=False):
    """Contour map of ``z = f(x, y)`` — the same surface seen from above."""
    from matplotlib.colors import LinearSegmentedColormap

    from .symbols import y as ysym

    p = theme.palette()
    blues = LinearSegmentedColormap.from_list(
        "seq_blue", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#0d366b"]
    )
    f = sp.lambdify((x, ysym), sym(expr), "numpy")
    X, Y = np.meshgrid(np.linspace(*xrange, points), np.linspace(*yrange, points))
    with np.errstate(all="ignore"):
        Z = f(X, Y) * np.ones_like(X)
    fig, ax = _axes(figsize=(7, 6))
    filled = ax.contourf(X, Y, Z, levels=levels, cmap=blues)
    ax.contour(X, Y, Z, levels=levels, colors=[p.surface], linewidths=0.6)
    bar = fig.colorbar(filled, ax=ax)
    bar.ax.tick_params(colors=p.muted)
    bar.outline.set_edgecolor(p.axis)
    return _finish(fig, ax, title or f"z = {sp.sstr(sym(expr))}", save=save, show=show)


def plot_slope_field(expr, xrange=(-4, 4), yrange=(-4, 4), density=20, solutions=None,
                     title=None, save=None, show=False):
    """Direction field for ``dy/dx = f(x, y)``, optionally with solution curves.

    Each dash shows the gradient a solution must have there; the curves thread
    through them.

    >>> plot_slope_field("x - y", solutions=[(0, 0), (0, 2)])  # doctest: +SKIP
    """
    from scipy.integrate import solve_ivp

    from .symbols import y as ysym

    p = theme.palette()
    f = sp.lambdify((x, ysym), sym(expr), "numpy")
    X, Y = np.meshgrid(np.linspace(*xrange, density), np.linspace(*yrange, density))
    with np.errstate(all="ignore"):
        slope = f(X, Y) * np.ones_like(X)
    norm = np.sqrt(1 + slope**2)
    fig, ax = _axes(figsize=(7, 6))
    ax.quiver(X, Y, 1 / norm, slope / norm, color=p.muted, angles="xy",
              headwidth=0, headlength=0, headaxislength=0, pivot="mid", scale=28)
    for i, (x0, y0) in enumerate(solutions or []):
        sol = solve_ivp(lambda tv, yv: f(tv, yv), (x0, xrange[1]), [y0],
                        dense_output=True, max_step=0.05)
        ax.plot(sol.t, sol.y[0], color=p.color(i), linewidth=2,
                label=f"through ({x0}, {y0})")
        back = solve_ivp(lambda tv, yv: f(tv, yv), (x0, xrange[0]), [y0],
                         dense_output=True, max_step=0.05)
        ax.plot(back.t, back.y[0], color=p.color(i), linewidth=2)
    ax.set_xlim(*xrange)
    ax.set_ylim(*yrange)
    return _finish(fig, ax, title or f"dy/dx = {sp.sstr(sym(expr))}",
                   legend=bool(solutions), save=save, show=show)


# --- statistical charts ------------------------------------------------------

def histogram(data, bins=10, title=None, xlabel="value", save=None, show=False):
    """Histogram with the mean marked."""
    p = theme.palette()
    arr = np.asarray(data, dtype=float)
    fig, ax = _axes()
    ax.hist(arr, bins=bins, color=p.color(0), edgecolor=p.surface, linewidth=2)
    ax.axvline(arr.mean(), color=p.color(1), linewidth=2, label=f"mean = {arr.mean():.3g}")
    ax.grid(axis="x", visible=False)
    return _finish(fig, ax, title or "Distribution", xlabel=xlabel, ylabel="frequency",
                   legend=True, save=save, show=show)


def boxplot(data, labels=None, title=None, save=None, show=False):
    """Box plot: median, quartiles, whiskers and outliers — the five-number summary."""
    p = theme.palette()
    groups = data if isinstance(data[0], (list, tuple, np.ndarray)) else [data]
    fig, ax = _axes()
    bp = ax.boxplot(groups, tick_labels=labels, patch_artist=True, widths=0.5)
    for i, box in enumerate(bp["boxes"]):
        box.set(facecolor=p.color(i % 8), alpha=0.35, edgecolor=p.color(i % 8), linewidth=1.8)
    for part in ("whiskers", "caps"):
        for item in bp[part]:
            item.set(color=p.axis, linewidth=1.2)
    for med in bp["medians"]:
        med.set(color=p.ink, linewidth=2)
    for fly in bp["fliers"]:
        fly.set(marker="o", markerfacecolor=p.critical, markeredgecolor=p.surface, markersize=6)
    ax.grid(axis="x", visible=False)
    return _finish(fig, ax, title or "Spread", xlabel="", ylabel="value", save=save, show=show)


def scatter(xs, ys, fit: str | None = "linear", title=None, xlabel="x", ylabel="y",
            save=None, show=False):
    """Scatter plot with an optional fitted model and its R² reported.

    >>> scatter([1, 2, 3, 4], [2.1, 3.9, 6.2, 7.8])  # doctest: +SKIP
    """
    from .stats import regression

    p = theme.palette()
    fig, ax = _axes()
    ax.plot(xs, ys, "o", color=p.color(0), markersize=7,
            markeredgecolor=p.surface, markeredgewidth=1.5, label="data", linestyle="none")
    if fit:
        model = regression(xs, ys, fit)
        grid = np.linspace(min(xs), max(xs), 300)
        ax.plot(grid, model["predict"](grid), color=p.color(1), linewidth=2,
                label=f"{model['equation']}   (R² = {model['r_squared']:.4f})")
    return _finish(fig, ax, title or "Scatter", xlabel=xlabel, ylabel=ylabel,
                   legend=True, save=save, show=show)


def plot_normal(mean=0.0, sd=1.0, shade=None, title=None, save=None, show=False):
    """Normal curve, optionally shading ``P(a < X < b)`` and labelling it.

    >>> plot_normal(100, 15, shade=(85, 115))  # doctest: +SKIP
    """
    from scipy import stats as st

    p = theme.palette()
    xs = np.linspace(mean - 4 * sd, mean + 4 * sd, 800)
    ys = st.norm.pdf(xs, mean, sd)
    fig, ax = _axes()
    ax.plot(xs, ys, color=p.color(0), label=f"N({mean}, {sd}²)")
    if shade:
        lo, hi = shade
        mask = (xs >= lo) & (xs <= hi)
        prob = float(st.norm.cdf(hi, mean, sd) - st.norm.cdf(lo, mean, sd))
        ax.fill_between(xs[mask], 0, ys[mask], color=p.color(0), alpha=0.25,
                        label=f"P({lo} < X < {hi}) = {prob:.4f}")
    ax.set_ylim(bottom=0)
    return _finish(fig, ax, title or "Normal distribution", ylabel="density",
                   legend=True, save=save, show=show)


# --- interactive (plotly) ----------------------------------------------------

def interactive(*exprs, domain=(-10, 10), labels=None, title="Interactive plot",
                points=2000, var=x, save=None):
    """Interactive Plotly version of :func:`plot` — hover, zoom, pan.

    Writes a standalone HTML file (opens in a browser) and returns its path.
    """
    import plotly.graph_objects as go

    p = theme.palette()
    fig = go.Figure()
    for i, e in enumerate(exprs):
        xs, ys = _sample(e, *domain, points, var)
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", name=labels[i] if labels else f"y = {sp.sstr(sym(e))}",
            line={"color": p.color(i), "width": 2},
            hovertemplate="x = %{x:.4f}<br>y = %{y:.4f}<extra></extra>",
        ))
    fig.update_layout(
        title=title, template="plotly_white", hovermode="x unified",
        paper_bgcolor=p.page, plot_bgcolor=p.surface,
        font={"color": p.ink_secondary, "family": "system-ui, sans-serif"},
        xaxis={"gridcolor": p.grid, "zerolinecolor": p.axis, "title": "x"},
        yaxis={"gridcolor": p.grid, "zerolinecolor": p.axis, "title": "y"},
        showlegend=len(exprs) > 1,
    )
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(save) if save else PLOT_DIR / f"{_slug(title)}.html"
    fig.write_html(path, include_plotlyjs="cdn")
    return path


def interactive_surface(expr, xrange=(-5, 5), yrange=(-5, 5), title="Surface",
                        points=80, save=None):
    """Interactive 3D surface you can rotate in a browser."""
    import plotly.graph_objects as go

    from .symbols import y as ysym

    p = theme.palette()
    f = sp.lambdify((x, ysym), sym(expr), "numpy")
    xs = np.linspace(*xrange, points)
    ys = np.linspace(*yrange, points)
    X, Y = np.meshgrid(xs, ys)
    with np.errstate(all="ignore"):
        Z = f(X, Y) * np.ones_like(X)
    ramp = [[0.0, "#cde2fb"], [0.25, "#86b6ef"], [0.5, "#3987e5"],
            [0.75, "#256abf"], [1.0, "#0d366b"]]
    fig = go.Figure(go.Surface(x=xs, y=ys, z=Z, colorscale=ramp))
    fig.update_layout(title=title, paper_bgcolor=p.page,
                      font={"color": p.ink_secondary, "family": "system-ui, sans-serif"})
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(save) if save else PLOT_DIR / f"{_slug(title)}.html"
    fig.write_html(path, include_plotlyjs="cdn")
    return path


__all__ = [
    "PLOT_DIR",
    "boxplot",
    "histogram",
    "interactive",
    "interactive_surface",
    "plot",
    "plot_analysis",
    "plot_contour",
    "plot_implicit",
    "plot_integral",
    "plot_normal",
    "plot_parametric",
    "plot_polar",
    "plot_slope_field",
    "plot_surface",
    "plot_tangent",
    "scatter",
]
