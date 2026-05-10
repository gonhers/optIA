from __future__ import annotations

from .evaluator import score_candidate
from .generator import DEFAULT_CANDIDATE_COUNT, generate_candidates
from .schemas import CandidateResponse, OptimizeResponse
from .translator import LanguageCode, translate_text


def optimize_prompt(
    prompt: str,
    target_language: LanguageCode | None = None,
    candidate_count: int = DEFAULT_CANDIDATE_COUNT,
) -> OptimizeResponse:
    scored_candidates = [
        CandidateResponse(text=text, score=score_candidate(prompt, text))
        for text in generate_candidates(prompt, count=candidate_count)
    ]
    ranked_candidates = sorted(scored_candidates, key=lambda candidate: candidate.score, reverse=True)
    best_response = translate_text(ranked_candidates[0].text, target_language)

    return OptimizeResponse(best_response=best_response, candidates=ranked_candidates)
