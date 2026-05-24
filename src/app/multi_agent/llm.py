import json
from dataclasses import dataclass
from typing import Any

import httpx

from src.app.core.config import settings


@dataclass
class GroqReasoner:
    model: str | None = None
    timeout_seconds: float = 15.0

    def __post_init__(self) -> None:
        self.model = self.model or settings.GROQ_MODEL

    def is_configured(self) -> bool:
        return bool(settings.GROQ_API_KEY and self.model)

    def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        fallback: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.is_configured():
            return fallback

        payload = {
            "model": self.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else fallback
        except Exception:
            return fallback
