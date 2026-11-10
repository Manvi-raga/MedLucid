"""MedLucid — plain-language explanations of medical lab reports for people with flagged results.
Streamlit front end. Run locally:  streamlit run app.py
"""
import os

import streamlit as st

import ai
from samples import SAMPLE_CONCERN, SAMPLE_CONCERN_NORMAL, SAMPLE_REPORT, SAMPLE_REPORT_NORMAL
from ui import CSS, counts_html, export_text, finding_html, questions_html, esc, steps_html

st.set_page_config(page_title="MedLucid", page_icon="🩺", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

STATUS_ORDER = {"attention": 0, "borderline": 1, "normal": 2}
QUICK_CONCERNS = [
    "What do these terms mean?",
    "Is anything here serious?",
    "What should I ask my doctor?",
    "Do I need to repeat any test?",
]
SAMPLE_TEXT = {"flagged": SAMPLE_REPORT, "normal": SAMPLE_REPORT_NORMAL}
SAMPLE_CONCERNS = {"flagged": SAMPLE_CONCERN, "normal": SAMPLE_CONCERN_NORMAL}


def get_secret(name: str):
    if os.environ.get(name):
        return os.environ[name]
    try:
        return st.secrets.get(name)
    except Exception:  # no secrets file present
        return None


API_KEY = get_secret("GEMINI_API_KEY")
MODEL = get_secret("GEMINI_MODEL") or ai.DEFAULT_MODEL

# ---------- session state ----------
defaults = {"step": 1, "sample": None, "concern": "", "result": None, "is_demo": False, "used_concern": ""}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


def reset_all():
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1


def use_sample(kind: str):
    st.session_state.sample = kind
    st.session_state.concern = SAMPLE_CONCERNS[kind]


def add_quick_concern(pick: str):
    cur = st.session_state.concern.strip()
    st.session_state.concern = (cur + " " + pick).strip() if cur else pick


# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### About MedLucid")
    st.write("MedLucid helps people with flagged lab results understand them in plain language, "
             "answers *your* worry about the report, and gives you questions to take to your doctor.")
    st.markdown("### Your privacy")
    st.write("Your file is processed in memory for this session only. MedLucid has no database and "
             "does not save your report.")
    st.caption("Prototype notice: this is a student project. Please use the sample reports or a dummy "
               "report, not real medical records.")
    if st.button("Clear everything", use_container_width=True):
        reset_all()
        st.rerun()
    st.caption(f"AI mode: {'live (' + MODEL + ')' if API_KEY else 'demo (no API key set)'}")
    if API_KEY:
        with st.expander("Check available models"):
            if st.button("List models my key can use", use_container_width=True):
                try:
                    st.session_state["model_list"] = ai.list_models(API_KEY)
                except Exception as e:  # noqa: BLE001
                    st.session_state["model_list"] = [f"Could not list models: {type(e).__name__}"]
            for name in st.session_state.get("model_list", []):
                st.code(name, language=None)

# ---------- header ----------
st.markdown(
    '<div class="ml-brand"><div class="ml-logo">M</div><div class="ml-name">MedLucid</div></div>'
    '<div class="ml-tag">Got a lab report with values you don\'t understand? Get it explained in plain language, in your own words.</div>',
    unsafe_allow_html=True,
)
st.markdown(steps_html(st.session_state.step), unsafe_allow_html=True)

# =====================================================================
# STEP 1 — share report + concern
# =====================================================================
if st.session_state.step == 1:
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown('<div class="ml-sec">1 · Your report</div>'
                    '<div class="ml-sec-sub">Upload a lab report as a PDF or a clear photo.</div>',
                    unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload report", type=list(ai.SUPPORTED_MIME.keys()), label_visibility="collapsed",
            key=f"uploader_{st.session_state.get('uploader_key', 0)}",
        )
        pasted = st.text_area("…or paste the report text", height=110, key="pasted",
                              placeholder="Paste the text of your report here")
        c1, c2 = st.columns(2)
        c1.button("Try a sample with flagged values", on_click=use_sample, args=("flagged",), use_container_width=True)
        c2.button("Try an all-normal sample", on_click=use_sample, args=("normal",), use_container_width=True)
        if st.session_state.sample:
            if st.button("Remove sample", use_container_width=True):
                st.session_state.sample = None
                st.rerun()
            with st.expander("Preview sample report (synthetic data)"):
                st.code(SAMPLE_TEXT[st.session_state.sample], language=None)

    with right:
        st.markdown('<div class="ml-sec">2 · What is worrying you?</div>'
                    '<div class="ml-sec-sub">Tell us in your own words. We read this together with your report.</div>',
                    unsafe_allow_html=True)
        st.text_area("Your concern", key="concern", height=150, label_visibility="collapsed",
                     placeholder="e.g. My sugar number looks high. Should I be worried?")
        st.caption("Quick add")
        qc = st.columns(2)
        for i, q in enumerate(QUICK_CONCERNS):
            qc[i % 2].button(q, key=f"qc{i}", on_click=add_quick_concern, args=(q,), use_container_width=True)

    has_report = bool(uploaded) or bool(pasted.strip()) or bool(st.session_state.sample)
    st.write("")
    go = st.button("Explain my report", type="primary", disabled=not has_report)
    if not has_report:
        st.caption("Add a report (or try a sample) to continue.")

    if go:
        if uploaded:
            args = dict(file_bytes=uploaded.getvalue(), file_name=uploaded.name)
        elif pasted.strip():
            args = dict(report_text=pasted)
        else:
            args = dict(report_text=SAMPLE_TEXT[st.session_state.sample])
        try:
            with st.spinner("Reading your report and your question together…"):
                result, is_demo = ai.analyze(concern=st.session_state.concern, api_key=API_KEY, model=MODEL, **args)
            if not result.is_medical_report:
                st.warning("This doesn't look like a medical report. Please upload a lab report or prescription.")
            else:
                st.session_state.update(result=result, is_demo=is_demo,
                                        used_concern=st.session_state.concern, step=2)
                st.rerun()
        except ai.AnalysisError as e:
            st.error(str(e))

# =====================================================================
# STEP 2 — results
# =====================================================================
else:
    r = st.session_state.result
    flagged = [f for f in r.findings if f.status != "normal"]
    top = st.columns([1, 0.35])
    with top[1]:
        if st.button("← Explain another report", use_container_width=True):
            reset_all()
            st.rerun()

    if st.session_state.is_demo:
        st.markdown('<span class="ml-demo">DEMO MODE — pre-written sample output, not live AI</span>', unsafe_allow_html=True)

    clear = not flagged
    st.markdown(
        f'<div class="ml-hero {"clear" if clear else ""}"><div class="kicker">{"All clear" if clear else "Your report at a glance"}</div>'
        f'<div class="headline">{esc(r.headline)}</div><div class="summary">{esc(r.summary)}</div></div>',
        unsafe_allow_html=True,
    )
    if r.seek_care_note:
        st.markdown(f'<div class="ml-care"><b>Please speak to a doctor soon.</b> {esc(r.seek_care_note)}</div>',
                    unsafe_allow_html=True)

    if clear:
        # Short journey: nothing flagged, so no follow-up flow, just reassurance and the detail on request.
        if st.session_state.used_concern.strip():
            st.markdown(f'<div class="ml-card" style="background:#F1F6F7"><p><i>“{esc(st.session_state.used_concern)}”</i></p></div>',
                        unsafe_allow_html=True)
        st.markdown(f'<div class="ml-card"><h4>Your concern</h4><p>{esc(r.concern_answer)}</p></div>', unsafe_allow_html=True)
        if r.questions_for_doctor:
            st.markdown(questions_html(r.questions_for_doctor), unsafe_allow_html=True)
        with st.expander(f"See each of the {len(r.findings)} results"):
            for f in r.findings:
                st.markdown(finding_html(f), unsafe_allow_html=True)
        st.markdown(f'<div class="ml-note"><b>Limits.</b> {esc(r.limits_note)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(counts_html(r.findings), unsafe_allow_html=True)
        col_a, col_b = st.columns([1.35, 1], gap="large")
        with col_a:
            st.markdown("#### Your results, explained")
            only_flagged = st.toggle("Show only results worth asking my doctor about", value=False,
                                     help="Hides the normal results. Switch off to see everything.")
            shown = [f for f in r.findings if f.status != "normal"] if only_flagged else list(r.findings)
            hidden = len(r.findings) - len(shown)
            for f in sorted(shown, key=lambda x: STATUS_ORDER[x.status]):
                st.markdown(finding_html(f), unsafe_allow_html=True)
            if only_flagged and hidden:
                st.caption(f"{hidden} normal result{'s' if hidden != 1 else ''} hidden. Switch the toggle off to see them.")

        with col_b:
            st.markdown("#### Your concern")
            if st.session_state.used_concern.strip():
                st.markdown(f'<div class="ml-card" style="background:#F1F6F7"><p><i>“{esc(st.session_state.used_concern)}”</i></p></div>',
                            unsafe_allow_html=True)
            st.markdown(f'<div class="ml-card"><h4>What the report can and can’t tell you</h4><p>{esc(r.concern_answer)}</p></div>',
                        unsafe_allow_html=True)
            st.markdown(questions_html(r.questions_for_doctor), unsafe_allow_html=True)
            if r.terms_explained:
                with st.expander("Medical terms in plain words"):
                    for t in r.terms_explained:
                        st.markdown(f"**{t.term}** — {t.meaning}")
            st.markdown(f'<div class="ml-note"><b>Limits.</b> {esc(r.limits_note)}</div>', unsafe_allow_html=True)
            st.download_button("Download summary + questions", data=export_text(r, st.session_state.used_concern),
                               file_name="medlucid-summary.txt", mime="text/plain", use_container_width=True)

    st.markdown(
        '<div class="ml-disclaimer">MedLucid explains reports in plain language. It is not a diagnosis, '
        'does not recommend treatment, and does not replace your doctor. AI can make mistakes: check the '
        '“where this came from” line on each result, and confirm everything with your doctor.</div>',
        unsafe_allow_html=True,
    )
