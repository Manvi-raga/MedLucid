"""Synthetic sample reports + pre-written explanations used in DEMO MODE (no API key).
All data here is invented; no real patient."""
from schema import Explanation, Finding, Term

SAMPLE_CONCERN = "I'm worried about my sugar and cholesterol numbers. Is any of this serious, and what should I ask my doctor?"
SAMPLE_CONCERN_NORMAL = "This is my yearly check-up. Is everything fine?"

SAMPLE_REPORT = """\
SAMPLE DIAGNOSTICS LAB  (synthetic data for demonstration only)
Patient: Demo Patient      Age/Sex: 42 / F      Sample: Fasting venous blood

TEST                      RESULT     UNIT      REFERENCE RANGE
Haemoglobin               11.2       g/dL      12.0 - 15.5
Fasting Blood Glucose     108        mg/dL     70 - 99
HbA1c                     5.9        %         Below 5.7 (normal); 5.7-6.4 (prediabetes range)
Total Cholesterol         221        mg/dL     Below 200
LDL Cholesterol           142        mg/dL     Below 100 (optimal)
HDL Cholesterol           52         mg/dL     Above 50
Triglycerides             168        mg/dL     Below 150
TSH                       2.4        uIU/mL    0.4 - 4.0
Creatinine                0.9        mg/dL     0.6 - 1.1
Vitamin D (25-OH)         18         ng/mL     30 - 100

Lab comment: Results to be correlated clinically.
"""

SAMPLE_REPORT_NORMAL = """\
SAMPLE DIAGNOSTICS LAB  (synthetic data for demonstration only)
Patient: Demo Patient      Age/Sex: 35 / M      Sample: Fasting venous blood

TEST                      RESULT     UNIT      REFERENCE RANGE
Haemoglobin               14.6       g/dL      13.5 - 17.5
Fasting Blood Glucose     88         mg/dL     70 - 99
HbA1c                     5.2        %         Below 5.7
LDL Cholesterol           92         mg/dL     Below 100
TSH                       2.1        uIU/mL    0.4 - 4.0
Creatinine                0.9        mg/dL     0.7 - 1.3

Lab comment: All values within reference limits.
"""

SAMPLES = {SAMPLE_REPORT.strip(): "flagged", SAMPLE_REPORT_NORMAL.strip(): "normal"}


def _f(name, value, unit, num, lo, hi, ref, status, meaning, quote):
    return Finding(name=name, value_text=value, unit=unit, numeric_value=num, ref_low=lo, ref_high=hi,
                   reference_text=ref, status=status, plain_meaning=meaning, source_quote=quote)


def demo_explanation(kind: str = "flagged") -> Explanation:
    return _demo_normal() if kind == "normal" else _demo_flagged()


def _demo_normal() -> Explanation:
    f = _f
    return Explanation(
        is_medical_report=True,
        headline="All of your results are inside the lab's expected ranges.",
        summary=("This report covers blood count, blood sugar, cholesterol, thyroid and kidney function. "
                 "Every value sits inside the range printed by the lab, and the lab's own comment says the same. "
                 "There is nothing here that needs follow-up on its own."),
        findings=[
            f("Haemoglobin", "14.6", "g/dL", 14.6, 13.5, 17.5, "13.5 - 17.5", "normal", "The protein in red blood cells that carries oxygen. Inside the lab's range.", "Haemoglobin  14.6  g/dL  13.5 - 17.5"),
            f("Fasting Blood Glucose", "88", "mg/dL", 88, 70, 99, "70 - 99", "normal", "Sugar in your blood after not eating overnight. Inside the lab's range.", "Fasting Blood Glucose  88  mg/dL  70 - 99"),
            f("HbA1c", "5.2", "%", 5.2, None, 5.7, "Below 5.7", "normal", "Your average blood sugar over about three months. Inside the lab's range.", "HbA1c  5.2  %  Below 5.7"),
            f("LDL Cholesterol", "92", "mg/dL", 92, None, 100, "Below 100", "normal", "Often called 'bad' cholesterol. Inside the lab's range.", "LDL Cholesterol  92  mg/dL  Below 100"),
            f("TSH", "2.1", "uIU/mL", 2.1, 0.4, 4.0, "0.4 - 4.0", "normal", "A signal from the brain that controls the thyroid gland. Inside the lab's range.", "TSH  2.1  uIU/mL  0.4 - 4.0"),
            f("Creatinine", "0.9", "mg/dL", 0.9, 0.7, 1.3, "0.7 - 1.3", "normal", "A waste product the kidneys clear. Inside the lab's range.", "Creatinine  0.9  mg/dL  0.7 - 1.3"),
        ],
        concern_answer=("You asked whether everything is fine. Based on this report alone, every value is inside the lab's range, "
                        "which is reassuring. A report cannot cover how you feel or your history, so if you have symptoms, mention them to your doctor."),
        questions_for_doctor=["When should I repeat this check-up?"],
        terms_explained=[Term(term="Fasting", meaning="The sample was taken after not eating for several hours, usually overnight."),
                         Term(term="HbA1c", meaning="A blood test showing your average blood sugar over roughly three months.")],
        limits_note="This explanation only uses what is printed in your report. It does not know your symptoms, medicines or history.",
        seek_care_note=None,
    )


def _demo_flagged() -> Explanation:
    f = _f
    return Explanation(
        is_medical_report=True,
        headline="Most results are in range; a few related to blood sugar, cholesterol and vitamin D are worth discussing.",
        summary=(
            "This report covers blood count, blood sugar, cholesterol, thyroid, kidney and vitamin D. "
            "Your thyroid, kidney and HDL ('good') cholesterol results sit inside the lab's range. "
            "Several results sit a little outside it: blood sugar markers, LDL cholesterol, triglycerides, "
            "haemoglobin and vitamin D. None of these alone tells us what is happening, but together they "
            "are a good reason for a conversation with your doctor."
        ),
        findings=[
            f("Fasting Blood Glucose", "108", "mg/dL", 108, 70, 99, "70 - 99", "borderline",
              "This is the sugar in your blood after not eating overnight. Yours is slightly above the lab's range, which is often a reason to recheck rather than a conclusion.",
              "Fasting Blood Glucose  108  mg/dL  70 - 99"),
            f("HbA1c", "5.9", "%", 5.9, None, 5.7, "Below 5.7 (normal); 5.7-6.4 (prediabetes range)", "borderline",
              "HbA1c reflects your average blood sugar over about three months. The report itself labels 5.7-6.4 as the 'prediabetes range', so this is worth discussing with your doctor.",
              "HbA1c  5.9  %  Below 5.7 (normal); 5.7-6.4 (prediabetes range)"),
            f("LDL Cholesterol", "142", "mg/dL", 142, None, 100, "Below 100 (optimal)", "attention",
              "LDL is often called 'bad' cholesterol because high levels are linked to fatty build-up in blood vessels over time. Yours is above the lab's optimal level.",
              "LDL Cholesterol  142  mg/dL  Below 100 (optimal)"),
            f("Total Cholesterol", "221", "mg/dL", 221, None, 200, "Below 200", "borderline",
              "The overall amount of cholesterol in your blood. Slightly above the lab's range, mainly driven by the LDL part.",
              "Total Cholesterol  221  mg/dL  Below 200"),
            f("Triglycerides", "168", "mg/dL", 168, None, 150, "Below 150", "borderline",
              "A type of fat in your blood that can be affected by meals, weight and sugar levels. Mildly above range.",
              "Triglycerides  168  mg/dL  Below 150"),
            f("HDL Cholesterol", "52", "mg/dL", 52, 50, None, "Above 50", "normal",
              "HDL is the 'good' cholesterol that helps carry fat away. Yours is inside the lab's range.",
              "HDL Cholesterol  52  mg/dL  Above 50"),
            f("Haemoglobin", "11.2", "g/dL", 11.2, 12.0, 15.5, "12.0 - 15.5", "attention",
              "Haemoglobin is the protein in red blood cells that carries oxygen. Yours is below the lab's range, which can have several causes; your doctor can help work out which.",
              "Haemoglobin  11.2  g/dL  12.0 - 15.5"),
            f("Vitamin D (25-OH)", "18", "ng/mL", 18, 30, 100, "30 - 100", "attention",
              "Vitamin D supports bones and muscles. Yours is below the lab's range, which is common and something to discuss with your doctor.",
              "Vitamin D (25-OH)  18  ng/mL  30 - 100"),
            f("TSH", "2.4", "uIU/mL", 2.4, 0.4, 4.0, "0.4 - 4.0", "normal",
              "TSH is a signal from the brain that controls the thyroid gland. Yours is inside the lab's range.",
              "TSH  2.4  uIU/mL  0.4 - 4.0"),
            f("Creatinine", "0.9", "mg/dL", 0.9, 0.6, 1.1, "0.6 - 1.1", "normal",
              "A waste product that the kidneys clear. Yours is inside the lab's range.",
              "Creatinine  0.9  mg/dL  0.6 - 1.1"),
        ],
        concern_answer=(
            "You asked about sugar and cholesterol. Your fasting glucose (108) and HbA1c (5.9%) are a little above "
            "the lab's normal range, and the report itself places 5.9% in the 'prediabetes range'. Your LDL (142) and "
            "total cholesterol (221) are also above the listed limits. These are common findings and are usually "
            "discussed and rechecked rather than treated as an emergency, but this report alone cannot say how serious "
            "they are for you; that depends on your age, family history, symptoms and other tests, which only your doctor knows."
        ),
        questions_for_doctor=[
            "My HbA1c is 5.9% and fasting glucose is 108. Do I need a repeat test, and when?",
            "My LDL is 142. What is my overall heart-risk picture, and does it need action now or just monitoring?",
            "My haemoglobin and vitamin D are below range. Should we look for a cause, and do I need any follow-up tests?",
            "Which lifestyle changes would help most with sugar and cholesterol in my case?",
            "When should I repeat these tests, and is there anything I should do before the next one?",
        ],
        terms_explained=[
            Term(term="HbA1c", meaning="A blood test showing your average blood sugar over roughly the last three months."),
            Term(term="LDL / HDL", meaning="Two kinds of cholesterol, often called 'bad' (LDL) and 'good' (HDL)."),
            Term(term="Fasting", meaning="The blood sample was taken after not eating for several hours, usually overnight."),
            Term(term="TSH", meaning="Thyroid-stimulating hormone; a signal that tells the thyroid gland how much to work."),
        ],
        limits_note=(
            "This explanation only uses what is printed in your report. It does not know your symptoms, medicines, "
            "history or earlier results, so it cannot say what is causing any result or what you should do about it."
        ),
        seek_care_note=None,
    )
