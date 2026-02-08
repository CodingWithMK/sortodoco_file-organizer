from pathlib import Path
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Iterable, Set
from sortodoco.domain.models import Plan, Operation
from sortodoco.infra.config import load_rules, build_ext_map
from sortodoco.infra.fs import ensure_session_dirs
from sortodoco.utils.filters import is_ignorable
from sortodoco.utils.rules_loader import load_ignore_rules

CATEGORY_NAMES = ("Images", "Videos", "Audios", "Documents", "Executables", "Archives", "Fonts", "Code")

# Plan the downloads directory organization with ignore rules
def plan_downloads(downloads_dir: Path, rules_path: Path) -> Plan:
    session_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rules = load_rules(rules_path) # {"Images": ["jpg", ...], ...}
    ignore_rules = load_ignore_rules()
    ext_to_cat = build_ext_map(rules) # {"jpg": "Images", ...}

    cats = [cat for cat in CATEGORY_NAMES if cat in rules] + ["_Misc"]

    target_dirs = ensure_session_dirs(
        downloads_dir,
        cats,
        session_ts
    )

    ops: list[Operation] = []
    summary: dict[str, int] = {cat: 0 for cat in target_dirs.keys()}

    # Build candidates ONCE (top-level)
    candidates: list[Path] = []
    for entry in downloads_dir.iterdir():
        skip, _ = is_ignorable(entry, ignore_rules)
        if not skip:
            candidates.append(entry)

    for entry in sorted(candidates, key=lambda p: p.name.casefold()):
        # Guards
        if not entry.is_file(): # Guardline
            continue

        ext = entry.suffix.lower().lstrip(".")
        category = ext_to_cat.get(ext, "_Misc")
        dst_dir = target_dirs[category]
        dst_path = dst_dir / entry.name

        ops.append(Operation(kind="move", src=entry, dst=dst_path))
        summary[category] += 1

    return Plan(session_ts=session_ts, ops=ops, summary=summary)