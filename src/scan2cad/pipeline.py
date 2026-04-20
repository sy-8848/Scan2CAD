from __future__ import annotations

from pathlib import Path

from .dxf import write_dxf
from .geometry import Path as CadPath
from .merge import MergeSettings, merge_fragments
from .rasterize import pdf_pages_to_gray
from .vectorize import image_to_paths


def convert_pdf_to_dxf(
    pdf_path: Path,
    output_path: Path,
    dpi: int = 300,
    merge_settings: MergeSettings | None = None,
    min_points: int = 8,
    as_curve: bool = False,
) -> list[CadPath]:
    settings = merge_settings or MergeSettings()
    all_paths: list[CadPath] = []
    page_offset = 0.0
    page_height = 0.0

    for page in pdf_pages_to_gray(pdf_path, dpi=dpi):
        page_height, page_width = page.shape
        paths = image_to_paths(page, min_points=min_points)
        merged = merge_fragments(paths, settings)
        shifted = [
            CadPath(tuple((x, y + page_offset) for x, y in path.points))
            for path in merged
            if len(path.points) >= 2
        ]
        all_paths.extend(shifted)
        page_offset += float(page_height) + dpi * 0.25

    write_dxf(all_paths, output_path, page_height=max(page_offset, page_height), as_curve=as_curve)
    return all_paths
