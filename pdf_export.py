"""Builds the downloadable PDF so it looks like the app: hero, counts, result cards with range bars,
the simple pictures, questions for the doctor and limits. Pure Python (reportlab), no network."""
import io
import re
from datetime import date
from xml.sax.saxutils import escape as _xml_escape

from reportlab.graphics.shapes import Circle, Drawing, Ellipse, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (Flowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

import visuals as V

STATUS = {
    "normal": {"label": "In the expected range", "fg": "#0B6B52", "bg": "#E3F6F0", "bar": "#0E8F6E"},
    "borderline": {"label": "On the edge / slightly outside", "fg": "#8A5200", "bg": "#FFF3DC", "bar": "#D68A00"},
    "attention": {"label": "Worth asking your doctor about", "fg": "#9B3322", "bg": "#FBE9E5", "bar": "#C8452F"},
}
ORDER = {"attention": 0, "borderline": 1, "normal": 2}
INK = "#12313B"
MUTED = "#5C727A"
TEAL = "#0F7C87"
HERO = "#0F4A5C"

PAGE_W, PAGE_H = A4
MARGIN = 16 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

_REPL = {"‘": "'", "’": "'", "“": '"', "”": '"', "≥": ">=", "≤": "<=", "→": "->",
         "↔": "<->", "•": "-", " ": " ", "−": "-", "µ": "u", "μ": "u", "✓": "",
         "✕": "x", "≈": "~"}


def clean(text) -> str:
    """Keep text inside what the built-in PDF fonts can draw, then make it safe for Paragraph markup."""
    t = str(text or "")
    for k, v in _REPL.items():
        t = t.replace(k, v)
    t = t.encode("cp1252", "replace").decode("cp1252")
    return _xml_escape(t)


def _style(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=colors.HexColor(INK), alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)


S = {
    "body": _style("body"),
    "small": _style("small", fontSize=8, leading=11, textColor=colors.HexColor(MUTED)),
    "h2": _style("h2", fontName="Helvetica-Bold", fontSize=13, leading=16, spaceBefore=8, spaceAfter=5),
    "name": _style("name", fontName="Helvetica-Bold", fontSize=11, leading=14),
    "val": _style("val", fontName="Helvetica-Bold", fontSize=13, leading=15, alignment=2),
    "hero_h": _style("hero_h", fontName="Times-Bold", fontSize=15, leading=19, textColor=colors.white),
    "hero_b": _style("hero_b", fontSize=9.5, leading=13.5, textColor=colors.HexColor("#D6E7EB")),
    "hero_k": _style("hero_k", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=colors.HexColor("#8FC3CC")),
    "q": _style("q", leftIndent=0),
    "note": _style("note", fontSize=8.5, leading=12, textColor=colors.HexColor(MUTED)),
}


class RangeBar(Flowable):
    """Same geometry as the on-screen bar: shaded 'expected' zone, coloured marker for the result."""

    def __init__(self, width, value, low, high, color):
        super().__init__()
        self.w, self.value, self.low, self.high, self.color = width, value, low, high, color
        self.height = 24

    def wrap(self, aw, ah):
        return self.w, self.height

    def draw(self):
        v, low, high = self.value, self.low, self.high
        zone_lo = low if low is not None else min(0.0, v)
        zone_hi = high if high is not None else max(v, low or 0) * 1.35
        a, b = min(zone_lo, v), max(zone_hi, v)
        pad = (b - a) * 0.3 or 1.0
        dmin, dmax = a - pad, b + pad
        if a >= 0:
            dmin = max(dmin, 0.0)
        span = dmax - dmin

        def pos(x):
            return max(0.0, min(1.0, (x - dmin) / span)) * self.w

        c = self.canv
        y = 12
        c.setFillColor(colors.HexColor("#E6ECEE"))
        c.roundRect(0, y, self.w, 6, 3, stroke=0, fill=1)
        zl = 0 if low is None else pos(zone_lo)
        zr = self.w if high is None else pos(zone_hi)
        c.setFillColor(colors.HexColor("#BFE6DD"))
        c.roundRect(zl, y, max(zr - zl, 3), 6, 3, stroke=0, fill=1)
        c.setFillColor(colors.HexColor(self.color))
        c.roundRect(pos(v) - 1.8, y - 3, 3.6, 12, 1.5, stroke=0, fill=1)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(colors.HexColor(MUTED))
        if low is not None:
            c.drawString(0, 1, f"expected from {low:g}")
        if high is not None:
            c.drawRightString(self.w, 1, f"up to {high:g}")


def _picture(kind, f, width):
    H = 122
    d = Drawing(360, H)
    base = "sugar" if kind.startswith("sugar") else kind
    idx = V.position_index(f)
    xs = [5, 130, 255]
    teal = colors.HexColor(V.TEAL)
    for i, x in enumerate(xs):
        if base in ("sugar", "haemoglobin"):
            d.add(Rect(x, H - 58, 100, 44, rx=22, ry=22, fillColor=colors.HexColor(V.BLOOD),
                       strokeColor=colors.HexColor(V.BLOOD_EDGE), strokeWidth=1.5))
            n = V.SUGAR_N[i] if base == "sugar" else V.CELL_N[i]
            for (px, py) in V._POS[:n]:
                if base == "sugar":
                    d.add(Rect(x + px - 4, H - (14 + py) - 4, 8, 8, rx=2, ry=2, fillColor=colors.HexColor("#F2A93B"), strokeColor=None))
                    d.add(Rect(x + px - 3, H - (14 + py - 3) - 3, 3, 3, rx=1, ry=1, fillColor=colors.HexColor("#FFE2A8"), strokeColor=None))
                else:
                    d.add(Circle(x + px, H - (14 + py), 7.5, fillColor=colors.HexColor("#C93A3A"), strokeColor=None))
                    d.add(Circle(x + px, H - (14 + py), 3.2, fillColor=colors.HexColor("#E57B7B"), strokeColor=None))
        else:
            lumen = V.ARTERY_LUMEN[i]
            cx, cy = x + 50, H - 36
            d.add(Circle(cx, cy, 30, fillColor=colors.HexColor("#E6A29B"), strokeColor=None))
            d.add(Circle(cx, cy, 26, fillColor=colors.HexColor("#F3E2A0"), strokeColor=None))
            d.add(Circle(cx, cy, lumen, fillColor=colors.HexColor("#D9534F"), strokeColor=None))
            d.add(Circle(cx - lumen * 0.35, cy + lumen * 0.35, lumen * 0.25, fillColor=colors.HexColor("#EE8E8A"), strokeColor=None))
        d.add(String(x + 50, H - 88, V.LABELS[base][i], textAnchor="middle", fontSize=11,
                     fontName="Helvetica-Bold" if i == idx else "Helvetica",
                     fillColor=teal if i == idx else colors.HexColor(V.INK)))
    mx = xs[idx] + 50
    d.add(Rect(xs[idx] - 4, H - 94, 108, 92, rx=12, ry=12, fillColor=None, strokeColor=teal, strokeWidth=2,
               strokeDashArray=[4, 3]))
    d.add(Polygon([mx - 7, H - 102, mx + 7, H - 102, mx, H - 94], fillColor=teal, strokeColor=None))
    d.add(String(mx, H - 116, "Your result", textAnchor="middle", fontSize=11, fontName="Helvetica-Bold", fillColor=teal))
    s = width / 360.0
    d.scale(s, s)
    d.width, d.height = 360 * s, H * s
    d.hAlign = "LEFT"
    return d


def _pill(text, fg, bg):
    w = stringWidth(text, "Helvetica-Bold", 8) + 14
    p = Paragraph(f'<font color="{fg}"><b>{clean(text)}</b></font>', _style("pill", fontSize=8, leading=10))
    t = Table([[p]], colWidths=[w])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("ROUNDEDCORNERS", [8, 8, 8, 8])]))
    t.hAlign = "LEFT"
    return t


def _finding_card(f):
    st = STATUS[f.status]
    inner_w = CONTENT_W - 5 - 20
    head = Table(
        [[[Paragraph(clean(f.name), S["name"]), Spacer(1, 3), _pill(st["label"], st["fg"], st["bg"])],
          Paragraph(f'{clean(f.value_text)} <font size="8" color="{MUTED}">{clean(f.unit)}</font>', S["val"])]],
        colWidths=[inner_w * 0.68, inner_w * 0.32])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    content = [head, Spacer(1, 6)]
    if f.numeric_value is not None and (f.ref_low is not None or f.ref_high is not None):
        content += [RangeBar(inner_w, f.numeric_value, f.ref_low, f.ref_high, st["bar"]), Spacer(1, 4)]
    elif f.reference_text:
        content += [Paragraph(f"Report range: {clean(f.reference_text)}", S["small"]), Spacer(1, 3)]
    if getattr(f, "check_note", None):
        content += [Paragraph(f'<font color="#8A5200"><b>Check:</b> {clean(f.check_note)}</font>', S["small"]), Spacer(1, 3)]
    content.append(Paragraph(clean(f.plain_meaning), S["body"]))
    kind = V.kind_for(f.name) if f.numeric_value is not None else None
    if kind:
        base = "sugar" if kind.startswith("sugar") else kind
        content += [Spacer(1, 6), _picture(kind, f, min(300, inner_w)), Spacer(1, 2),
                    Paragraph(clean(V.CAPTIONS[kind]), S["note"]),
                    Paragraph("Simplified illustration of the general idea. It is not a picture of your own body and not a diagnosis.",
                              _style("n2", fontSize=7.5, leading=10, textColor=colors.HexColor("#8A9DA3")))]
    if f.source_quote:
        content += [Spacer(1, 4), Paragraph(f'<font color="{MUTED}">From your report:</font> <font name="Courier" size="8">{clean(f.source_quote)}</font>', S["small"])]
    card = Table([["", content]], colWidths=[5, CONTENT_W - 5])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(st["bar"])),
        ("BACKGROUND", (1, 0), (1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D5E1E4")),
        ("LEFTPADDING", (1, 0), (1, 0), 10), ("RIGHTPADDING", (1, 0), (1, 0), 10),
        ("TOPPADDING", (1, 0), (1, 0), 9), ("BOTTOMPADDING", (1, 0), (1, 0), 10),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return card


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor(MUTED))
    canvas.drawString(MARGIN, 10 * mm, "MedLucid explains reports in plain language. It is not a diagnosis and does not replace your doctor.")
    canvas.drawRightString(PAGE_W - MARGIN, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(result, concern: str = "") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=14 * mm,
                            bottomMargin=18 * mm, title="MedLucid summary", author="MedLucid (student prototype)")
    out = []

    # header
    hdr = Table([[Paragraph('<font name="Times-Bold" size="18" color="#12313B">MedLucid</font>', S["body"]),
                  Paragraph(f'Plain-language summary<br/>{date.today().strftime("%d %b %Y")}', _style("hr", fontSize=8.5, leading=11, alignment=2, textColor=colors.HexColor(MUTED)))]],
                colWidths=[CONTENT_W * 0.6, CONTENT_W * 0.4])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("LINEBELOW", (0, 0), (-1, 0), 1.2, colors.HexColor(TEAL)),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    out += [hdr, Spacer(1, 10)]

    # hero
    hero = Table([[[Paragraph("YOUR REPORT AT A GLANCE", S["hero_k"]), Spacer(1, 4),
                    Paragraph(clean(result.headline), S["hero_h"]), Spacer(1, 6),
                    Paragraph(clean(result.summary), S["hero_b"])]]], colWidths=[CONTENT_W])
    hero.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(HERO)), ("LEFTPADDING", (0, 0), (-1, -1), 14),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 12),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 13), ("ROUNDEDCORNERS", [10, 10, 10, 10])]))
    out += [hero, Spacer(1, 8)]

    # urgent note
    if getattr(result, "seek_care_note", None):
        sc = Table([[Paragraph(f"<b>Please read:</b> {clean(result.seek_care_note)}", S["body"])]], colWidths=[CONTENT_W])
        sc.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBE9E5")),
                                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C8452F")),
                                ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                                ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        out += [sc, Spacer(1, 8)]

    # counts
    cells = []
    for k in ("normal", "borderline", "attention"):
        n = sum(1 for f in result.findings if f.status == k)
        cells.append([Paragraph(f'<font name="Times-Bold" size="20" color="{STATUS[k]["fg"]}">{n}</font>',
                                _style("cn", fontSize=20, leading=24)),
                      Paragraph(f'<font color="{STATUS[k]["fg"]}" size="8">{STATUS[k]["label"]}</font>',
                                _style("cl", fontSize=8, leading=11))])
    gap = 6
    cw = (CONTENT_W - 2 * gap) / 3
    counts = Table([[cells[0], "", cells[1], "", cells[2]]], colWidths=[cw, gap, cw, gap, cw])
    counts.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.HexColor(STATUS["normal"]["bg"])),
                                ("BACKGROUND", (2, 0), (2, 0), colors.HexColor(STATUS["borderline"]["bg"])),
                                ("BACKGROUND", (4, 0), (4, 0), colors.HexColor(STATUS["attention"]["bg"])),
                                ("LEFTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 6),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("ROUNDEDCORNERS", [8, 8, 8, 8])]))
    out += [counts, Spacer(1, 4)]

    # concern
    if (concern or "").strip():
        out += [Paragraph("Your concern", S["h2"]),
                Paragraph(f'<i>"{clean(concern.strip())}"</i>', S["body"]), Spacer(1, 4)]
    if result.concern_answer:
        out += [Paragraph("What the report can and can't tell you", S["h2"]), Paragraph(clean(result.concern_answer), S["body"])]

    # findings
    if result.findings:
        out += [Paragraph("Your results, explained", S["h2"])]
        for f in sorted(result.findings, key=lambda x: ORDER[x.status]):
            out += [KeepTogether([_finding_card(f)]), Spacer(1, 7)]

    # questions
    if result.questions_for_doctor:
        out += [Paragraph("Questions to take to your doctor", S["h2"])]
        rows = [[Paragraph(f'<font name="Helvetica-Bold" color="{TEAL}">{i}</font>', S["body"]), Paragraph(clean(q), S["q"])]
                for i, q in enumerate(result.questions_for_doctor, 1)]
        qt = Table(rows, colWidths=[16, CONTENT_W - 16])
        qt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                                ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#E1EAEC")),
                                ("TOPPADDING", (0, 0), (-1, -1), 5)]))
        out += [qt]

    # terms
    if result.terms_explained:
        out += [Paragraph("Medical terms in plain words", S["h2"])]
        for t in result.terms_explained:
            out += [Paragraph(f"<b>{clean(t.term)}</b> - {clean(t.meaning)}", S["body"]), Spacer(1, 2)]

    # limits
    out += [Spacer(1, 8)]
    lim = Table([[Paragraph(f"<b>Limits.</b> {clean(result.limits_note)}", S["note"])]], colWidths=[CONTENT_W])
    lim.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F6F7")),
                             ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                             ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    out += [KeepTogether([lim])]

    doc.build(out, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
