import importlib.util
import sys
import types

import numpy as np
import pytest

from plotshapes import geometry as g

HAS_PLOTLY = importlib.util.find_spec("plotly") is not None


# ------------------------------------------------------------------ circle


@pytest.mark.parametrize("radius,center", [(1.0, (0, 0)), (2.5, (3, -1)), (0.1, (-5, 5))])
def test_circle_radius_constant(radius, center):
    x, y = g.circle(radius, center, n=100)
    r = np.hypot(x - center[0], y - center[1])
    np.testing.assert_allclose(r, radius, rtol=1e-12)


def test_circle_closure_and_count():
    x, y = g.circle(n=50)
    assert len(x) == len(y) == 51
    assert g.is_closed(x, y)
    assert len({(round(a, 9), round(b, 9)) for a, b in zip(x[:-1], y[:-1], strict=True)}) == 50


def test_circle_area_and_perimeter_converge():
    x, y = g.circle(2.0, n=2000)
    assert g.polygon_area(x, y) == pytest.approx(np.pi * 4, rel=1e-5)
    assert g.path_length(x, y) == pytest.approx(2 * np.pi * 2, rel=1e-5)


@pytest.mark.parametrize("kwargs", [{"radius": 0}, {"radius": -1}, {"n": 2}])
def test_circle_rejects_bad_input(kwargs):
    with pytest.raises(ValueError):
        g.circle(**kwargs)


# ----------------------------------------------------------------- ellipse


def test_ellipse_satisfies_equation():
    x, y = g.ellipse(3.0, 1.5, n=300)
    np.testing.assert_allclose((x / 3.0) ** 2 + (y / 1.5) ** 2, 1.0, rtol=1e-12)
    assert g.is_closed(x, y)
    assert g.polygon_area(x, y) == pytest.approx(np.pi * 3.0 * 1.5, rel=1e-3)


def test_ellipse_rotation_preserves_shape():
    x, y = g.ellipse(2.0, 1.0, center=(1, 1), angle_deg=45, n=400)
    xr, yr = g.rotate(x - 1, y - 1, -45)
    np.testing.assert_allclose((xr / 2.0) ** 2 + yr**2, 1.0, atol=1e-12)


def test_ellipse_equal_axes_is_circle():
    x1, y1 = g.ellipse(1.0, 1.0, n=64)
    x2, y2 = g.circle(1.0, n=64)
    np.testing.assert_allclose(x1, x2, atol=1e-12)
    np.testing.assert_allclose(y1, y2, atol=1e-12)


# ----------------------------------------------------------------- polygon


@pytest.mark.parametrize("sides", [3, 4, 6, 12])
def test_polygon_vertices_and_sides(sides):
    x, y = g.regular_polygon(sides, radius=2.0)
    assert len(x) == sides + 1 and g.is_closed(x, y)
    np.testing.assert_allclose(np.hypot(x, y), 2.0)
    edges = np.hypot(np.diff(x), np.diff(y))
    np.testing.assert_allclose(edges, edges[0])
    expected = 0.5 * sides * 4.0 * np.sin(2 * np.pi / sides)
    assert g.polygon_area(x, y) == pytest.approx(expected)


def test_square_area():
    x, y = g.regular_polygon(4, radius=np.sqrt(2), rotation_deg=45)
    assert g.polygon_area(x, y) == pytest.approx(4.0)
    np.testing.assert_allclose(x[0], 1.0)


def test_polygon_rejects_two_sides():
    with pytest.raises(ValueError):
        g.regular_polygon(2)


# ------------------------------------------------------- spiral and rose


def test_spiral_radius_grows_linearly():
    x, y = g.spiral(turns=3, spacing=1.0, n=301)
    r = np.hypot(x, y)
    assert len(x) == 301
    assert r[0] == pytest.approx(0.0)
    assert r[-1] == pytest.approx(3.0)
    assert np.all(np.diff(r) > 0)
    assert not g.is_closed(x, y)


@pytest.mark.parametrize("k,petals", [(1, 1), (2, 4), (3, 3), (4, 8), (5, 5)])
def test_rose_petal_count(k, petals):
    assert g.rose_petals(k) == petals
    x, y = g.rose(k, amplitude=2.0, n=4001)
    r = np.hypot(x, y)
    assert r.max() == pytest.approx(2.0, rel=1e-4)
    assert g.is_closed(x, y, tol=1e-9)
    # Count tips: local maxima of r that reach the amplitude.
    tips = np.sum((r[1:-1] > r[:-2]) & (r[1:-1] >= r[2:]) & (r[1:-1] > 1.99))
    tips += r[0] > 1.99  # theta = 0 is always a petal tip (shared with the end)
    assert tips == petals


def test_rose_rejects_non_integer():
    with pytest.raises(ValueError):
        g.rose(2.5)


def test_shape_registry():
    assert set(g.SHAPES) == {"circle", "ellipse", "polygon", "spiral", "rose"}


# ------------------------------------------------------------ plotly layer


class _FakeFigure:
    def __init__(self, data=None):
        self.data = [data] if data is not None else []
        self.layout, self.shapes, self.xaxes, self.yaxes = {}, [], {}, {}

    def update_layout(self, **kw):
        self.layout.update(kw)

    def update_xaxes(self, **kw):
        self.xaxes.update(kw)

    def update_yaxes(self, **kw):
        self.yaxes.update(kw)

    def add_shape(self, **kw):
        self.shapes.append(kw)


@pytest.fixture
def fake_plotly(monkeypatch):
    go = types.ModuleType("plotly.graph_objects")
    go.Figure = _FakeFigure
    go.Scatter = lambda **kw: kw
    pkg = types.ModuleType("plotly")
    pkg.graph_objects = go
    monkeypatch.setitem(sys.modules, "plotly", pkg)
    monkeypatch.setitem(sys.modules, "plotly.graph_objects", go)
    return go


def test_circle_figure_with_fake_plotly(fake_plotly):
    from plotshapes import plotly_figures as pf

    fig = pf.circle_figure(radius=2.0, n=40)
    trace = fig.data[0]
    assert len(trace["x"]) == 41 and trace["fill"] == "toself"
    np.testing.assert_allclose(np.hypot(trace["x"], trace["y"]), 2.0)
    assert fig.yaxes["scaleanchor"] == "x"
    assert fig.layout["title"] == "Circle (r = 2.0)"


def test_circle_shape_figure_with_fake_plotly(fake_plotly):
    from plotshapes import plotly_figures as pf

    fig = pf.circle_shape_figure(radius=1.5, center=(1, 2))
    (shape,) = fig.shapes
    assert shape["type"] == "circle"
    assert (shape["x0"], shape["y0"], shape["x1"], shape["y1"]) == (-0.5, 0.5, 2.5, 3.5)


def test_spiral_figure_not_filled(fake_plotly):
    from plotshapes import plotly_figures as pf

    assert pf.spiral_figure(turns=2).data[0]["fill"] is None
    assert "8 petals" in pf.rose_figure(k=4).layout["title"]


@pytest.mark.skipif(not HAS_PLOTLY, reason="plotly not installed")
def test_real_plotly_figure():
    from plotshapes import plotly_figures as pf

    fig = pf.circle_figure(radius=1.0, n=10)
    assert len(fig.data[0].x) == 11
    assert pf.circle_shape_figure().layout.shapes[0].type == "circle"


def test_matplotlib_gallery(tmp_path):
    pytest.importorskip("matplotlib")
    from plotshapes.mpl_render import GALLERY, render_gallery

    paths = render_gallery(tmp_path, dpi=40)
    assert len(paths) == len(GALLERY) + 1
    for p in paths:
        assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
