import argparse
from pathlib import Path

from reportlab.graphics import renderSVG
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing


def write_qr(url: str, output: Path, size: int = 180) -> None:
    qr = QrCodeWidget(url)
    x0, y0, x1, y1 = qr.getBounds()
    scale = min(size / (x1 - x0), size / (y1 - y0))
    drawing = Drawing(
        size,
        size,
        transform=[scale, 0, 0, scale, -x0 * scale, -y0 * scale],
    )
    drawing.add(qr)
    output.parent.mkdir(parents=True, exist_ok=True)
    renderSVG.drawToFile(drawing, str(output))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the public case-study QR code")
    parser.add_argument("--url", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("case-study/assets/qr/site-url.svg"),
    )
    args = parser.parse_args()
    write_qr(args.url, args.output)
    print(f"Wrote {args.output} for {args.url}")


if __name__ == "__main__":
    main()
