from pathlib import Path
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Iterable, Set
from domain.models import Plan, Operation
from infra.config import load_rules, build_ext_map
from infra.fs import ensure_session_dirs
from utils.filters import is_ignorable

IGNORE_SUFFIXES = (".crdownload", ".part", ".tmp", ".download")
CATEGORY_NAMES = ("Images", "Videos", "Audios", "Documents", "Executables", "Archives", "Fonts", "Code")

# effective = load_ignore_rules(found_path)

# skip, reasons = is_ignorable(path, effective)

def plan_downloads(downloads_dir: Path, rules_path: Path) -> Plan:
    session_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rules = load_rules(rules_path) # {"Images": ["jpg", ...], ...}
    ext_to_cat = build_ext_map(rules) # {"jpg": "Images", ...}

    cats = [cat for cat in CATEGORY_NAMES if cat in rules] + ["_Misc"]

    target_dirs = ensure_session_dirs(
        downloads_dir,
        cats,
        session_ts
    )

    ops: list[Operation] = []
    summary: dict[str, int] = {cat: 0 for cat in target_dirs.keys()}

    for entry in sorted(downloads_dir.iterdir(), key=lambda p: p.name.lower()):
        # Guards
        if entry.is_dir(): # Skip every Directory (even Category-dirs)
            continue
        if not entry.is_file(): # Guardline
            continue

        name_lower = entry.name.lower()
        # Skipping uncomplete Downloads
        if name_lower.endswith(IGNORE_SUFFIXES):
            continue

        ext = entry.suffix.lower().lstrip(".")
        category = ext_to_cat.get(ext, "_Misc")
        dst_dir = target_dirs[category]
        dst_path = dst_dir / entry.name

        ops.append(Operation(kind="move", src=entry, dst=dst_path))
        summary[category] += 1

    return Plan(session_ts=session_ts, ops=ops, summary=summary)