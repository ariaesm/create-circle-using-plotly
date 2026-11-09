"""Matplotlib fallback renderer (used to build the PNG gallery in docs/)."""

from __future__ import annotations

from pathlib import Path

from . import geometry as g

COLOR = "#2f6f9f"

GALLERY = [
    ("circle", "Circle  r = 1", lambda: g.circle(1.0), True),
    ("ellipse", "Ellipse  a=2, b=1, 30°", lambda: g.ellipse(2.0, 1.0, angle_deg=30), True),
    ("hexagon", "Regular hexagon", lambda: g.regular_polygon(6), True),
    ("spiral", "Archimedean spiral, 3 turns", lambda: g.spiral(3), False),
    ("rose", "Rose curve k = 4 (8 petals)", lambda: g.rose(4), True),
    ("rose5", "Rose curve k = 5 (5 petals)", lambda: g.rose(5), True),
]


def draw(ax, x, y, title: str, fill: bool = True) -> None:
    ax.plot(x, y, color=COLOR, linewidth=2)
    if fill:
        ax.fill(x, y, color=COLOR, alpha=0.15, linewidth=0)
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def render_gallery(out_dir: str | Path = "docs", dpi: int = 100) -> list[Path]:
    """Write one PNG per shape plus ``gallery.png``; return the written paths."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, title, make, fill in GALLERY:
        fig, ax = plt.subplots(figsize=(4, 4))
        draw(ax, *make(), title, fill)
        fig.tight_layout()
        path = out / f"{name}.png"
        fig.savefig(path, dpi=dpi)
        plt.close(fig)
        written.append(path)

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    for ax, (_, title, make, fill) in zip(axes.flat, GALLERY, strict=True):
        draw(ax, *make(), title, fill)
    fig.tight_layout()
    path = out / "gallery.png"
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    written.append(path)
    return written


if __name__ == "__main__":
    for p in render_gallery():
        print("wrote", p)
