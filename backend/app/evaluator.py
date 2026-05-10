from __future__ import annotations

import hashlib
import re

from .llm import extract_focus_terms


def _stable_noise(prompt: str, candidate: str) -> float:
    digest = hashlib.sha256(f"{prompt}:{candidate}".encode("utf-8")).hexdigest()
    return (int(digest[:4], 16) % 8) / 10


def score_candidate(prompt: str, candidate: str) -> float:
    prompt_terms = set(extract_focus_terms(prompt, limit=8))
    candidate_words = set(re.findall(r"[A-Za-z0-9']+", candidate.lower()))

    overlap_ratio = len(prompt_terms & candidate_words) / max(1, len(prompt_terms))
    word_count = len(candidate.split())
    length_score = min(word_count / 42, 1.0)
    action_bonus = 0.4 if "next step" in candidate.lower() or "outcome" in candidate.lower() else 0.0

    raw_score = 4.6 + (overlap_ratio * 2.3) + (length_score * 1.0) + action_bonus + _stable_noise(prompt, candidate)
    bounded_score = min(max(raw_score, 6.0), 9.4)
    return round(bounded_score, 1)
