from scan2cad.geometry import Path
from scan2cad.merge import MergeSettings, merge_fragments


def test_merges_short_tangent_fragments_into_one_curve():
    paths = [
        Path(((0, 0), (10, 0), (20, 0))),
        Path(((22, 0.4), (32, 0.8), (42, 1.2))),
        Path(((44, 1.4), (55, 2.0), (65, 3.0))),
    ]

    merged = merge_fragments(paths, MergeSettings(max_gap=4, max_angle_degrees=12, simplify_epsilon=0))

    assert len(merged) == 1
    assert merged[0].points[0] == (0, 0)
    assert merged[0].points[-1] == (65, 3.0)


def test_does_not_merge_crossing_or_sharp_angle_fragments():
    paths = [
        Path(((0, 0), (10, 0))),
        Path(((11, 0), (11, 10))),
    ]

    merged = merge_fragments(paths, MergeSettings(max_gap=3, max_angle_degrees=20, simplify_epsilon=0))

    assert len(merged) == 2


def test_can_merge_reversed_fragment_orientation():
    paths = [
        Path(((0, 0), (10, 0))),
        Path(((22, 0), (12, 0))),
    ]

    merged = merge_fragments(paths, MergeSettings(max_gap=3, max_angle_degrees=5, simplify_epsilon=0))

    assert len(merged) == 1
    assert merged[0].points == ((0, 0), (10, 0), (12, 0), (22, 0))
