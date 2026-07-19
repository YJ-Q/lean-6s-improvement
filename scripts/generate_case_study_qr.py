from pathlib import Path

from reportlab.graphics import renderSVG
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing


ROOT = Path(__file__).resolve().parents[1]
URL = "https://yj-q.github.io/lean-6s-improvement/"
OUTPUT = ROOT / "case-study" / "assets" / "diagrams" / "site-qr.svg"


def main() -> None:
    qr = QrCodeWidget(URL)
    x0, y0, x1, y1 = qr.getBounds()
    size = 180
    drawing = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
    drawing.add(qr)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    renderSVG.drawToFile(drawing, str(OUTPUT))
    print(OUTPUT)


if __name__ == "__main__":
    main()
