"""Render the PNG gallery in docs/ with Matplotlib (no plotly needed).

Run from the repository root:  python3 examples/gallery.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from plotshapes.mpl_render import render_gallery  # noqa: E402

if __name__ == "__main__":
    for path in render_gallery("docs"):
        print("wrote", path)
