"""The one AI capability: report + patient's own words  ->  structured plain-language explanation."""
from typing import Optional

from schema import Explanation
from prompts import SYSTEM_INSTRUCTION, build_user_message
from samples import SAMPLES, demo_explanation

DEFAULT_MODEL = "gemini-2.5-flash"
SUPPORTED_MIME = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}


class AnalysisError(Exception):
    """Raised with a message that is safe and friendly to show the user."""


def analyze(
    concern: str,
    api_key: Optional[str],
    file_bytes: Optional[bytes] = None,
    file_name: str = "",
    report_text: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> tuple[Explanation, bool]:
    """Returns (explanation, is_demo). Demo mode is used only when there is no API key
    AND the input is one of the built-in sample reports."""
    if not api_key:
        kind = SAMPLES.get((report_text or "").strip())
        if kind:
            return demo_explanation(kind), True
        raise AnalysisError(
            "No Gemini API key is configured, so only the built-in sample reports can be explained. "
            "Add GEMINI_API_KEY in the app settings to analyse your own file."
        )

    if not file_bytes and not (report_text and report_text.strip()):
        raise AnalysisError("Please add a report first (PDF, photo, or pasted text).")

    try:
        from google import genai
        from google.genai import types
    except ImportError as e:  # pragma: no cover
        raise AnalysisError("The AI library is not installed. Run: pip install -r requirements.txt") from e

    parts = []
    if file_bytes:
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        mime = SUPPORTED_MIME.get(ext)
        if not mime:
            raise AnalysisError("Unsupported file type. Please upload a PDF, PNG, JPG or WEBP.")
        parts.append(types.Part.from_bytes(data=file_bytes, mime_type=mime))
    if report_text and report_text.strip():
        parts.append("REPORT TEXT:\n" + report_text.strip())
    parts.append(build_user_message(concern))

    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=model,
            contents=parts,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=Explanation,
                temperature=0.2,
            ),
        )
        result = resp.parsed if isinstance(getattr(resp, "parsed", None), Explanation) \
            else Explanation.model_validate_json(resp.text)
    except AnalysisError:
        raise
    except Exception as e:
        msg = str(e).lower()
        if "api key" in msg or "permission" in msg or "401" in msg or "403" in msg:
            raise AnalysisError("The AI service rejected the API key. Check GEMINI_API_KEY.") from e
        if "429" in msg or "quota" in msg or "rate" in msg:
            raise AnalysisError("The AI service is busy or over its free limit. Please try again in a minute.") from e
        raise AnalysisError("Something went wrong while reading the report. Please try again, or try a clearer file.") from e

    return result, False
