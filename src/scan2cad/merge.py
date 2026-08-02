from __future__ import annotations

from dataclasses import dataclass

from .geometry import Path, angle_between, distance, simplify_rdp


@dataclass(frozen=True)
class MergeSettings:
    max_gap: float = 8.0
    max_angle_degrees: float = 22.0
    simplify_epsilon: float = 1.2
    tangent_sample: int = 4


def merge_fragments(paths: list[Path], settings: MergeSettings) -> list[Path]:
    """Join short traced fragments into longer smooth paths.

    The algorithm repeatedly connects the best compatible pair of open endpoints.
    A candidate is accepted only when the endpoint gap is small and both outgoing
    tangents continue in nearly the same direction after orienting the paths.
    """
    active = [path for path in paths if len(path.points) >= 2]
    changed = True

    while changed:
        changed = False
        best: tuple[float, int, int, Path] | None = None

        for left_idx in range(len(active)):
            for right_idx in range(left_idx + 1, len(active)):
                candidate = _best_join(active[left_idx], active[right_idx], settings)
                if candidate is None:
                    continue
                score, joined = candidate
                if best is None or score < best[0]:
                    best = (score, left_idx, right_idx, joined)

        if best is not None:
            _, left_idx, right_idx, joined = best
            next_active = []
            for idx, path in enumerate(active):
                if idx not in (left_idx, right_idx):
                    next_active.append(path)
            next_active.append(joined)
            active = next_active
            changed = True

    return [_simplified(path, settings.simplify_epsilon) for path in active]


def _best_join(left: Path, right: Path, settings: MergeSettings) -> tuple[float, Path] | None:
    orientations = (
        (left, right),
        (left.reversed(), right),
        (left, right.reversed()),
        (left.reversed(), right.reversed()),
    )

    best: tuple[float, Path] | None = None
    for first, second in orientations:
        gap = distance(first.end, second.start)
        if gap > settings.max_gap:
            continue

        first_tangent = first.tangent_at_end(settings.tangent_sample)
        second_tangent = second.tangent_at_start(settings.tangent_sample)
        angle = angle_between(first_tangent, second_tangent)
        if angle > settings.max_angle_degrees:
            continue

        bridge_penalty = gap / max(settings.max_gap, 1.0)
        angle_penalty = angle / max(settings.max_angle_degrees, 1.0)
        score = bridge_penalty + angle_penalty
        joined = Path(_join_points(first.points, second.points, gap))
        if best is None or score < best[0]:
            best = (score, joined)

    return best


def _join_points(left: tuple[tuple[float, float], ...], right: tuple[tuple[float, float], ...], gap: float):
    if gap <= 1e-6:
        return left + right[1:]
    return left + right


def _simplified(path: Path, epsilon: float) -> Path:
    simplified = simplify_rdp(path.points, epsilon)
    if len(simplified) < 2:
        return path
    return Path(tuple(simplified))
