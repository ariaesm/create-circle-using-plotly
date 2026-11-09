"""Plotly figures for the shapes. Plotly is imported lazily inside each function,
so the geometry module works (and is testable) without plotly installed."""

from __future__ import annotations

from . import geometry as g


def _go():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ImportError("plotly is required: pip install plotly") from exc
    return go


def _square_layout(fig, title: str | None):
    fig.update_layout(
        title=title,
        template="plotly_white",
        width=600,
        height=600,
        showlegend=False,
        margin=dict(l=40, r=40, t=60 if title else 30, b=40),
    )
    # Equal scaling on both axes so circles look like circles.
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


def shape_figure(x, y, title: str | None = None, fill: bool = True, color: str = "#2f6f9f"):
    """Line (optionally filled) trace for any coordinate arrays."""
    go = _go()
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=color, width=2),
            fill="toself" if fill else None,
            fillcolor="rgba(47,111,159,0.15)" if fill else None,
            hoverinfo="x+y",
        )
    )
    return _square_layout(fig, title)


def circle_figure(radius: float = 1.0, center=(0.0, 0.0), n: int = 200, **kwargs):
    """Circle drawn from sampled points as a Scatter trace."""
    x, y = g.circle(radius, center, n)
    return shape_figure(x, y, title=kwargs.pop("title", f"Circle (r = {radius})"), **kwargs)


def circle_shape_figure(radius: float = 1.0, center=(0.0, 0.0), color: str = "#2f6f9f"):
    """Circle drawn with Plotly's built-in layout shape (``type="circle"``)."""
    go = _go()
    cx, cy = center
    fig = go.Figure()
    fig.add_shape(
        type="circle",
        xref="x",
        yref="y",
        x0=cx - radius,
        y0=cy - radius,
        x1=cx + radius,
        y1=cy + radius,
        line=dict(color=color, width=2),
        fillcolor="rgba(47,111,159,0.15)",
    )
    pad = radius * 0.2
    fig.update_xaxes(range=[cx - radius - pad, cx + radius + pad])
    fig.update_yaxes(range=[cy - radius - pad, cy + radius + pad])
    return _square_layout(fig, f"Circle shape (r = {radius})")


def ellipse_figure(a: float = 2.0, b: float = 1.0, angle_deg: float = 0.0, **kwargs):
    x, y = g.ellipse(a, b, angle_deg=angle_deg)
    return shape_figure(x, y, title=kwargs.pop("title", f"Ellipse (a={a}, b={b})"), **kwargs)


def polygon_figure(sides: int = 6, radius: float = 1.0, **kwargs):
    x, y = g.regular_polygon(sides, radius)
    return shape_figure(x, y, title=kwargs.pop("title", f"Regular {sides}-gon"), **kwargs)


def spiral_figure(turns: float = 3.0, spacing: float = 1.0, **kwargs):
    x, y = g.spiral(turns, spacing)
    kwargs.setdefault("fill", False)
    return shape_figure(x, y, title=kwargs.pop("title", f"Spiral ({turns} turns)"), **kwargs)


def rose_figure(k: int = 4, amplitude: float = 1.0, **kwargs):
    x, y = g.rose(k, amplitude)
    title = kwargs.pop("title", f"Rose curve (k={k}, {g.rose_petals(k)} petals)")
    return shape_figure(x, y, title=title, **kwargs)
