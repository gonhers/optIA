from __future__ import annotations

import json
import re
from urllib import error, request

from .settings import get_llm_runtime_settings

STYLE_GUIDES = (
    (
        "Position the idea around the user's core goal",
        "Translate the prompt into a crisp product narrative",
        "End with a practical next step",
    ),
    (
        "Frame the answer like an operator's launch note",
        "Call out the clearest customer benefit",
        "Highlight a measurable outcome",
    ),
    (
        "Use a concise strategy tone",
        "Turn the prompt into a focused execution plan",
        "Close with a decision-ready summary",
    ),
    (
        "Lead with a polished product marketing angle",
        "Make the value proposition feel immediate and concrete",
        "Wrap with a crisp rollout recommendation",
    ),
    (
        "Write with an executive summary tone",
        "Surface the strategic takeaway before the details",
        "Finish with a confident recommendation",
    ),
    (
        "Approach the answer like a customer success update",
        "Tie the message to customer impact and day-to-day usefulness",
        "Close with a practical adoption suggestion",
    ),
    (
        "Shape the response like a launch-ready release note",
        "Prioritize the clearest functional improvement in the message",
        "End with a rollout detail that feels easy to execute",
    ),
    (
        "Use a consultative strategy voice",
        "Clarify what decision the reader should make next",
        "Finish with a guidance-oriented next move",
    ),
    (
        "Frame the response as a product ops brief",
        "Keep the messaging structured around outcomes and execution",
        "Close with an implementation-ready takeaway",
    ),
    (
        "Write from a growth-focused SaaS perspective",
        "Stress the differentiator that would increase user confidence",
        "End with a concise action path for the team",
    ),
    (
        "Present the answer like a founder update",
        "Keep the language direct, credible, and momentum-oriented",
        "Close with a next-step recommendation the team can ship quickly",
    ),
)

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
    "your",
}


def normalize_prompt(prompt: str) -> str:
    return re.sub(r"\s+", " ", prompt).strip()


def extract_focus_terms(prompt: str, limit: int = 4) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9']+", prompt.lower())
    keywords = [token for token in tokens if token not in STOP_WORDS and len(token) > 2]
    return keywords[:limit]


def simulate_llm_response(prompt: str, variant: int) -> str:
    clean_prompt = normalize_prompt(prompt)
    focus_terms = extract_focus_terms(clean_prompt)
    focus_summary = ", ".join(focus_terms) if focus_terms else "the main user intent"
    style = STYLE_GUIDES[variant % len(STYLE_GUIDES)]

    return (
        f"{style[0]} and keep the response grounded in {focus_summary}. "
        f"{style[1]} so the user immediately understands why it matters. "
        f"For the prompt '{clean_prompt}', emphasize clarity, confidence, and useful specifics. "
        f"{style[2]} that makes the recommendation easy to act on."
    )


def _resolve_chat_completions_url(base_url: str) -> str:
    normalized_base_url = base_url.rstrip("/")
    if normalized_base_url.endswith("/chat/completions"):
        return normalized_base_url
    return f"{normalized_base_url}/chat/completions"


def _build_live_prompt(prompt: str, variant: int) -> str:
    clean_prompt = normalize_prompt(prompt)
    style = STYLE_GUIDES[variant % len(STYLE_GUIDES)]
    return (
        "Create a concise, high-quality answer for the following prompt. "
        "Keep the response clear, useful, and polished. "
        f"Use this framing: {style[0]}. {style[1]}. {style[2]}. "
        f"Prompt: {clean_prompt}"
    )


def generate_live_llm_response(prompt: str, variant: int) -> str:
    settings = get_llm_runtime_settings()
    if not settings.api_key:
        raise RuntimeError("Modo real habilitado, pero falta configurar LLM_API_KEY.")
    if not settings.base_url or not settings.model:
        raise RuntimeError(
            "Modo real habilitado, pero faltan LLM_BASE_URL y/o LLM_MODEL. "
            "Configura un proveedor compatible con OpenAI."
        )

    request_url = _resolve_chat_completions_url(settings.base_url)
    payload = {
        "model": settings.model,
        "messages": [
            {
                "role": "developer",
                "content": "You generate one strong candidate response at a time for a prompt optimizer app.",
            },
            {
                "role": "user",
                "content": _build_live_prompt(prompt, variant),
            },
        ],
        "temperature": 0.7 + ((variant % 4) * 0.1),
        "reasoning_effort": "minimal",
    }
    request_data = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        request_url,
        data=request_data,
        headers={
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=settings.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        error_message = ""
        try:
            error_payload = json.loads(exc.read().decode("utf-8"))
            error_message = str(error_payload.get("error", {}).get("message", "")).strip()
        except Exception:
            error_message = ""

        detail_suffix = f" Detalle: {error_message}" if error_message else ""
        raise RuntimeError(
            f"El proveedor LLM devolvio {exc.code}. "
            f"Revisa la API key, el modelo y la base URL.{detail_suffix}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError("No se pudo conectar al proveedor LLM configurado.") from exc

    choices = data.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    content = str(message.get("content", "")).strip()
    if not content:
        raise RuntimeError("El proveedor LLM no devolvio contenido utilizable.")

    return content


def generate_candidate_response(prompt: str, variant: int) -> str:
    settings = get_llm_runtime_settings()
    if settings.is_live_mode:
        return generate_live_llm_response(prompt, variant)
    return simulate_llm_response(prompt, variant)
