"""Pure-NumPy generators for 2-D shapes as coordinate arrays.

Every function returns ``(x, y)`` as two 1-D float arrays. Closed shapes repeat
the first point at the end so a line plot draws a closed outline.
"""

from __future__ import annotations

import numpy as np

Point = tuple[float, float]


def _check_positive(**values: float) -> None:
    for name, value in values.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")


def circle(radius: float = 1.0, center: Point = (0.0, 0.0), n: int = 200):
    """Circle outline with ``n`` distinct points (``n + 1`` including closure)."""
    _check_positive(radius=radius)
    if n < 3:
        raise ValueError("n must be >= 3")
    t = np.linspace(0.0, 2 * np.pi, n + 1)
    x = center[0] + radius * np.cos(t)
    y = center[1] + radius * np.sin(t)
    x[-1], y[-1] = x[0], y[0]  # exact closure
    return x, y


def ellipse(
    a: float = 2.0,
    b: float = 1.0,
    center: Point = (0.0, 0.0),
    angle_deg: float = 0.0,
    n: int = 200,
):
    """Ellipse with semi-axes ``a`` (x) and ``b`` (y), rotated by ``angle_deg``."""
    _check_positive(a=a, b=b)
    if n < 3:
        raise ValueError("n must be >= 3")
    t = np.linspace(0.0, 2 * np.pi, n + 1)
    ex, ey = a * np.cos(t), b * np.sin(t)
    x, y = rotate(ex, ey, angle_deg)
    x, y = x + center[0], y + center[1]
    x[-1], y[-1] = x[0], y[0]
    return x, y


def regular_polygon(
    sides: int, radius: float = 1.0, center: Point = (0.0, 0.0), rotation_deg: float = 90.0
):
    """Regular polygon inscribed in a circle; first vertex at ``rotation_deg``."""
    if sides < 3:
        raise ValueError("a polygon needs at least 3 sides")
    _check_positive(radius=radius)
    t = np.deg2rad(rotation_deg) + 2 * np.pi * np.arange(sides + 1) / sides
    x = center[0] + radius * np.cos(t)
    y = center[1] + radius * np.sin(t)
    x[-1], y[-1] = x[0], y[0]
    return x, y


def spiral(turns: float = 3.0, spacing: float = 1.0, n: int = 600, center: Point = (0.0, 0.0)):
    """Archimedean spiral r = spacing * theta / (2 pi); radius grows by ``spacing`` per turn."""
    _check_positive(turns=turns, spacing=spacing)
    if n < 2:
        raise ValueError("n must be >= 2")
    theta = np.linspace(0.0, 2 * np.pi * turns, n)
    r = spacing * theta / (2 * np.pi)
    return center[0] + r * np.cos(theta), center[1] + r * np.sin(theta)


def rose(k: int = 4, amplitude: float = 1.0, n: int = 1000, center: Point = (0.0, 0.0)):
    """Rose curve r = amplitude * cos(k * theta) for integer ``k``.

    The curve has ``k`` petals for odd ``k`` and ``2k`` petals for even ``k``.
    """
    if not isinstance(k, (int, np.integer)) or k < 1:
        raise ValueError("k must be a positive integer")
    _check_positive(amplitude=amplitude)
    period = np.pi if k % 2 else 2 * np.pi
    theta = np.linspace(0.0, period, n)
    r = amplitude * np.cos(k * theta)
    return center[0] + r * np.cos(theta), center[1] + r * np.sin(theta)


def rose_petals(k: int) -> int:
    return k if k % 2 else 2 * k


# ------------------------------------------------------------ helpers


def rotate(x, y, angle_deg: float, origin: Point = (0.0, 0.0)):
    """Rotate points counter-clockwise around ``origin``."""
    a = np.deg2rad(angle_deg)
    x0, y0 = np.asarray(x) - origin[0], np.asarray(y) - origin[1]
    xr = origin[0] + x0 * np.cos(a) - y0 * np.sin(a)
    yr = origin[1] + x0 * np.sin(a) + y0 * np.cos(a)
    return xr, yr


def is_closed(x, y, tol: float = 1e-9) -> bool:
    return bool(abs(x[0] - x[-1]) <= tol and abs(y[0] - y[-1]) <= tol)


def polygon_area(x, y) -> float:
    """Signed shoelace area (positive for counter-clockwise outlines)."""
    x, y = np.asarray(x), np.asarray(y)
    return float(0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1]))


def path_length(x, y) -> float:
    return float(np.sum(np.hypot(np.diff(x), np.diff(y))))


SHAPES = {
    "circle": circle,
    "ellipse": ellipse,
    "polygon": regular_polygon,
    "spiral": spiral,
    "rose": rose,
}
