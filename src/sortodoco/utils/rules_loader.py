# sortodoco/utils/rules_loader.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from sortodoco.domain.ignore_rules import IgnoreRules


def user_ignore_rules_path() -> Path:
    """
    Simple cross-platform baseline for loading user rules
    """
    return Path.home() / ".config" / "sortodoco" / "ignore_rules.json"


def repo_ignore_rules_path() -> Path:
    """
    Works when running from source; consider packaging later
    """
    return Path.cwd() / "rules" / "ignore_rules.json"


def load_ignore_rules(path: Optional[Path] = None) -> IgnoreRules:
    """
    Load ignore rules from JSON, merge with defaults, and NEVER crash.
    """
    base = IgnoreRules.defaults()

    candidates = []
    if path is not None:
        candidates.append(path)
    candidates.append(user_ignore_rules_path())
    candidates.append(repo_ignore_rules_path())

    rules_path = next((p for p in candidates if p.exists()), None)
    if rules_path is None:
        return base

    try:
        raw = json.loads(rules_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return base

    # Merge + normalize
    names = raw.get("names", [])
    suffixes = raw.get("suffixes", [])
    globs = raw.get("globs", [])
    allow_names = raw.get("allow_names", [])

    return IgnoreRules(
        enabled=bool(raw.get("enabled", base.enabled)),
        ignore_dirs=bool(raw.get("ignore_dirs", base.ignore_dirs)),
        hidden=bool(raw.get("hidden", base.hidden)),
        names_cf=base.names_cf | frozenset(n.casefold() for n in names),
        suffixes_cf=base.suffixes_cf if not suffixes else tuple(s.casefold() for s in suffixes),
        globs_cf=base.globs_cf if not globs else tuple(g.casefold() for g in globs),
        allow_names_cf=frozenset(a.casefold() for a in allow_names),
    )
