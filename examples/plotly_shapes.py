"""Build the Plotly figures and save them as standalone HTML files (needs plotly).

Run from the repository root:  python3 examples/plotly_shapes.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from plotshapes import plotly_figures as pf  # noqa: E402

FIGURES = {
    "circle": pf.circle_figure(radius=2.0),
    "circle_shape": pf.circle_shape_figure(radius=2.0),
    "ellipse": pf.ellipse_figure(a=3, b=1.5, angle_deg=30),
    "hexagon": pf.polygon_figure(sides=6),
    "spiral": pf.spiral_figure(turns=4),
    "rose": pf.rose_figure(k=5),
}

if __name__ == "__main__":
    out = Path("out")
    out.mkdir(exist_ok=True)
    for name, fig in FIGURES.items():
        path = out / f"{name}.html"
        fig.write_html(path, include_plotlyjs="cdn")
        print("wrote", path)
    if "--show" in sys.argv:
        FIGURES["circle"].show()
