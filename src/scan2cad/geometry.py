from __future__ import annotations

from dataclasses import dataclass
from math import acos, degrees, hypot
from typing import Iterable

Point = tuple[float, float]


@dataclass(frozen=True)
class Path:
    points: tuple[Point, ...]

    def reversed(self) -> "Path":
        return Path(tuple(reversed(self.points)))

    @property
    def start(self) -> Point:
        return self.points[0]

    @property
    def end(self) -> Point:
        return self.points[-1]

    def tangent_at_start(self, sample: int = 4) -> Point:
        return _tangent(self.points, 0, min(sample, len(self.points) - 1))

    def tangent_at_end(self, sample: int = 4) -> Point:
        last = len(self.points) - 1
        return _tangent(self.points, max(0, last - sample), last)


def distance(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def angle_between(a: Point, b: Point) -> float:
    alen = hypot(a[0], a[1])
    blen = hypot(b[0], b[1])
    if alen == 0 or blen == 0:
        return 180.0
    dot = (a[0] * b[0] + a[1] * b[1]) / (alen * blen)
    dot = max(-1.0, min(1.0, dot))
    return degrees(acos(dot))


def simplify_rdp(points: Iterable[Point], epsilon: float) -> list[Point]:
    pts = list(points)
    if len(pts) < 3 or epsilon <= 0:
        return pts

    keep = [False] * len(pts)
    keep[0] = True
    keep[-1] = True
    stack = [(0, len(pts) - 1)]

    while stack:
        start, end = stack.pop()
        farthest = start
        max_distance = 0.0
        for idx in range(start + 1, end):
            current = _point_line_distance(pts[idx], pts[start], pts[end])
            if current > max_distance:
                max_distance = current
                farthest = idx
        if max_distance > epsilon:
            keep[farthest] = True
            stack.append((start, farthest))
            stack.append((farthest, end))

    return [point for point, use in zip(pts, keep) if use]


def _tangent(points: tuple[Point, ...], start: int, end: int) -> Point:
    return (points[end][0] - points[start][0], points[end][1] - points[start][1])


def _point_line_distance(point: Point, start: Point, end: Point) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if dx == 0 and dy == 0:
        return distance(point, start)
    numerator = abs(dy * point[0] - dx * point[1] + end[0] * start[1] - end[1] * start[0])
    return numerator / hypot(dx, dy)
