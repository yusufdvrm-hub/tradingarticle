"""Denetim günlüğü: her aday, öneri, risk kararı ve işlem JSONL olarak yazılır."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Journal:
    def __init__(self, path: Path | None):
        self.path = path
        self.counts: dict[str, int] = {}
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, kind: str, **data: Any) -> None:
        self.counts[kind] = self.counts.get(kind, 0) + 1
        if self.path is None:
            return
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "kind": kind, **data}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")
