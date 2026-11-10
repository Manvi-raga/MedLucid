"""Structured output the AI must return. The UI renders straight from this,
so the model never writes free-form HTML/markdown into the page."""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Finding(BaseModel):
    name: str = Field(description="Test or finding name exactly as printed in the report")
    value_text: str = Field(description="Result as printed, e.g. '142' or 'Positive'")
    unit: str = Field(default="", description="Unit as printed, may be empty")
    numeric_value: Optional[float] = Field(default=None, description="Result as a number if numeric, else null")
    ref_low: Optional[float] = Field(default=None, description="Lower end of the printed reference range, else null")
    ref_high: Optional[float] = Field(default=None, description="Upper end of the printed reference range, else null")
    reference_text: str = Field(default="", description="Reference range exactly as printed, may be empty")
    status: Literal["normal", "borderline", "attention"] = Field(
        description="normal = inside the printed range; borderline = just outside or on the edge; "
                    "attention = clearly outside. Judge ONLY against the range printed in the report."
    )
    plain_meaning: str = Field(description="Plain-language explanation (about Grade 8 reading level). Borderline or attention results: a 3-5 sentence paragraph covering what the test measures, where the value sits versus the printed range, what it is commonly associated with (as possibilities, never a diagnosis), and what it cannot tell. Normal results: 1-2 sentences.")
    source_quote: str = Field(description="The exact line or phrase from the report this finding came from")


class Term(BaseModel):
    term: str
    meaning: str = Field(description="One plain-language sentence")


class Explanation(BaseModel):
    is_medical_report: bool = Field(description="False if the document is not a lab report, prescription or clinical document")
    headline: str = Field(description="One calm sentence capturing the overall picture")
    summary: str = Field(description="4-6 sentence plain-language overview: how many results are in range versus flagged, which flagged ones matter most, and how related results connect")
    findings: list[Finding]
    concern_answer: str = Field(description="Direct, calm answer (4-6 sentences) to the patient's own typed concern, using this report's numbers and general health education in non-diagnostic wording. Say clearly what the report cannot tell them.")
    questions_for_doctor: list[str] = Field(description="Specific questions this patient should ask their doctor, tailored to the report and their concern. 4-6 if anything is flagged; 0-2 optional ones if everything is in range.")
    terms_explained: list[Term] = Field(description="Medical terms or abbreviations in the report, explained simply")
    limits_note: str = Field(description="What this explanation cannot know (history, symptoms, other results)")
    seek_care_note: Optional[str] = Field(default=None, description="Only if values look urgent per the report's own flags: advise contacting a doctor promptly. Otherwise null.")
