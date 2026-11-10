"""Simple schematic illustrations we draw ourselves (inline SVG, no images, no network).

Each picture is a 3-panel scale (lower / in range / higher) with a marker under the panel that
matches the patient's result. They show the GENERAL idea only, never the patient's own body."""
from html import escape

BLOOD = "#F6D5D3"
BLOOD_EDGE = "#E3A9A5"
INK = "#46606A"
TEAL = "#0F7C87"

LABELS = {
    "sugar": ("Lower", "In range", "Higher"),
    "cholesterol": ("Lower", "In range", "Higher"),
    "haemoglobin": ("Lower", "In range", "Higher"),
}

CAPTIONS = {
    "sugar": ("Sugar (glucose) travels in your blood. Your body uses insulin like a key that lets sugar into "
              "your cells for energy. The test shows how much sugar is in the blood at that moment."),
    "sugar_a1c": ("HbA1c is a look-back test: it reflects your average blood sugar over roughly the last "
                  "three months, not just one moment. More sugar in the blood over time means a higher number."),
    "cholesterol": ("LDL is a fatty particle carried in the blood. Over many years, higher levels are linked to "
                    "fatty deposits building up inside artery walls and narrowing them."),
    "haemoglobin": ("Haemoglobin is the protein inside red blood cells that carries oxygen around your body. "
                    "A lower level means the blood carries less oxygen with each beat. Many everyday things "
                    "can influence it."),
}

# fixed positions inside a 100 x 44 vessel (x, y), so pictures are identical every time
SUGAR_N = (2, 6, 12)
CELL_N = (3, 7, 12)
ARTERY_LUMEN = (24, 20, 14)

_POS = [(14, 12), (32, 30), (50, 14), (68, 31), (84, 13), (22, 24), (41, 22), (60, 24), (77, 24),
        (9, 30), (92, 28), (50, 33)]


def kind_for(name: str):
    n = (name or "").lower()
    if any(k in n for k in ("hba1c", "a1c", "glycated", "glycosylated")):
        return "sugar_a1c"
    if any(k in n for k in ("glucose", "blood sugar", "fasting sugar", "sugar")):
        return "sugar"
    if any(k in n for k in ("haemoglobin", "hemoglobin")):
        return "haemoglobin"
    if "hdl" in n:
        return None  # higher HDL is the "good" direction; no picture for it in this MVP
    if "ldl" in n or ("cholesterol" in n and "total" in n) or n.strip() == "cholesterol":
        return "cholesterol"
    return None


def position_index(f) -> int:
    """0 = below the printed range, 1 = inside, 2 = above."""
    v = f.numeric_value
    if v is None:
        return 1
    if f.ref_low is not None and v < f.ref_low:
        return 0
    if f.ref_high is not None and v > f.ref_high:
        return 2
    return 1


def _vessel(x):
    return (f'<rect x="{x}" y="14" width="100" height="44" rx="22" fill="{BLOOD}" stroke="{BLOOD_EDGE}" '
            f'stroke-width="1.5"/>')


def _sugar_panel(x, n):
    out = _vessel(x)
    for (px, py) in _POS[:n]:
        out += (f'<rect x="{x + px - 4}" y="{14 + py - 4}" width="8" height="8" rx="2" fill="#F2A93B"/>'
                f'<rect x="{x + px - 3}" y="{14 + py - 3}" width="3" height="3" rx="1" fill="#FFE2A8"/>')
    return out


def _cell_panel(x, n):
    out = _vessel(x)
    for (px, py) in _POS[:n]:
        cx, cy = x + px, 14 + py
        out += (f'<ellipse cx="{cx}" cy="{cy}" rx="7.5" ry="7.5" fill="#C93A3A"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="3.2" ry="3.2" fill="#E57B7B"/>')
    return out


def _artery_panel(x, lumen):
    cx, cy = x + 50, 36
    return (f'<circle cx="{cx}" cy="{cy}" r="30" fill="#E6A29B"/>'            # artery wall
            f'<circle cx="{cx}" cy="{cy}" r="26" fill="#F3E2A0"/>'            # room for deposits
            f'<circle cx="{cx}" cy="{cy}" r="{lumen}" fill="#D9534F"/>'       # open channel for blood
            f'<circle cx="{cx - lumen * 0.35:.1f}" cy="{cy - lumen * 0.35:.1f}" r="{lumen * 0.25:.1f}" fill="#EE8E8A"/>')


def schematic_svg(kind: str, f) -> str:
    base = "sugar" if kind.startswith("sugar") else kind
    idx = position_index(f)
    xs = [5, 130, 255]
    panels = ""
    for i, x in enumerate(xs):
        if base == "sugar":
            panels += _sugar_panel(x, SUGAR_N[i])
        elif base == "haemoglobin":
            panels += _cell_panel(x, CELL_N[i])
        else:
            panels += _artery_panel(x, ARTERY_LUMEN[i])
    labels = LABELS[base]
    texts = ""
    for i, x in enumerate(xs):
        weight = "700" if i == idx else "400"
        fill = TEAL if i == idx else INK
        texts += (f'<text x="{x + 50}" y="88" text-anchor="middle" font-size="11" font-weight="{weight}" '
                  f'fill="{fill}" font-family="sans-serif">{escape(labels[i])}</text>')
    mx = xs[idx] + 50
    marker = (f'<rect x="{xs[idx] - 4}" y="2" width="108" height="92" rx="12" fill="none" stroke="{TEAL}" '
              f'stroke-width="2" stroke-dasharray="4 3"/>'
              f'<path d="M{mx - 7} 102 L{mx + 7} 102 L{mx} 94 Z" fill="{TEAL}"/>'
              f'<text x="{mx}" y="116" text-anchor="middle" font-size="11" font-weight="700" fill="{TEAL}" '
              f'font-family="sans-serif">Your result</text>')
    # artery panels sit lower inside their frame; shift the viewBox so nothing is clipped
    return (f'<svg viewBox="0 0 360 122" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="Simplified illustration: lower, in range and higher, with your result marked">'
            f'{panels}{texts}{marker}</svg>')


def picture_html(f) -> str:
    """Returns an HTML block ('' if no picture applies to this finding)."""
    if f.numeric_value is None:
        return ""
    kind = kind_for(f.name)
    if not kind:
        return ""
    base = "sugar" if kind.startswith("sugar") else kind
    return (f'<details class="ml-src ml-pic"><summary>See it as a picture</summary>'
            f'{schematic_svg(kind, f)}'
            f'<p>{escape(CAPTIONS[kind])}</p>'
            f'<p class="ml-pic-note">Simplified illustration of the general idea. It is not a picture of your own body '
            f'and not a diagnosis.</p></details>')
