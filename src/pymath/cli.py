"""The `pymath` command — a ClassWiz you drive from the terminal.

    pymath solve "x^2 - 5x + 6 = 0"
    pymath diff "sin(x)*x^2"
    pymath integrate "x^2" --from 0 --to 3
    pymath plot "x^2" "2x+1" --domain -5:5
    pymath triangle --a 3 --b 4 --C 90
    pymath repl
"""

from __future__ import annotations

import typer

from . import algebra, calculus, numbertheory, plotting, stats, trig
from .display import console, show, table

app = typer.Typer(
    add_completion=False,
    help="A programmable graphics calculator. Run `pymath repl` for an interactive session.",
    no_args_is_help=True,
)


def _domain(text: str) -> tuple[float, float]:
    lo, hi = text.split(":")
    return float(lo), float(hi)


@app.command()
def solve(
    equation: str = typer.Argument(..., help='e.g. "x^2 - 5x + 6 = 0"'),
    var: str = typer.Option("x", help="variable to solve for"),
    real: bool = typer.Option(False, "--real", help="discard complex solutions"),
):
    """Solve an equation exactly."""
    import sympy as sp

    result = algebra.solve(equation, sp.Symbol(var, real=True),
                           domain="real" if real else "complex")
    show(result, label=f"solutions for {var}")


@app.command()
def simplify(expression: str):
    """Simplify, factorise and expand an expression, all three."""
    table({
        "input": algebra.sym(expression),
        "simplified": algebra.simplify(expression),
        "factorised": algebra.factorise(expression),
        "expanded": algebra.expand(expression),
    }, title="forms")


@app.command()
def diff(
    expression: str,
    var: str = typer.Option("x"),
    order: int = typer.Option(1, help="1 = first derivative, 2 = second, ..."),
):
    """Differentiate an expression."""
    import sympy as sp

    show(calculus.diff(expression, sp.Symbol(var, real=True), order),
         label=f"d^{order}/d{var}^{order}")


@app.command()
def integrate(
    expression: str,
    var: str = typer.Option("x"),
    lower: str = typer.Option(None, "--from", help="lower bound (omit for indefinite)"),
    upper: str = typer.Option(None, "--to", help="upper bound"),
):
    """Integrate, definitely or indefinitely."""
    import sympy as sp

    result = calculus.integrate(expression, sp.Symbol(var, real=True), lower, upper)
    show(result, label="integral" + ("" if lower is None else f" from {lower} to {upper}"))


@app.command()
def analyse(expression: str, plot_it: bool = typer.Option(True, "--plot/--no-plot")):
    """Full curve analysis: intercepts, turning points, asymptotes — and a graph."""
    info = calculus.analyse(expression)
    flat = {k: v for k, v in info.items() if k not in ("stationary_points", "inflection_points")}
    table(flat, title=f"analysis of {expression}")
    for pt in info["stationary_points"]:
        console.print(f"  stationary: ({pt['x']}, {pt['y']}) — {pt['nature']}")
    for pt in info["inflection_points"]:
        console.print(f"  inflection: ({pt['x']}, {pt['y']})")
    if plot_it:
        path = plotting.plot_analysis(expression)
        console.print(f"\n[green]graph saved:[/green] {path}")


@app.command()
def limit(expression: str, to: str = typer.Option("0"), var: str = typer.Option("x")):
    """Evaluate a limit. Use `oo` for infinity."""
    import sympy as sp

    show(calculus.limit(expression, sp.Symbol(var, real=True), to), label="limit")


@app.command()
def plot(
    expressions: list[str] = typer.Argument(..., help="one or more functions of x"),
    domain: str = typer.Option("-10:10", help="range as lo:hi"),
    title: str = typer.Option(None),
    html: bool = typer.Option(False, "--html", help="interactive Plotly output instead of PNG"),
    dark: bool = typer.Option(False, "--dark", help="dark theme"),
):
    """Graph one or more functions."""
    from . import theme

    theme.use("dark" if dark else "light")
    lo, hi = _domain(domain)
    if html:
        path = plotting.interactive(*expressions, domain=(lo, hi), title=title or "Interactive plot")
    else:
        path = plotting.plot(*expressions, domain=(lo, hi), title=title)
    console.print(f"[green]saved:[/green] {path}")


@app.command()
def trigsolve(
    equation: str = typer.Argument(..., help='e.g. "sin(x) = 1/2"'),
    lower: float = typer.Option(0, "--from"),
    upper: float = typer.Option(360, "--to"),
    radians: bool = typer.Option(False, "--radians"),
):
    """Solve a trig equation over a domain (degrees by default)."""
    result = trig.solve_trig(equation, lower=lower, upper=upper, deg=not radians)
    show(result, label="solutions")


@app.command()
def triangle(
    a: float = typer.Option(None, "--a", help="side a"),
    b: float = typer.Option(None, "--b"),
    c: float = typer.Option(None, "--c"),
    A: float = typer.Option(None, "--A", help="angle A in degrees, opposite side a"),
    B: float = typer.Option(None, "--B"),
    C: float = typer.Option(None, "--C"),
):
    """Solve a triangle from any three measurements."""
    given = {k: v for k, v in {"a": a, "b": b, "c": c, "A": A, "B": B, "C": C}.items()
             if v is not None}
    table(trig.solve_triangle(**given), title="triangle")


@app.command()
def statistics(values: list[float] = typer.Argument(..., help="the data set")):
    """Descriptive statistics for a list of numbers."""
    table(stats.describe(values), title="summary")


@app.command()
def regress(
    xs: str = typer.Option(..., help="comma-separated x values"),
    ys: str = typer.Option(..., help="comma-separated y values"),
    kind: str = typer.Option("linear", help="linear|quadratic|cubic|exponential|logarithmic|power"),
    plot_it: bool = typer.Option(True, "--plot/--no-plot"),
):
    """Fit a regression model to paired data."""
    X = [float(v) for v in xs.split(",")]
    Y = [float(v) for v in ys.split(",")]
    table(stats.regression(X, Y, kind), title=f"{kind} regression")
    if plot_it:
        console.print(f"[green]graph saved:[/green] {plotting.scatter(X, Y, fit=kind)}")


@app.command()
def factor(value: int):
    """Prime factorisation of an integer."""
    table(numbertheory.factorise_int(value), title=f"factors of {value}")


@app.command()
def base(value: str, frm: int = typer.Option(10, "--from"), to: int = typer.Option(2, "--to")):
    """Convert a number between bases (2-36)."""
    console.print(numbertheory.to_base(numbertheory.from_base(value, frm), to))


@app.command()
def repl():
    """Start an interactive session with everything already imported."""
    import code

    import pymath

    banner = (
        "pymath — everything from `from pymath import *` is loaded.\n"
        "  solve('x^2 = 9')   diff('sin(x)')   plot('x^2')   describe([1,2,3])\n"
        "  Ctrl-D to exit."
    )
    namespace = {name: getattr(pymath, name) for name in pymath.__all__}
    namespace["pymath"] = pymath
    try:  # a nicer REPL if IPython is around
        from IPython import start_ipython

        start_ipython(argv=[], user_ns=namespace, display_banner=False)
        console.print(banner)
    except ImportError:
        code.interact(banner=banner, local=namespace, exitmsg="")


if __name__ == "__main__":
    app()
