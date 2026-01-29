from dataclasses import dataclass
from pathlib import Path
from typing import Literal

OpKind = Literal["move"] # TODO: Add "trash" later

@dataclass(frozen=True)
class Operation:
    kind: OpKind
    src: Path
    dst: Path

@dataclass
class Plan:
    session_ts: str
    ops: list[Operation]
    summary: dict[str, int] # e.g. {"Documents": 12, "_Misc": 3}