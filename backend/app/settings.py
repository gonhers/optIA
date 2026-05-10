from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


def _read_env_file() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')

    return values


def get_env_values() -> dict[str, str]:
    values = _read_env_file()
    for key, value in os.environ.items():
        values[key] = value
    return values


def read_setting(name: str, default: str = "") -> str:
    return get_env_values().get(name, default)


def read_int_setting(name: str, default: int) -> int:
    raw_value = read_setting(name, str(default)).strip()
    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class LlmRuntimeSettings:
    mode: str
    api_key: str
    base_url: str
    model: str
    timeout_seconds: int

    @property
    def wants_live_mode(self) -> bool:
        return self.mode == "live"

    @property
    def is_live_ready(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    @property
    def is_live_mode(self) -> bool:
        return self.wants_live_mode and self.is_live_ready


def get_llm_runtime_settings() -> LlmRuntimeSettings:
    mode = read_setting("LLM_MODE", "simulation").strip().lower() or "simulation"
    normalized_mode = "live" if mode == "live" else "simulation"

    return LlmRuntimeSettings(
        mode=normalized_mode,
        api_key=read_setting("LLM_API_KEY").strip(),
        base_url=read_setting("LLM_BASE_URL").strip(),
        model=read_setting("LLM_MODEL").strip(),
        timeout_seconds=max(read_int_setting("LLM_TIMEOUT_SECONDS", 30), 5),
    )
