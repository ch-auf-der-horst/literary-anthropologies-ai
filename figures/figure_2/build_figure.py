"""Publication figure, 120 mm wide. Run: python3 build_figure.py
Requires reportlab; pdftoppm on PATH for PNG. No network.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

import reportlab
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
META = json.loads((ROOT / "figure_data.json").read_text())
FONTDIR = Path(reportlab.__file__).parent / "fonts"
for name, filename in [("FigureSans", "Vera.ttf"), ("FigureBold", "VeraBd.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR / filename)))

MM = 72 / 25.4
INK = "#202b32"
MUTED = "#5c6a72"
PALE = "#eef2f4"
LINE = "#c5ced3"
PATH = "#4a5c68"
KEEP = "#3a5870"
LOSS = "#6a543f"
KEEP_PALE = "#e8eef3"
LOSS_PALE = "#f3eee8"
W, H = 120.0, 160.0


def fmt_width(s: str, size: float, bold: bool = False) -> float:
    font = "FigureBold" if bold else "FigureSans"
    return pdfmetrics.stringWidth(s, font, size) / MM


class Fig:
    def __init__(self, width_mm: float, height_mm: float):
        self.W = width_mm
        self.H = height_mm
        self.c = canvas.Canvas(
            str(ROOT / "_temp.pdf"),
            pagesize=(width_mm * MM, height_mm * MM),
            invariant=1,
        )
        normal = base64.b64encode((FONTDIR / "Vera.ttf").read_bytes()).decode()
        bold = base64.b64encode((FONTDIR / "VeraBd.ttf").read_bytes()).decode()
        self.svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm}mm" height="{height_mm}mm" viewBox="0 0 {width_mm * MM} {height_mm * MM}">',
            f'<defs><style>@font-face{{font-family:FigureSans;src:url(data:font/ttf;base64,{normal})}} @font-face{{font-family:FigureSans;font-weight:bold;src:url(data:font/ttf;base64,{bold})}}</style></defs>',
        ]

    def _y(self, y_from_top: float) -> float:
        return (self.H - y_from_top) * MM

    def rect(self, x, y_top, w, h, fill, stroke="none", lw=0.35, rx=0.5):
        yb = self.H - y_top - h
        self.c.saveState()
        self.c.setFillColor(HexColor(fill))
        if stroke == "none":
            self.c.roundRect(x * MM, yb * MM, w * MM, h * MM, rx * MM, fill=1, stroke=0)
        else:
            self.c.setStrokeColor(HexColor(stroke))
            self.c.setLineWidth(lw)
            self.c.roundRect(x * MM, yb * MM, w * MM, h * MM, rx * MM, fill=1, stroke=1)
        self.c.restoreState()
        sw = "none" if stroke == "none" else stroke
        self.svg.append(
            f'<rect x="{x * MM:.2f}" y="{y_top * MM:.2f}" width="{w * MM:.2f}" height="{h * MM:.2f}" '
            f'rx="{rx * MM:.2f}" fill="{fill}" stroke="{sw}" stroke-width="{lw}"/>'
        )

    def line(self, x0, y0, x1, y1, color, lw=0.7):
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(lw)
        self.c.setLineCap(1)
        self.c.line(x0 * MM, self._y(y0), x1 * MM, self._y(y1))
        self.svg.append(
            f'<line x1="{x0 * MM:.2f}" y1="{y0 * MM:.2f}" x2="{x1 * MM:.2f}" y2="{y1 * MM:.2f}" '
            f'stroke="{color}" stroke-width="{lw}" stroke-linecap="round"/>'
        )

    def curve(self, x0, y0, x1, y1, color, lw=1.1):
        mid = (x0 + x1) / 2
        p = self.c.beginPath()
        p.moveTo(x0 * MM, self._y(y0))
        p.curveTo(mid * MM, self._y(y0), mid * MM, self._y(y1), x1 * MM, self._y(y1))
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(lw)
        self.c.setLineCap(1)
        self.c.drawPath(p, fill=0, stroke=1)
        self.svg.append(
            f'<path d="M {x0 * MM:.2f} {y0 * MM:.2f} C {mid * MM:.2f} {y0 * MM:.2f}, '
            f'{mid * MM:.2f} {y1 * MM:.2f}, {x1 * MM:.2f} {y1 * MM:.2f}" fill="none" '
            f'stroke="{color}" stroke-width="{lw}" stroke-linecap="round"/>'
        )

    def fork_path(self, x0, y0, x_left, y_left, x_right, y_right, color, lw=1.15):
        """Y from a stem: short drop, then two curves."""
        y_split = y0 + 3.2
        p = self.c.beginPath()
        p.moveTo(x0 * MM, self._y(y0))
        p.lineTo(x0 * MM, self._y(y_split))
        p.curveTo(
            x0 * MM,
            self._y(y_split + 4.5),
            x_left * MM,
            self._y(y_left - 4.5),
            x_left * MM,
            self._y(y_left),
        )
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(lw)
        self.c.setLineCap(1)
        self.c.setLineJoin(1)
        self.c.drawPath(p, fill=0, stroke=1)
        p2 = self.c.beginPath()
        p2.moveTo(x0 * MM, self._y(y_split))
        p2.curveTo(
            x0 * MM,
            self._y(y_split + 4.5),
            x_right * MM,
            self._y(y_right - 4.5),
            x_right * MM,
            self._y(y_right),
        )
        self.c.drawPath(p2, fill=0, stroke=1)
        self.svg.append(
            f'<path d="M {x0 * MM:.2f} {y0 * MM:.2f} L {x0 * MM:.2f} {y_split * MM:.2f} '
            f'C {x0 * MM:.2f} {(y_split + 4.5) * MM:.2f}, {x_left * MM:.2f} {(y_left - 4.5) * MM:.2f}, '
            f'{x_left * MM:.2f} {y_left * MM:.2f}" fill="none" stroke="{color}" '
            f'stroke-width="{lw}" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        self.svg.append(
            f'<path d="M {x0 * MM:.2f} {y_split * MM:.2f} C {x0 * MM:.2f} {(y_split + 4.5) * MM:.2f}, '
            f'{x_right * MM:.2f} {(y_right - 4.5) * MM:.2f}, {x_right * MM:.2f} {y_right * MM:.2f}" '
            f'fill="none" stroke="{color}" stroke-width="{lw}" stroke-linecap="round"/>'
        )

    def text(self, x, y_top, s, size=8, weight="normal", color=INK, ha="left"):
        font = "FigureBold" if weight == "bold" else "FigureSans"
        width = pdfmetrics.stringWidth(s, font, size)
        xx = x * MM - (width if ha == "right" else width / 2 if ha == "center" else 0)
        yy = self._y(y_top) - size * 0.32
        self.c.setFont(font, size)
        self.c.setFillColor(HexColor(color))
        self.c.drawString(xx, yy, s)
        anchor = {"left": "start", "center": "middle", "right": "end"}[ha]
        self.svg.append(
            f'<text x="{x * MM:.2f}" y="{y_top * MM:.2f}" font-family="FigureSans" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>'
        )

    def save(self, stem: str, title: str, reading: str):
        self.c.setTitle(title)
        self.c.setAuthor("Christoph auf der Horst")
        self.c.save()
        out = ROOT / stem
        (ROOT / "_temp.pdf").replace(out.with_suffix(".pdf"))
        self.svg.insert(1, "<title>" + html.escape(title) + "</title><desc>" + html.escape(reading) + "</desc>")
        out.with_suffix(".svg").write_text("\n".join(self.svg + ["</svg>"]))
        subprocess.run(
            ["pdftoppm", "-r", "400", "-png", "-singlefile", str(out.with_suffix(".pdf")), str(out)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )


def case_block(fig: Fig, x, y, w, name, note, pad=1.6):
    fig.text(x + pad, y, name, 6.5, "bold")
    fig.text(x + pad, y + 3.6, note, 6, color=MUTED)
    return 8.0


def draw():
    d = META
    fig = Fig(W, H)

    fig.text(3.5, 7.0, d["title"], 10, "bold")
    fig.text(3.5, 12.2, d["subtitle"], 6.5, color=MUTED)

    start_w, start_h = 88.0, 12.2
    start_x = (W - start_w) / 2
    start_y = 16.0
    fig.rect(start_x, start_y, start_w, start_h, PALE, LINE, 0.35, rx=0.8)
    fig.text(W / 2, start_y + 4.4, d["start"][0], 7.5, "bold", ha="center")
    fig.text(W / 2, start_y + 8.8, d["start"][1], 7.5, "bold", ha="center")
    start_cx = W / 2
    start_bottom = start_y + start_h

    gap = 1.6
    col_w = (W - 7.0 - 2 * gap) / 3
    left_x = 3.5
    mid_x = left_x + col_w + gap
    right_x = mid_x + col_w + gap
    col_y = 37.4
    col_h = 40.5

    fig.curve(start_cx - 6, start_bottom, left_x + col_w / 2, col_y, PATH, 1.1)
    fig.curve(start_cx, start_bottom, mid_x + col_w / 2, col_y, PATH, 1.3)
    fig.curve(start_cx + 6, start_bottom, right_x + col_w / 2, col_y, PATH, 1.1)

    def path_card(x, titles, claim_lines, cases, extra_lines=None):
        fig.rect(x, col_y, col_w, col_h, "#ffffff", LINE, 0.35, rx=0.7)
        fig.rect(x, col_y, 1.15, col_h, PATH, "none", 0, rx=0.2)
        cy = col_y + 4.2
        for i, line in enumerate(titles):
            fig.text(x + 2.3, cy, line, 6.5, "bold")
            cy += 3.6 if i == 0 and len(titles) > 1 else 4.0
        for line in claim_lines:
            fig.text(x + 2.3, cy, line, 6, color=MUTED)
            cy += 3.4
        cy += 1.4
        for name, note in cases:
            fig.text(x + 2.3, cy, name, 6.5, "bold")
            fig.text(x + 2.3, cy + 3.4, note, 6, color=MUTED)
            cy += 8.2
        if extra_lines:
            for line in extra_lines:
                fig.text(x + 2.3, cy, line, 6, color=MUTED)
                cy += 3.3

    her = d["paths"]["herkunft"]
    path_card(left_x, [her["title"]], [her["claim"]], her["cases"])

    arb = d["paths"]["arbeit"]
    path_card(
        mid_x,
        [arb["title"]],
        [arb["claim"]],
        [tuple(arb["before"])],
    )

    ver = d["paths"]["verantwortung"]
    path_card(
        right_x,
        ["Öffentliche", "Verantwortung"],
        [ver["claim"]],
        ver["cases"],
    )

    # Fork occupies the visual centre beneath the middle path.
    fork_gap = 3.0
    fork_w = 36.5
    pair_w = 2 * fork_w + fork_gap
    keep_x = (W - pair_w) / 2
    loss_x = keep_x + fork_w + fork_gap
    fork_y = col_y + col_h + 11.0
    fork_h = 30.0
    stem_cx = mid_x + col_w / 2
    stem_bottom = col_y + col_h

    fig.line(mid_x + 2.3, col_y + col_h - 10.4, mid_x + col_w - 2.2, col_y + col_h - 10.4, LINE, 0.35)
    fig.text(mid_x + 2.3, col_y + col_h - 8.2, d["fork"]["hinge"][0], 6, color=MUTED)
    fig.text(mid_x + 2.3, col_y + col_h - 4.6, d["fork"]["hinge"][1], 6, color=MUTED)
    fig.fork_path(
        stem_cx,
        stem_bottom,
        keep_x + fork_w / 2,
        fork_y,
        loss_x + fork_w / 2,
        fork_y,
        PATH,
        1.3,
    )

    keep = d["fork"]["keep"]
    fig.rect(keep_x, fork_y, fork_w, fork_h, KEEP_PALE, KEEP, 0.6, rx=0.7)
    fig.text(keep_x + 2.0, fork_y + 4.2, keep["title"][0], 7, "bold", KEEP)
    fig.text(keep_x + 2.0, fork_y + 8.0, keep["title"][1], 7, "bold", KEEP)
    ky = fork_y + 13.0
    for name, note in keep["cases"]:
        fig.text(keep_x + 2.0, ky, name, 6.5, "bold")
        fig.text(keep_x + 2.0, ky + 3.4, note, 6, color=MUTED)
        ky += 7.8

    loss = d["fork"]["loss"]
    fig.rect(loss_x, fork_y, fork_w, fork_h, LOSS_PALE, LOSS, 0.6, rx=0.7)
    fig.text(loss_x + 2.0, fork_y + 4.2, loss["title"][0], 7, "bold", LOSS)
    fig.text(loss_x + 2.0, fork_y + 8.0, loss["title"][1], 7, "bold", LOSS)
    ly = fork_y + 13.0
    for name, note in loss["cases"]:
        fig.text(loss_x + 2.0, ly, name, 6.5, "bold")
        fig.text(loss_x + 2.0, ly + 3.4, note, 6, color=MUTED)
        ly += 7.8

    find_y = 127.0
    find_h = 26.5
    fig.rect(3.5, find_y, 113.0, find_h, PALE, LINE, 0.35, rx=0.8)
    fig.curve(left_x + col_w / 2, col_y + col_h, 12.0, find_y, PATH, 0.9)
    fig.curve(keep_x + fork_w / 2, fork_y + fork_h, 46.0, find_y, KEEP, 1.0)
    fig.curve(loss_x + fork_w / 2, fork_y + fork_h, 74.0, find_y, LOSS, 1.0)
    fig.curve(right_x + col_w / 2, col_y + col_h, 108.0, find_y, PATH, 0.9)

    fig.text(W / 2, find_y + 5.4, d["finding"][0], 6.5, "bold", ha="center")
    fig.text(W / 2, find_y + 10.4, d["finding"][1], 6.5, "bold", ha="center")
    fig.text(W / 2, find_y + 16.6, d["finding"][2], 6.5, ha="center")
    fig.text(W / 2, find_y + 21.6, d["finding"][3], 6.5, ha="center")

    reading = (
        "Drei Begründungen menschlicher Autorschaft. Die Gabelung fragt, "
        "ob Steuerung als schöpferische Beteiligung genügt."
    )
    fig.save(d["stem"], d["title"], reading)


def booklet(stem: str):
    c = canvas.Canvas(str(ROOT / f"{stem}_mit_Lesetext.pdf"), pagesize=(595.276, 841.89))
    c.setTitle("Worin besteht menschliche Autorschaft?")
    c.setAuthor("Christoph auf der Horst")
    c.setFont("FigureSans", 12)
    c.drawString(48, 800, "Abbildung · Worin besteht menschliche Autorschaft?")
    img = ROOT / f"{stem}.png"
    w = W / 25.4 * 72
    h = H / 25.4 * 72
    c.drawImage(ImageReader(str(img)), (595.276 - w) / 2, 780 - h, width=w, height=h)
    y = 780 - h - 18
    c.setFont("FigureSans", 9)
    for line in textwrap.wrap("Bildunterschrift: " + META["caption"], 92, break_long_words=False):
        c.drawString(48, y, line)
        y -= 12
    c.showPage()
    reading = (ROOT / "Lesetext.md").read_text()
    body = "\n".join(reading.split("\n")[2:])
    y = 800
    c.setFont("FigureBold", 12)
    c.drawString(48, y, "Lesetext")
    y = 776
    c.setFont("FigureSans", 10)
    for para in body.split("\n\n"):
        para = para.replace("**Bildunterschrift:** ", "Bildunterschrift: ")
        for line in textwrap.wrap(para, 92, break_long_words=False):
            if y < 50:
                c.showPage()
                y = 800
                c.setFont("FigureSans", 10)
            c.drawString(48, y, line)
            y -= 13
        y -= 8
    c.save()


def main():
    draw()
    stem = META["stem"]
    booklet(stem)
    shutil.copyfile(FONTDIR / "bitstream-vera-license.txt", ROOT / "FONT_LICENSE.txt")
    (ROOT / "README.md").write_text(
        "# Worin besteht menschliche Autorschaft?\n\n"
        "Publikationsfassung 120 × 160 mm zu `Aufsatz_v7_gekuerzt`, Kapitel 8. "
        "Drei Begründungswege; Gabelung als Bewertungsfrage. "
        "Fallkennungen, keine Arenenspalten. Rezeption ausgeklammert.\n\n"
        f"- `{stem}.pdf` — Druckdatei, 120 mm breit\n"
        f"- `{stem}.svg` — Vektorgrafik\n"
        f"- `{stem}.png` — 400 dpi\n"
        f"- `{stem}_mit_Lesetext.pdf` — Abbildung plus Lesetext\n"
        "- `Lesetext.md` — editierbare Begleitfassung\n\n"
        "Reproduktion: `python3 build_figure.py` (reportlab, pdftoppm). "
        "Schrift: Bitstream Vera, FONT_LICENSE.txt.\n"
    )
    files = [p for p in ROOT.iterdir() if p.name != "manifest.json" and p.suffix in {".pdf", ".svg", ".png", ".md", ".json", ".py", ".txt"}]
    (ROOT / "manifest.json").write_text(
        json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}, indent=2) + "\n"
    )
    print(f"Created {stem}.pdf/.svg/.png")


if __name__ == "__main__":
    main()
