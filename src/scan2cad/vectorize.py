from __future__ import annotations

from collections import defaultdict

import cv2
import numpy as np

from .geometry import Path

Pixel = tuple[int, int]


def image_to_paths(gray: np.ndarray, min_points: int = 8) -> list[Path]:
    binary = _binarize(gray)
    skeleton = _thin(binary)
    pixel_paths = _trace_skeleton(skeleton)
    paths: list[Path] = []
    for path in pixel_paths:
        if len(path) >= min_points:
            paths.append(Path(tuple((float(x), float(y)) for x, y in path)))
    return paths


def _binarize(gray: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresholded = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        35,
        9,
    )
    kernel = np.ones((2, 2), np.uint8)
    return cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)


def _thin(binary: np.ndarray) -> np.ndarray:
    image = (binary > 0).astype(np.uint8)
    previous = np.zeros_like(image)
    while not np.array_equal(image, previous):
        previous = image.copy()
        image = _zhang_suen_pass(image, 0)
        image = _zhang_suen_pass(image, 1)
    return image


def _zhang_suen_pass(image: np.ndarray, pass_index: int) -> np.ndarray:
    padded = np.pad(image, 1)
    remove: list[Pixel] = []
    height, width = image.shape

    for y in range(1, height + 1):
        for x in range(1, width + 1):
            if padded[y, x] == 0:
                continue
            neighbors = [
                padded[y - 1, x],
                padded[y - 1, x + 1],
                padded[y, x + 1],
                padded[y + 1, x + 1],
                padded[y + 1, x],
                padded[y + 1, x - 1],
                padded[y, x - 1],
                padded[y - 1, x - 1],
            ]
            count = int(sum(neighbors))
            transitions = sum(1 for idx in range(8) if neighbors[idx] == 0 and neighbors[(idx + 1) % 8] == 1)
            if not (2 <= count <= 6 and transitions == 1):
                continue
            if pass_index == 0:
                if neighbors[0] * neighbors[2] * neighbors[4] == 0 and neighbors[2] * neighbors[4] * neighbors[6] == 0:
                    remove.append((x - 1, y - 1))
            else:
                if neighbors[0] * neighbors[2] * neighbors[6] == 0 and neighbors[0] * neighbors[4] * neighbors[6] == 0:
                    remove.append((x - 1, y - 1))

    result = image.copy()
    for x, y in remove:
        result[y, x] = 0
    return result


def _trace_skeleton(skeleton: np.ndarray) -> list[list[Pixel]]:
    pixels = {(x, y) for y, x in zip(*np.nonzero(skeleton))}
    if not pixels:
        return []

    adjacency: dict[Pixel, list[Pixel]] = defaultdict(list)
    for pixel in pixels:
        for neighbor in _neighbors(pixel):
            if neighbor in pixels:
                adjacency[pixel].append(neighbor)

    visited_edges: set[frozenset[Pixel]] = set()
    paths: list[list[Pixel]] = []
    starts = [pixel for pixel in pixels if len(adjacency[pixel]) != 2]

    for start in starts:
        for neighbor in adjacency[start]:
            edge = frozenset((start, neighbor))
            if edge not in visited_edges:
                paths.append(_walk_path(start, neighbor, adjacency, visited_edges))

    for pixel in pixels:
        for neighbor in adjacency[pixel]:
            edge = frozenset((pixel, neighbor))
            if edge not in visited_edges:
                paths.append(_walk_path(pixel, neighbor, adjacency, visited_edges))

    return paths


def _walk_path(start: Pixel, next_pixel: Pixel, adjacency: dict[Pixel, list[Pixel]], visited_edges: set[frozenset[Pixel]]) -> list[Pixel]:
    path = [start, next_pixel]
    previous = start
    current = next_pixel
    visited_edges.add(frozenset((start, next_pixel)))

    while len(adjacency[current]) == 2:
        candidates = [pixel for pixel in adjacency[current] if pixel != previous]
        if not candidates:
            break
        following = candidates[0]
        edge = frozenset((current, following))
        if edge in visited_edges:
            break
        path.append(following)
        visited_edges.add(edge)
        previous, current = current, following

    return path


def _neighbors(pixel: Pixel) -> list[Pixel]:
    x, y = pixel
    return [
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
        (x - 1, y),
        (x + 1, y),
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
    ]
