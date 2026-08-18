"""Pretty output for the terminal and for notebooks."""

from __future__ import annotations

import sympy as sp
from rich.console import Console
from rich.table import Table

console = Console()


def show(value, label: str | None = None, decimals: int = 6) -> None:
    """Print a result the way a calculator would: exact form, then decimal.

    Dicts (the analysis helpers return them) print as a two-column table.
    """
    if isinstance(value, dict):
        table(value, title=label)
        return
    if label:
        console.print(f"[bold]{label}[/bold]")
    if isinstance(value, (list, tuple)):
        for item in value:
            show(item, decimals=decimals)
        return
    console.print(f"  {sp.pretty(value, use_unicode=True)}")
    approx = _approx(value, decimals)
    if approx is not None:
        console.print(f"  [dim]≈ {approx}[/dim]")


def table(mapping: dict, title: str | None = None) -> None:
    """Render a dict of results as a table."""
    t = Table(title=title, show_header=True, header_style="bold", box=None, pad_edge=False)
    t.add_column("quantity", style="cyan")
    t.add_column("exact")
    t.add_column("approx", style="dim")
    for key, value in mapping.items():
        if callable(value):
            continue
        approx = _approx(value, 6)
        t.add_row(str(key), _short(value), "" if approx is None else str(approx))
    console.print(t)


def _short(value, limit: int = 88) -> str:
    text = sp.sstr(value) if isinstance(value, sp.Basic) else str(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _approx(value, decimals: int):
    """Decimal form, or None when there isn't a sensible one."""
    try:
        if isinstance(value, sp.Basic):
            if not value.free_symbols and value.is_number:
                num = complex(value)
                if abs(num.imag) < 1e-12:
                    return round(num.real, decimals)
                return complex(round(num.real, decimals), round(num.imag, decimals))
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return None


__all__ = ["console", "show", "table"]
