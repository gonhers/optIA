from __future__ import annotations

from .llm import generate_candidate_response

DEFAULT_CANDIDATE_COUNT = 3
MIN_CANDIDATE_COUNT = 1
MAX_CANDIDATE_COUNT = 10


def normalize_candidate_count(value: object) -> int:
    if value is None or value == "":
        return DEFAULT_CANDIDATE_COUNT

    if isinstance(value, bool):
        raise ValueError("candidate_count debe ser un numero entero.")

    if isinstance(value, int):
        candidate_count = value
    elif isinstance(value, str):
        normalized_value = value.strip()
        if not normalized_value:
            return DEFAULT_CANDIDATE_COUNT
        if not normalized_value.isdigit():
            raise ValueError("candidate_count debe ser un numero entero.")
        candidate_count = int(normalized_value)
    else:
        raise ValueError("candidate_count debe ser un numero entero.")

    if not MIN_CANDIDATE_COUNT <= candidate_count <= MAX_CANDIDATE_COUNT:
        raise ValueError(
            f"candidate_count debe estar entre {MIN_CANDIDATE_COUNT} y {MAX_CANDIDATE_COUNT}."
        )

    return candidate_count

def generate_candidates(prompt: str, count: int = DEFAULT_CANDIDATE_COUNT) -> list[str]:
    return [generate_candidate_response(prompt, variant=index) for index in range(count)]
