from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

LanguageCode = Literal["es", "en", "fr", "zh", "pt", "ja", "it"]


@dataclass(frozen=True)
class LanguageOption:
    code: LanguageCode
    label: str
    simulated_prefix: str


LANGUAGE_OPTIONS: tuple[LanguageOption, ...] = (
    LanguageOption(code="es", label="Spanish", simulated_prefix="[Translated to Spanish]"),
    LanguageOption(code="en", label="English", simulated_prefix="[Translated to English]"),
    LanguageOption(code="fr", label="French", simulated_prefix="[Translated to French]"),
    LanguageOption(code="zh", label="Chinese", simulated_prefix="[Translated to Chinese]"),
    LanguageOption(code="pt", label="Portuguese", simulated_prefix="[Translated to Portuguese]"),
    LanguageOption(code="ja", label="Japanese", simulated_prefix="[Translated to Japanese]"),
    LanguageOption(code="it", label="Italian", simulated_prefix="[Translated to Italian]"),
)

LANGUAGE_MAP: dict[LanguageCode, LanguageOption] = {
    language.code: language
    for language in LANGUAGE_OPTIONS
}
SUPPORTED_LANGUAGE_CODES: tuple[LanguageCode, ...] = tuple(
    language.code for language in LANGUAGE_OPTIONS
)
SUPPORTED_LANGUAGE_CODES_TEXT = ", ".join(SUPPORTED_LANGUAGE_CODES)


def normalize_target_language(value: object) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("target_language debe ser un codigo de idioma en texto.")

    normalized_value = value.strip().lower()
    return normalized_value or None


def validate_target_language(value: object) -> LanguageCode | None:
    normalized_value = normalize_target_language(value)
    if normalized_value is None:
        return None

    if normalized_value not in LANGUAGE_MAP:
        raise ValueError(
            f"target_language '{normalized_value}' no es valido. "
            f"Codigos soportados: {SUPPORTED_LANGUAGE_CODES_TEXT}."
        )

    return cast(LanguageCode, normalized_value)


def get_language_option(language_code: LanguageCode) -> LanguageOption:
    return LANGUAGE_MAP[language_code]


def get_language_label(language_code: LanguageCode) -> str:
    return get_language_option(language_code).label


def translate_text(text: str, target_language: LanguageCode | None) -> str:
    if not target_language:
        return text

    language_option = get_language_option(target_language)
    return f"{language_option.simulated_prefix} {text}"
