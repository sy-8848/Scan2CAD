from __future__ import annotations

from pathlib import Path

import fitz
import numpy as np


def pdf_pages_to_gray(pdf_path: Path, dpi: int = 300) -> list[np.ndarray]:
    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    pages: list[np.ndarray] = []

    with fitz.open(pdf_path) as document:
        for page in document:
            pixmap = page.get_pixmap(matrix=matrix, colorspace=fitz.csGRAY, alpha=False)
            image = np.frombuffer(pixmap.samples, dtype=np.uint8)
            pages.append(image.reshape(pixmap.height, pixmap.width).copy())

    return pages
