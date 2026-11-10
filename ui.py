"""Presentation helpers: CSS and small HTML builders. No AI logic here."""
import html
from typing import Optional

CSS = """
<style>
#MainMenu, footer, header [data-testid="stToolbar"] {visibility: hidden;}
.block-container, [data-testid="stMainBlockContainer"] {padding-top: 3.6rem !important; padding-bottom: 3rem; max-width: 1080px;}
h1, h2, h3 {font-family: Georgia, 'Cambria', serif; color: #0B2E3A; letter-spacing: -0.01em;}

.ml-brand {display:flex; align-items:center; gap:.65rem; margin-bottom:.2rem;}
.ml-logo {width:38px; height:38px; border-radius:11px; background:linear-gradient(135deg,#028090,#02C39A);
  display:flex; align-items:center; justify-content:center; color:#fff; font-weight:700; font-family:Georgia,serif; font-size:1.2rem;}
.ml-name {font-family:Georgia,serif; font-size:1.55rem; font-weight:700; color:#0B2E3A;}
.ml-tag {color:#5B6B72; margin:.1rem 0 1.1rem 0;}

.ml-steps {display:flex; gap:.6rem; margin:.4rem 0 1.4rem 0; flex-wrap:wrap;}
.ml-step {display:flex; align-items:center; gap:.55rem; padding:.45rem .9rem; border-radius:999px;
  background:#fff; border:1px solid #D7E3E6; color:#5B6B72; font-size:.9rem;}
.ml-step .n {width:22px; height:22px; border-radius:50%; background:#D7E3E6; color:#fff; font-weight:700;
  display:flex; align-items:center; justify-content:center; font-size:.8rem;}
.ml-step.on {border-color:#028090; color:#0B2E3A; font-weight:600;}
.ml-step.on .n {background:#028090;}
.ml-step.done .n {background:#02C39A;}

.ml-card {background:#fff; border:1px solid #D7E3E6; border-radius:16px; padding:1.1rem 1.25rem; margin-bottom:.9rem;
  box-shadow:0 1px 2px rgba(11,46,58,.04);}
.ml-card h4 {margin:0 0 .4rem 0; font-family:Georgia,serif; color:#0B2E3A; font-size:1.05rem;}
.ml-card p {margin:.25rem 0; line-height:1.55; color:#1F2D33;}
.ml-hero {background:linear-gradient(135deg,#0B2E3A,#04586A); border-radius:18px; padding:1.4rem 1.5rem; color:#fff; margin-bottom:1rem;}
.ml-hero.clear {background:linear-gradient(135deg,#0B5B4A,#0E8F6E);}
.ml-hero .kicker {text-transform:uppercase; letter-spacing:.08em; font-size:.72rem; color:#9FE3D4; margin-bottom:.35rem;}
.ml-hero .headline {font-family:Georgia,serif; font-size:1.35rem; line-height:1.35; margin-bottom:.6rem;}
.ml-hero .summary {color:#D5ECEA; line-height:1.55; font-size:.97rem;}

.ml-counts {display:flex; gap:.7rem; margin-bottom:1rem; flex-wrap:wrap;}
.ml-count {flex:1; min-width:150px; border-radius:14px; padding:.7rem .95rem; border:1px solid transparent;}
.ml-count .num {font-family:Georgia,serif; font-size:1.7rem; font-weight:700; line-height:1.1;}
.ml-count .lbl {font-size:.82rem;}

.ml-find {background:#fff; border:1px solid #D7E3E6; border-left-width:5px; border-radius:14px; padding:.9rem 1.1rem; margin-bottom:.7rem;}
.ml-find-top {display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap;}
.ml-find-name {font-weight:700; color:#0B2E3A; font-size:1.02rem;}
.ml-find-val {font-family:Georgia,serif; font-size:1.25rem; font-weight:700; color:#0B2E3A;}
.ml-find-val small {font-family:inherit; font-weight:400; color:#5B6B72; font-size:.8rem;}
.ml-pill {display:inline-block; padding:.12rem .6rem; border-radius:999px; font-size:.74rem; font-weight:600; margin-top:.15rem;}
.ml-meaning {margin:.55rem 0 .2rem 0; line-height:1.55; color:#1F2D33; font-size:.95rem;}
.ml-src {font-size:.82rem; color:#5B6B72; margin-top:.35rem;}
.ml-src summary {cursor:pointer; color:#028090;}
.ml-src code {background:#F1F6F7; padding:.1rem .35rem; border-radius:5px; color:#1F2D33; font-size:.8rem;}

.ml-bar {position:relative; height:10px; border-radius:6px; background:#E6ECEE; margin:.7rem 0 .15rem 0;}
.ml-zone {position:absolute; top:0; height:10px; border-radius:6px; background:#BFE9DF;}
.ml-mark {position:absolute; top:-5px; width:6px; height:20px; border-radius:3px; transform:translateX(-3px);}
.ml-bar-lbls {display:flex; justify-content:space-between; font-size:.72rem; color:#5B6B72;}

.ml-q {display:flex; gap:.7rem; padding:.55rem 0; border-bottom:1px dashed #D7E3E6;}
.ml-q:last-child {border-bottom:none;}
.ml-q .qn {flex:0 0 26px; height:26px; border-radius:50%; background:#E8F4F4; color:#028090; font-weight:700;
  display:flex; align-items:center; justify-content:center; font-size:.82rem;}
.ml-q .qt {line-height:1.5;}

.ml-note {background:#FFF8E8; border:1px solid #F0DDB0; border-radius:14px; padding:.8rem 1rem; color:#5A4300; font-size:.9rem; line-height:1.5; margin:.6rem 0;}
.ml-care {background:#FBE9E5; border:1px solid #F0C0B6; border-radius:14px; padding:.8rem 1rem; color:#7A2A1D; font-size:.95rem; line-height:1.5; margin-bottom:1rem;}
.ml-disclaimer {font-size:.8rem; color:#5B6B72; text-align:center; margin-top:1.4rem; line-height:1.5;}
.ml-demo {display:inline-block; background:#FFF3DC; color:#8A5200; border:1px solid #F0DDB0; padding:.2rem .65rem; border-radius:999px; font-size:.78rem; font-weight:600; margin-bottom:.6rem;}
.ml-sec {font-family:Georgia,serif; font-weight:700; color:#0B2E3A; font-size:1.1rem; margin:.1rem 0 .1rem 0;}
.ml-sec-sub {color:#5B6B72; font-size:.9rem; margin-bottom:.5rem;}

div[data-testid="stButton"] > button[kind="primary"] {border-radius:12px; padding:.6rem 1.4rem; font-weight:600;}
div[data-testid="stButton"] > button {border-radius:12px;}
div[data-testid="stButton"] button p {white-space: normal; line-height:1.25;}
.ml-ico{display:inline-flex;align-items:center;justify-content:center;width:1.9rem;height:1.9rem;margin-right:.5rem;border-radius:50%;background:#E4F1F2;font-size:1.05rem;vertical-align:middle}
.ml-pic svg{display:block;width:100%;max-width:440px;margin:.6rem 0 .3rem}
.ml-pic p{margin:.3rem 0;font-size:.9rem;line-height:1.5}
.ml-pic .ml-pic-note{font-size:.78rem;color:#6B7F86}
</style>
"""

STATUS_STYLE = {
    "normal": {"label": "In the expected range", "fg": "#0B6B52", "bg": "#E3F6F0", "bar": "#0E8F6E"},
    "borderline": {"label": "On the edge / slightly outside", "fg": "#8A5200", "bg": "#FFF3DC", "bar": "#D68A00"},
    "attention": {"label": "Worth asking your doctor about", "fg": "#9B3322", "bg": "#FBE9E5", "bar": "#C8452F"},
}


def esc(text: str) -> str:
    return html.escape(text or "").replace("\n", "<br>")


def steps_html(active: int) -> str:
    def cls(i):
        return "on" if i == active else ("done" if i < active else "")
    items = [(1, "Share your report & concern"), (2, "Understand your results")]
    return '<div class="ml-steps">' + "".join(
        f'<div class="ml-step {cls(i)}"><span class="n">{"✓" if i < active else i}</span>{label}</div>' for i, label in items
    ) + "</div>"


def _fmt(x: float) -> str:
    return f"{x:g}"


def range_bar_html(value: Optional[float], low: Optional[float], high: Optional[float], color: str) -> str:
    """A small visual showing where the result sits against the printed reference range."""
    if value is None or (low is None and high is None):
        return ""
    zone_lo = low if low is not None else min(0.0, value)
    zone_hi = high if high is not None else max(value, low or 0) * 1.35
    a, b = min(zone_lo, value), max(zone_hi, value)
    pad = (b - a) * 0.3 or 1.0
    dmin, dmax = a - pad, b + pad
    if a >= 0:
        dmin = max(dmin, 0.0)
    span = dmax - dmin

    def pos(x):
        return max(0.0, min(100.0, (x - dmin) / span * 100))

    zl, zr = (0.0 if low is None else pos(zone_lo)), (100.0 if high is None else pos(zone_hi))
    lbl_l = _fmt(low) if low is not None else ""
    lbl_r = _fmt(high) if high is not None else ""
    return (
        f'<div class="ml-bar"><div class="ml-zone" style="left:{zl:.1f}%;width:{max(zr - zl, 1):.1f}%"></div>'
        f'<div class="ml-mark" style="left:{pos(value):.1f}%;background:{color}"></div></div>'
        f'<div class="ml-bar-lbls"><span>{"expected from " + lbl_l if lbl_l else ""}</span>'
        f'<span>{"up to " + lbl_r if lbl_r else ""}</span></div>'
    )


ICON_RULES = [
    (("haemoglobin", "hemoglobin", "hb ", "rbc", "red blood", "wbc", "white blood", "platelet", "hematocrit", "haematocrit", "pcv", "mcv", "mch", "esr", "cbc", "ferritin", "iron"), "🩸"),
    (("glucose", "sugar", "hba1c", "a1c", "fasting", "insulin"), "🍬"),
    (("cholesterol", "ldl", "hdl", "triglycer", "lipid", "vldl"), "🫀"),
    (("tsh", "thyroid", "t3", "t4"), "🦋"),
    (("creatinine", "urea", "bun", "uric", "egfr", "kidney", "urine", "albumin", "protein"), "🫘"),
    (("sgpt", "sgot", "alt", "ast", "bilirubin", "alkaline", "ggt", "liver"), "🧪"),
    (("vitamin", "b12", "folate", "calcium", "d3", "25-oh"), "☀️"),
]


def icon_for(name: str) -> str:
    n = (name or "").lower() + " "
    for keys, icon in ICON_RULES:
        if any(k in n for k in keys):
            return icon
    return "🔬"


from visuals import picture_html


def finding_html(f) -> str:
    st = STATUS_STYLE[f.status]
    bar = range_bar_html(f.numeric_value, f.ref_low, f.ref_high, st["bar"])
    ref = f'<div class="ml-src">Report range: {esc(f.reference_text)}</div>' if f.reference_text and not bar else ""
    src = (f'<details class="ml-src"><summary>Where this came from in your report</summary>'
           f'<code>{esc(f.source_quote)}</code></details>') if f.source_quote else ""
    return (
        f'<div class="ml-find" style="border-left-color:{st["bar"]}">'
        f'<div class="ml-find-top"><div><div class="ml-find-name"><span class="ml-ico">{icon_for(f.name)}</span>{esc(f.name)}</div>'
        f'<span class="ml-pill" style="background:{st["bg"]};color:{st["fg"]}">{st["label"]}</span></div>'
        f'<div class="ml-find-val">{esc(f.value_text)} <small>{esc(f.unit)}</small></div></div>'
        f'{bar}{ref}<div class="ml-meaning">{esc(f.plain_meaning)}</div>{picture_html(f)}{src}</div>'
    )


def counts_html(findings) -> str:
    counts = {k: sum(1 for f in findings if f.status == k) for k in STATUS_STYLE}
    cells = ""
    for k in ("normal", "borderline", "attention"):
        s = STATUS_STYLE[k]
        cells += (f'<div class="ml-count" style="background:{s["bg"]};color:{s["fg"]};border-color:{s["bar"]}33">'
                  f'<div class="num">{counts[k]}</div><div class="lbl">{s["label"]}</div></div>')
    return f'<div class="ml-counts">{cells}</div>'


def questions_html(questions) -> str:
    rows = "".join(f'<div class="ml-q"><div class="qn">{i}</div><div class="qt">{esc(q)}</div></div>'
                   for i, q in enumerate(questions, 1))
    return f'<div class="ml-card"><h4>Questions to take to your doctor</h4>{rows}</div>'


def export_text(result, concern: str) -> str:
    lines = ["MedLucid — plain-language summary (not medical advice)", "=" * 56, "",
             result.headline, "", result.summary, "", "YOUR CONCERN", concern or "(none typed)", "", result.concern_answer, "",
             "RESULTS"]
    for f in result.findings:
        lines.append(f"- {f.name}: {f.value_text} {f.unit} [{STATUS_STYLE[f.status]['label']}] — {f.plain_meaning}")
    if result.questions_for_doctor:
        lines += ["", "QUESTIONS FOR YOUR DOCTOR"] + [f"{i}. {q}" for i, q in enumerate(result.questions_for_doctor, 1)]
    lines += ["", "LIMITS", result.limits_note, "",
              "MedLucid explains reports in plain language. It does not diagnose or replace your doctor."]
    return "\n".join(lines)
