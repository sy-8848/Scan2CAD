# Scan2CAD

Scan2CAD converts black-and-white bitmap-scanned PDF drawings into CAD-friendly DXF files.

The pipeline is tuned for architectural or engineering scans where long curves and
walls are often broken into many tiny straight fragments by raster tracing.

## Install

```powershell
python -m pip install -e .[dev]
```

## Convert a PDF

```powershell
scan2cad input.pdf output.dxf --dpi 300 --merge-distance 8 --angle 22
```

Important options:

- `--dpi`: rasterization quality. Higher values preserve detail but increase memory use.
- `--merge-distance`: maximum endpoint gap, in pixels, for reconnecting fragments.
- `--angle`: maximum tangent-angle change, in degrees, for joining fragments into one curve.
- `--min-points`: discard traced fragments shorter than this many skeleton points.
- `--curve`: write merged paths as DXF splines instead of lightweight polylines.

## How short segments become complete curves

1. Each PDF page is rasterized at the requested DPI; embedded PDF vectors are ignored.
2. The image is binarized and thinned to a one-pixel skeleton.
3. Skeleton pixels are traced into ordered polylines.
4. Nearby open endpoints are chained when their directions are compatible.
5. The final paths are simplified and written to DXF.

The fragment merger is conservative by default: it joins only endpoints that are
close and have a smooth tangent transition. This reduces broken curve output while
avoiding accidental joins across nearby but unrelated drawing lines.
