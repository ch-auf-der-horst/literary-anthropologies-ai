"""Publication Sankey, 120 mm wide. Run: python3 build_sankey.py
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
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
META = json.loads((ROOT / "sankey_data.json").read_text())
FONTDIR = Path(reportlab.__file__).parent / "fonts"
for name, filename in [("FigureSans", "Vera.ttf"), ("FigureBold", "VeraBd.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR / filename)))

MM = 72 / 25.4
INK = "#202b32"
MUTED = "#5c6a72"
OUT = "#9aa7ae"
PALE = "#eef2f4"
LINE = "#c5ced3"
W, H = 120.0, 178.0

# Selection Sankey only. Bundling is a separate, non-proportional column.
NODES = [
    ("de_inv", "de", "Inventar", 0, 232, "keep"),
    ("de_erg", "de", "Ergänzung", 0, 13, "keep"),
    ("de_kod", "de", "Kodiertabelle", 1, 203, "keep"),
    ("de_nur", "de", "nur Inventar", 1, 42, "out"),
    ("de_ki", "de", "stark/mittel", 2, 55, "keep"),
    ("de_restk", "de", "übrige", 2, 148, "out"),
    ("de_wort", "de", "Wortzählung", 3, 49, "result"),
    ("de_aus", "de", "Ausschluss", 3, 2, "out"),
    ("de_ext", "de", "extern", 3, 4, "out"),
    ("cn_inv", "cn", "Inventar", 0, 962, "keep"),
    ("cn_120", "cn", "Stichprobe", 1, 120, "keep"),
    ("cn_out", "cn", "nicht gezogen", 1, 842, "out"),
    ("cn_kern", "cn", "KI-Kern", 2, 32, "keep"),
    ("cn_nokern", "cn", "nicht im Kern", 2, 88, "out"),
    ("bt_de", "bt", "Screening DE", 0, 140, "keep"),
    ("bt_en", "bt", "Screening EN", 0, 80, "keep"),
    ("bt_ade", "bt", "A-Fälle DE", 1, 23, "keep"),
    ("bt_aen", "bt", "A-Fälle EN", 1, 11, "keep"),
    ("bt_b", "bt", "B ausgewählt", 1, 6, "keep"),
    ("bt_rest", "bt", "übriges Screening", 1, 180, "out"),
    ("bt_kde", "bt", "A DE", 2, 23, "keep"),
    ("bt_ken", "bt", "A EN", 2, 11, "keep"),
    ("bt_kb", "bt", "B-Kontrast", 2, 6, "out"),
]

LINKS = [
    ("de_inv", "de_kod", 190),
    ("de_inv", "de_nur", 42),
    ("de_erg", "de_kod", 13),
    ("de_kod", "de_ki", 55),
    ("de_kod", "de_restk", 148),
    ("de_ki", "de_wort", 49),
    ("de_ki", "de_aus", 2),
    ("de_ki", "de_ext", 4),
    ("cn_inv", "cn_120", 120),
    ("cn_inv", "cn_out", 842),
    ("cn_120", "cn_kern", 32),
    ("cn_120", "cn_nokern", 88),
    ("bt_de", "bt_ade", 23),
    ("bt_de", "bt_b", 6),
    ("bt_de", "bt_rest", 111),
    ("bt_en", "bt_aen", 11),
    ("bt_en", "bt_rest", 69),
    ("bt_ade", "bt_kde", 23),
    ("bt_aen", "bt_ken", 11),
    ("bt_b", "bt_kb", 6),
]

# Fixed plaques: not scaled to family or qualitative counts.
BOXES = [
    ("de", "de_kod", ["30 + 29 Einträge", "10 Kat. / 5 Felder", "überlappender", "Analysebestand"]),
    ("cn", "cn_kern", ["32 Texte", "12 Familien"]),
    ("bt", "bt_kde", ["DE · 23 A-Fälle", "22 zugeordnet", "6 Familien"]),
    ("bt", "bt_ken", ["EN · 11 A-Fälle", "6 Familien"]),
]
SKIP_LABEL = {"bt_kde", "bt_ken", "bt_kb"}


def hex_alpha(hex_color: str, alpha: float) -> Color:
    c = HexColor(hex_color)
    return Color(c.red, c.green, c.blue, alpha=alpha)


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


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
            f'<rect x="{x * MM:.2f}" y="{y_top * MM:.2f}" width="{w * MM:.2f}" height="{h * MM:.2f}" rx="{rx * MM:.2f}" fill="{fill}" stroke="{sw}" stroke-width="{lw}"/>'
        )

    def ribbon(self, x0, y0, x1, y1, thickness, fill: Color, svg_fill: str, svg_opacity: float):
        mid = (x0 + x1) / 2
        p = self.c.beginPath()
        p.moveTo(x0 * MM, self._y(y0))
        p.curveTo(mid * MM, self._y(y0), mid * MM, self._y(y1), x1 * MM, self._y(y1))
        p.lineTo(x1 * MM, self._y(y1 + thickness))
        p.curveTo(
            mid * MM,
            self._y(y1 + thickness),
            mid * MM,
            self._y(y0 + thickness),
            x0 * MM,
            self._y(y0 + thickness),
        )
        p.close()
        self.c.setFillColor(fill)
        self.c.drawPath(p, fill=1, stroke=0)
        self.svg.append(
            f'<path d="M {x0 * MM:.2f} {y0 * MM:.2f} C {mid * MM:.2f} {y0 * MM:.2f}, {mid * MM:.2f} {y1 * MM:.2f}, {x1 * MM:.2f} {y1 * MM:.2f} '
            f'L {x1 * MM:.2f} {(y1 + thickness) * MM:.2f} C {mid * MM:.2f} {(y1 + thickness) * MM:.2f}, {mid * MM:.2f} {(y0 + thickness) * MM:.2f}, {x0 * MM:.2f} {(y0 + thickness) * MM:.2f} Z" '
            f'fill="{svg_fill}" fill-opacity="{svg_opacity}" />'
        )

    def curve(self, x0, y0, x1, y1, color, lw=0.7):
        mid = (x0 + x1) / 2
        p = self.c.beginPath()
        p.moveTo(x0 * MM, self._y(y0))
        p.curveTo(mid * MM, self._y(y0), mid * MM, self._y(y1), x1 * MM, self._y(y1))
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(lw)
        self.c.setLineCap(1)
        self.c.drawPath(p, fill=0, stroke=1)
        self.svg.append(
            f'<path d="M {x0 * MM:.2f} {y0 * MM:.2f} C {mid * MM:.2f} {y0 * MM:.2f}, {mid * MM:.2f} {y1 * MM:.2f}, {x1 * MM:.2f} {y1 * MM:.2f}" fill="none" stroke="{color}" stroke-width="{lw}" stroke-linecap="round"/>'
        )

    def leader(self, x0, y0, x1, y1, color, lw=0.65, hold=0.72):
        """Stay near y0 until `hold` of the x-span, then drop to the box."""
        xb = x0 + (x1 - x0) * hold
        c1x, c2x = xb + (x1 - xb) * 0.35, xb + (x1 - xb) * 0.75
        p = self.c.beginPath()
        p.moveTo(x0 * MM, self._y(y0))
        p.lineTo(xb * MM, self._y(y0))
        p.curveTo(c1x * MM, self._y(y0), c2x * MM, self._y(y1), x1 * MM, self._y(y1))
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(lw)
        self.c.setLineCap(1)
        self.c.drawPath(p, fill=0, stroke=1)
        self.svg.append(
            f'<path d="M {x0 * MM:.2f} {y0 * MM:.2f} L {xb * MM:.2f} {y0 * MM:.2f} '
            f'C {c1x * MM:.2f} {y0 * MM:.2f}, {c2x * MM:.2f} {y1 * MM:.2f}, {x1 * MM:.2f} {y1 * MM:.2f}" '
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
            f'<text x="{x * MM:.2f}" y="{y_top * MM:.2f}" font-family="FigureSans" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>'
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


def layout():
    corpora = {c["id"]: c for c in META["corpora"]}
    pad_l, box_x = 16.0, 93.5
    header, footer = 22.0, 11.0
    band_gap = 5.5
    node_w = 2.15
    order = ["de", "cn", "bt"]
    inner_h = H - header - footer - band_gap * 2
    band_h = inner_h / 3
    col_n = 4
    span = box_x - 5.5 - pad_l - node_w
    col_x = [pad_l + i * span / (col_n - 1) for i in range(col_n)]
    bands = []
    for i, cid in enumerate(order):
        bands.append({"id": cid, "y": header + i * (band_h + band_gap), "h": band_h, **corpora[cid]})

    nodes = [
        {"id": nid, "corpus": corpus, "label": label, "column": col, "value": value, "role": role}
        for nid, corpus, label, col, value, role in NODES
    ]
    laid = []
    index = {}
    gap = 1.35
    for band in bands:
        group = [n for n in nodes if n["corpus"] == band["id"]]
        by_col: dict[int, list] = {}
        for n in group:
            by_col.setdefault(n["column"], []).append(n)
        base = band["base"]
        max_nodes = max(len(v) for v in by_col.values())
        px = (band["h"] - gap * (max_nodes - 1)) / base
        for c in range(col_n):
            y = band["y"]
            for n in by_col.get(c, []):
                h = max(1.05, n["value"] * px)
                item = {
                    **n,
                    "x": col_x[c],
                    "y": y,
                    "h": h,
                    "px": px,
                    "band_y": band["y"],
                    "band_bottom": band["y"] + band["h"],
                }
                laid.append(item)
                index[n["id"]] = item
                y += h + gap

    out_off: dict[str, float] = {}
    in_off: dict[str, float] = {}
    links = []
    for src, tgt, value in LINKS:
        s, t = index[src], index[tgt]
        thick = max(1.05, value * t["px"])
        sy = out_off.get(s["id"], 0.0)
        ty = in_off.get(t["id"], 0.0)
        out_off[s["id"]] = sy + thick
        in_off[t["id"]] = ty + thick
        links.append(
            {
                "s": s,
                "t": t,
                "thick": thick,
                "y0": s["y"] + sy,
                "y1": t["y"] + ty,
                "corpus": s["corpus"],
                "role": t["role"],
            }
        )
    return bands, laid, links, col_x, node_w, box_x, index


def place_labels(laid, min_gap=3.9):
    groups: dict[tuple, list] = {}
    for n in laid:
        groups.setdefault((n["corpus"], n["column"]), []).append(n)
    for nodes in groups.values():
        nodes.sort(key=lambda n: n["y"])
        ys = []
        top = nodes[0]["band_y"] + 2.0
        bottom = nodes[0]["band_bottom"] - 0.8
        for n in nodes:
            y = n["y"] + max(2.1, n["h"] / 2)
            if ys and y < ys[-1] + min_gap:
                y = ys[-1] + min_gap
            n["label_y"] = min(max(y, top), bottom)
            ys.append(n["label_y"])


def draw():
    bands, laid, links, col_x, node_w, box_x, index = layout()
    place_labels(laid)
    # Sit "Kodiertabelle 203" in the upper body, left of the thin 55-bar rather than on 148.
    kod = index["de_kod"]
    kod["label_y"] = min(kod["label_y"], kod["y"] + 8.4)
    # Pin CN labels to their own nodes; do not share a stacked height.
    kern = index["cn_kern"]
    nokern = index["cn_nokern"]
    kern["label_y"] = kern["y"] + kern["h"] / 2
    nokern["label_y"] = nokern["y"] + nokern["h"] / 2
    colors = {c["id"]: c["color"] for c in META["corpora"]}
    fig = Fig(W, H)
    fig.text(3.5, 7.2, META["title"], 10, "bold")
    fig.text(3.5, 12.8, META["subtitle"], 7.5, color=MUTED)

    for band in bands:
        fig.rect(2.2, band["y"] - 0.8, W - 4.4, band["h"] + 1.6, PALE, "none", 0, rx=1.0)
        fig.text(3.6, band["y"] + 4.6, band["title"], 8, "bold", band["color"])
        fig.text(3.6, band["y"] + 10.2, band["harvest"], 11, "bold")
        fig.text(3.6, band["y"] + 14.8, band["note"], 6, color=MUTED)

    for i, name in enumerate(META["columns"]):
        if i < len(col_x):
            x = col_x[i] + node_w / 2
        else:
            x = box_x + 12.2
        fig.text(x, 19.2, name, 6.5, color=MUTED, ha="center")

    for link in links:
        color = OUT if link["role"] == "out" else colors[link["corpus"]]
        alpha = 0.26 if link["role"] == "out" else 0.44
        fig.ribbon(
            link["s"]["x"] + node_w,
            link["y0"],
            link["t"]["x"],
            link["y1"],
            link["thick"],
            hex_alpha(color, alpha),
            color,
            alpha,
        )

    for n in laid:
        fill = OUT if n["role"] == "out" else colors[n["corpus"]]
        fig.rect(n["x"], n["y"], node_w, n["h"], fill, "none", 0, rx=0.35)
        if n["id"] in SKIP_LABEL:
            continue
        main = f"{n['label']} {fmt(n['value'])}"
        size = 6.5
        lx = n["x"] + node_w + 1.15
        nxt = [m["x"] for m in laid if m["corpus"] == n["corpus"] and m["column"] == n["column"] + 1]
        limit = W - 1.6 if n["column"] == 3 or not nxt else min(nxt) - 0.45
        while size > 6.0:
            if lx + pdfmetrics.stringWidth(main, "FigureSans", size) / MM <= limit:
                break
            size -= 0.5
        tw = pdfmetrics.stringWidth(main, "FigureSans", size) / MM + 0.8
        fig.rect(lx - 0.3, n["label_y"] - 2.0, tw, 3.05, "#ffffff", "none", 0, rx=0.25)
        fig.text(lx, n["label_y"] - 0.2, main, size)

    box_w = 25.3
    box_gap = 1.4

    def box_height(lines: list[str]) -> float:
        return 4.2 + 3.4 * len(lines)

    per_band: dict[str, list] = {}
    for band_id, src_id, lines in BOXES:
        per_band.setdefault(band_id, []).append((src_id, lines))
    for band in bands:
        items = per_band.get(band["id"], [])
        if not items:
            continue
        heights = [box_height(lines) for _, lines in items]
        total_h = sum(heights) + box_gap * (len(items) - 1)
        anchor = {"de": 0.88, "cn": 0.62, "bt": 0.78}[band["id"]]
        by = band["y"] + max(1.4, (band["h"] - total_h) * anchor)
        color = colors[band["id"]]
        for (src_id, lines), bh in zip(items, heights):
            src = index[src_id]
            x0 = src["x"] + node_w + 0.2
            y1 = by + bh / 2
            if src_id == "de_kod":
                fig.curve(x0, src["y"] + src["h"] - 1.1, box_x, y1, color, 0.65)
            elif src_id == "cn_kern":
                # Start after "KI-Kern 32" so the rail stays on the orange node and
                # does not cross "nicht im Kern 88".
                label_w = pdfmetrics.stringWidth("KI-Kern 32", "FigureSans", 6.5) / MM
                fig.leader(
                    src["x"] + node_w + 1.15 + label_w + 0.7,
                    src["y"] + src["h"] / 2,
                    box_x,
                    y1,
                    color,
                    0.65,
                )
            else:
                fig.curve(x0, src["y"] + src["h"] / 2, box_x, y1, color, 0.65)
            fig.rect(box_x, by, box_w, bh, "#ffffff", LINE, 0.35, rx=0.55)
            fig.rect(box_x, by, 1.05, bh, color, "none", 0, rx=0.2)
            fig.text(box_x + 2.2, by + 3.6, lines[0], 6.5, "bold")
            for i, line in enumerate(lines[1:], start=1):
                fig.text(box_x + 2.2, by + 3.6 + i * 3.4, line, 6, color=MUTED)
            by += bh + box_gap

    fig.text(3.5, H - 6.5, "Grau: Abfluss aus dem jeweiligen Pfad. Rechte Felder: Bündelung, nicht Restmenge.", 6.5, color=MUTED)

    reading = (
        "Drei Bahnen gleicher Höhe. Bandbreite proportional zum jeweiligen "
        "Ausgangsbestand: DE 245, CN 962, BT 220. "
        "Familien und Kategorien sind nicht mengenproportional."
    )
    fig.save(META["stem"], META["title"], reading)


def booklet(stem: str):
    c = canvas.Canvas(str(ROOT / f"{stem}_mit_Lesetext.pdf"), pagesize=(595.276, 841.89))
    c.setTitle("Auswahlwege und analytische Verdichtung")
    c.setAuthor("Christoph auf der Horst")
    c.setFont("FigureSans", 12)
    c.drawString(48, 800, "Abbildung · Auswahlwege und analytische Verdichtung")
    img = ROOT / f"{stem}.png"
    w = 120 / 25.4 * 72
    h = 178 / 25.4 * 72
    c.drawImage(ImageReader(str(img)), (595.276 - w) / 2, 780 - h, width=w, height=h)
    y = 780 - h - 18
    c.setFont("FigureSans", 9)
    caption = META["caption"]
    for line in textwrap.wrap("Bildunterschrift: " + caption, 92, break_long_words=False):
        c.drawString(48, y, line)
        y -= 12
    c.showPage()
    reading = (ROOT / "Lesetext.md").read_text()
    # Drop the heading already used as title.
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
        "# Auswahlwege und analytische Verdichtung\n\n"
        "Publikationsfassung 120 × 178 mm zu `Aufsatz_v7_gekuerzt`, Kapitel 3. "
        "Drei Bahnen gleicher Höhe; Bandbreite proportional zum jeweiligen "
        "Ausgangsbestand (DE 245, CN 962, BT 220). "
        "Deutscher Auswahlweg 203 → 55 + 148 → 49 / 2 / 4. "
        "Qualitativer Bestand (30 + 29 Einträge) als überlappender, "
        "nicht mengenproportionaler Anschluss, nicht als zusätzlicher Abfluss. "
        "Kategorien und Familien als Bündelung.\n\n"
        f"- `{stem}.pdf` — Druckdatei, 120 mm breit\n"
        f"- `{stem}.svg` — Vektorgrafik\n"
        f"- `{stem}.png` — 400 dpi\n"
        f"- `{stem}_mit_Lesetext.pdf` — Abbildung plus Lesetext\n"
        "- `Lesetext.md` — editierbare Begleitfassung\n\n"
        "Reproduktion: `python3 build_sankey.py` (reportlab, pdftoppm). "
        "Schrift: Bitstream Vera, FONT_LICENSE.txt.\n"
    )
    files = [p for p in ROOT.iterdir() if p.name != "manifest.json" and p.suffix in {".pdf", ".svg", ".png", ".md", ".json", ".py", ".txt"}]
    (ROOT / "manifest.json").write_text(
        json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}, indent=2) + "\n"
    )
    print(f"Created {stem}.pdf/.svg/.png")


if __name__ == "__main__":
    main()
