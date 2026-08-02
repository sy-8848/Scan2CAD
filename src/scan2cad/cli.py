from __future__ import annotations

import argparse
from pathlib import Path

from .merge import MergeSettings
from .pipeline import convert_pdf_to_dxf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert black-and-white scanned PDFs to DXF.")
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_dxf", type=Path)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--merge-distance", type=float, default=8.0)
    parser.add_argument("--angle", type=float, default=22.0, help="maximum endpoint tangent angle in degrees")
    parser.add_argument("--simplify", type=float, default=1.2, help="Ramer-Douglas-Peucker simplification epsilon")
    parser.add_argument("--min-points", type=int, default=8)
    parser.add_argument("--curve", action="store_true", help="write merged paths as DXF splines")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = MergeSettings(
        max_gap=args.merge_distance,
        max_angle_degrees=args.angle,
        simplify_epsilon=args.simplify,
    )
    paths = convert_pdf_to_dxf(
        args.input_pdf,
        args.output_dxf,
        dpi=args.dpi,
        merge_settings=settings,
        min_points=args.min_points,
        as_curve=args.curve,
    )
    print(f"Wrote {len(paths)} paths to {args.output_dxf}")


if __name__ == "__main__":
    main()
