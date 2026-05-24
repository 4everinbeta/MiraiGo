from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


class StateValidationError(ValueError):
    pass


class TravelStateValidator:
    def __init__(self, schema_path: str | Path):
        self.schema_path = Path(schema_path)
        with self.schema_path.open("r", encoding="utf-8") as handle:
            self.schema = json.load(handle)
        self.validator = Draft202012Validator(self.schema)

    def validate(self, state: dict[str, Any]) -> None:
        errors = sorted(self.validator.iter_errors(state), key=lambda err: list(err.path))
        if not errors:
            return
        rendered = "; ".join(self._render_error(error) for error in errors)
        raise StateValidationError(rendered)

    @staticmethod
    def _render_error(error: ValidationError) -> str:
        path = ".".join(str(part) for part in error.path) or "<root>"
        return f"{path}: {error.message}"

