from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.app.multi_agent.orchestrator import Orchestrator
from src.app.multi_agent.state import new_state


def default_schema_path() -> Path:
    return Path(__file__).resolve().parents[3] / "state" / "travel-state.schema.json"


def _load_state(state_file: Path | None) -> dict[str, Any]:
    if state_file is None or not state_file.exists():
        return new_state()
    with state_file.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError("State file must contain a JSON object.")
    return raw


def _save_state(state_file: Path | None, state: dict[str, Any]) -> None:
    if state_file is None:
        return
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with state_file.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)


def run_turn(
    orchestrator: Orchestrator, state: dict[str, Any], user_message: str
) -> tuple[dict[str, Any], str]:
    result = orchestrator.run(state, user_message)
    return result.state, result.output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Interactive CLI demo for the multi-agent travel orchestrator."
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=default_schema_path(),
        help="Path to travel-state JSON schema.",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help="Optional JSON file for persisting state between CLI runs.",
    )
    args = parser.parse_args()

    orchestrator = Orchestrator(args.schema)
    state = _load_state(args.state_file)

    print("Multi-agent travel demo. Type messages and press Enter. Type 'exit' to quit.")
    while True:
        try:
            user_message = input("you> ").strip()
        except EOFError:
            print()
            break

        if not user_message:
            continue
        if user_message.lower() in {"exit", "quit"}:
            break

        state, markdown_output = run_turn(orchestrator, state, user_message)
        _save_state(args.state_file, state)

        print("\nassistant:\n")
        print(markdown_output)
        print()

    _save_state(args.state_file, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

