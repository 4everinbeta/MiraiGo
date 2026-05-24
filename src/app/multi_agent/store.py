import json
from dataclasses import dataclass, field
from typing import Any

from src.app.db.redis import get_redis_client


@dataclass
class ConversationStateStore:
    key_prefix: str = "multi-agent:session"
    ttl_seconds: int = 86400
    _memory: dict[str, dict[str, Any]] = field(default_factory=dict)

    def _key(self, session_id: str) -> str:
        return f"{self.key_prefix}:{session_id}"

    def load(self, session_id: str) -> dict[str, Any] | None:
        key = self._key(session_id)
        redis_client = get_redis_client()
        if redis_client:
            try:
                raw = redis_client.get(key)
                if raw:
                    return json.loads(raw)
            except Exception:
                pass
        return self._memory.get(session_id)

    def save(self, session_id: str, state: dict[str, Any]) -> None:
        key = self._key(session_id)
        redis_client = get_redis_client()
        if redis_client:
            try:
                redis_client.setex(key, self.ttl_seconds, json.dumps(state))
                return
            except Exception:
                pass
        self._memory[session_id] = state
