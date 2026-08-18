"""Chart styling: one validated palette shared by every plot in the project.

The eight series colours are a colourblind-safe set in a *fixed order* — series 1
is always blue, series 2 always orange, and so on. Never shuffle or cycle them:
the ordering is what keeps adjacent colours distinguishable under colour-vision
deficiency, and consistent order means "the blue curve" means the same thing on
every chart you make.
"""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib as mpl

# Categorical slots, in the order they must be assigned.
SERIES_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SERIES_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500",
               "#d55181", "#008300", "#9085e9", "#e66767"]


@dataclass(frozen=True)
class Palette:
    """Every colour a chart needs, for one mode."""

    mode: str
    series: list[str]
    surface: str
    page: str
    ink: str
    ink_secondary: str
    muted: str
    grid: str
    axis: str
    good: str = "#0ca30c"
    critical: str = "#d03b3b"

    def color(self, index: int) -> str:
        """Series colour for slot ``index`` (0-based), capped at 8 series."""
        if index >= len(self.series):
            raise ValueError(
                "past 8 series, colour alone can't tell curves apart — "
                "split into several charts instead"
            )
        return self.series[index]


LIGHT = Palette(
    mode="light", series=SERIES_LIGHT, surface="#fcfcfb", page="#f9f9f7",
    ink="#0b0b0b", ink_secondary="#52514e", muted="#898781",
    grid="#e1e0d9", axis="#c3c2b7",
)
DARK = Palette(
    mode="dark", series=SERIES_DARK, surface="#1a1a19", page="#0d0d0d",
    ink="#ffffff", ink_secondary="#c3c2b7", muted="#898781",
    grid="#2c2c2a", axis="#383835",
)

_ACTIVE = LIGHT


def palette() -> Palette:
    """The palette currently in force."""
    return _ACTIVE


def use(mode: str = "light") -> Palette:
    """Switch all later plots to ``"light"`` or ``"dark"`` and apply the rcParams.

    >>> use("dark").surface
    '#1a1a19'
    """
    global _ACTIVE
    _ACTIVE = DARK if mode == "dark" else LIGHT
    p = _ACTIVE
    mpl.rcParams.update({
        "figure.facecolor": p.page,
        "axes.facecolor": p.surface,
        "savefig.facecolor": p.page,
        "axes.edgecolor": p.axis,
        "axes.labelcolor": p.ink_secondary,
        "axes.titlecolor": p.ink,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 12,
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 1.0,
        "axes.prop_cycle": mpl.cycler(color=p.series),
        "axes.grid": True,
        "grid.color": p.grid,          # grid stays recessive: it is not data
        "grid.linewidth": 0.8,
        "grid.alpha": 1.0,
        "text.color": p.ink,
        "xtick.color": p.muted,
        "ytick.color": p.muted,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "lines.linewidth": 1.8,        # thin marks
        "lines.markersize": 6,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "legend.labelcolor": p.ink_secondary,
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Segoe UI", "system-ui"],
        "mathtext.fontset": "dejavusans",
    })
    return p


use("light")

__all__ = ["DARK", "LIGHT", "SERIES_DARK", "SERIES_LIGHT", "Palette", "palette", "use"]
