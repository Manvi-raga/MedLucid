"""The one AI capability: report + patient's own words  ->  structured plain-language explanation."""
from typing import Optional

from schema import Explanation
from prompts import SYSTEM_INSTRUCTION, build_user_message
from samples import SAMPLES, demo_explanation

DEFAULT_MODEL = "gemini-3.8-flash"
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

    # Hard time limit per attempt so the app never hangs for minutes.
    client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=40_000))  # 40 s
    candidates = []
    for m in [model, "gemini-3.8-flash", "gemini-flash-latest"]:
        if m and m not in candidates:
            candidates.append(m)

    import time

    def _busy(low):
        return any(k in low for k in ("503", "unavailable", "overloaded", "high demand", "429",
                                      "resource_exhausted", "timed out", "timeout", "deadline"))

    def _config(fast: bool):
        kwargs = dict(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=Explanation,
            temperature=0.2,
            max_output_tokens=6000,
        )
        if fast:
            # Little/no "thinking": reading a report into a fixed JSON shape does not need it.
            kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        return types.GenerateContentConfig(**kwargs)

    last_error = None
    result = None
    fast = True
    for m in candidates:
        for attempt in range(2):  # at most one retry per model
            try:
                resp = client.models.generate_content(model=m, contents=parts, config=_config(fast))
                parsed = getattr(resp, "parsed", None)
                result = parsed if isinstance(parsed, Explanation) \
                    else Explanation.model_validate_json(resp.text)
                break
            except Exception as e:  # noqa: BLE001
                last_error = e
                low = str(e).lower()
                if "thinking" in low and fast:
                    fast = False  # this model rejects the thinking setting: retry without it
                    continue
                if "404" in low or "not_found" in low or "no longer available" in low:
                    break  # model gone: next model
                if _busy(low) and attempt == 0:
                    time.sleep(1.5)
                    continue
                break
        if result is not None:
            break

    if result is None:
        e = last_error
        raw = str(e) if e else "unknown error"
        if api_key:
            raw = raw.replace(api_key, "***")
        low = raw.lower()
        detail = f" (technical detail: {type(e).__name__}: {raw[:300]})"
        if "api key" in low or "api_key_invalid" in low or "401" in low or "403" in low or "permission" in low:
            raise AnalysisError("The AI service rejected the API key. Check GEMINI_API_KEY in Secrets." + detail) from e
        if "503" in low or "unavailable" in low or "high demand" in low or "429" in low or "quota" in low or "resource_exhausted" in low:
            raise AnalysisError("Google's AI service is very busy right now. Please wait a minute and press Explain my report again." + detail) from e
        if "404" in low or "not_found" in low:
            raise AnalysisError("The AI model name is not available. Set GEMINI_MODEL in Secrets to a current model." + detail) from e
        raise AnalysisError("Something went wrong while reading the report. Please try again, or try a clearer file." + detail) from e

    return result, False


def list_models(api_key: str) -> list[str]:
    """Names of models this key can use for generating content (used by the sidebar check)."""
    from google import genai
    client = genai.Client(api_key=api_key)
    names = []
    for m in client.models.list():
        actions = getattr(m, "supported_actions", None) or []
        if "generateContent" in actions:
            names.append((m.name or "").replace("models/", ""))
    return sorted(set(n for n in names if n))
