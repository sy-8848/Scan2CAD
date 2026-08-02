from __future__ import annotations

from pathlib import Path

import ezdxf

from .geometry import Path as CadPath


def write_dxf(paths: list[CadPath], output_path: Path, page_height: float, as_curve: bool = False) -> None:
    document = ezdxf.new("R2010")
    modelspace = document.modelspace()

    for path in paths:
        points = [(x, page_height - y, 0.0) for x, y in path.points]
        if len(points) < 2:
            continue
        if as_curve and len(points) >= 3:
            modelspace.add_spline(fit_points=points)
        else:
            modelspace.add_lwpolyline([(x, y) for x, y, _ in points])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.saveas(output_path)
