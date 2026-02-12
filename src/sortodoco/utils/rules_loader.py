from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from enum import Enum, auto
import platformdirs
import importlib.resources
from datetime import datetime

from sortodoco.domain.ignore_rules import IgnoreRules

class RulesLoadStatus(Enum):
    OK = auto()
    SEEDED = auto()
    RESET_INVALID_JSON = auto()
    FALLBACK_DEFAULTS = auto()

def get_user_rules_path() -> Path:
    """
    Returns OS-correct config file path for ignore_rules.json.
    """
    user_rules_path = platformdirs.user_config_dir("sortodoco")
    return Path(user_rules_path) / "ignore_rules.json"

def ensure_user_rules_exist() -> RulesLoadStatus:
    """
    Ensures user ignore_rules.json exists.
    If missing: create dir + write default JSON.
    """
    path = get_user_rules_path()
    
    try:
        if path.exists():
            return RulesLoadStatus.OK
        else:
            text = read_builtin_defaults_text()
            if not text:
                return RulesLoadStatus.FALLBACK_DEFAULTS
                
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            return RulesLoadStatus.SEEDED
    except OSError:
        return RulesLoadStatus.FALLBACK_DEFAULTS

def read_builtin_defaults_text() -> str:
    """
    Read ignore_rules.json shipped inside the installed package and return its text.
    """
    try:
        defaults = importlib.resources.files("sortodoco.rules") / "ignore_rules.json"
        with defaults.open("r", encoding="utf-8") as file:
            return file.read()
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        return ""

def parse_ignore_rules_json(raw: dict) -> IgnoreRules:
    """
    Parse ignore_rules.json text and return IgnoreRules.
    """
    names = raw.get("names") or []
    suffixes = raw.get("suffixes") or []
    globs = raw.get("globs") or []
    allow_names = raw.get("allow_names") or []

    return IgnoreRules(
        enabled=bool(raw.get("enabled", True)),
        ignore_dirs=bool(raw.get("ignore_dirs", True)),
        hidden=bool(raw.get("hidden", True)),
        names_cf=frozenset(str(n).casefold() for n in names),
        suffixes_cf=tuple(str(s).casefold() for s in suffixes),
        globs_cf=tuple(str(g).casefold() for g in globs),
        allow_names_cf=frozenset(str(a).casefold() for a in allow_names),
    )

def load_ignore_rules(path: Optional[Path] = None) -> IgnoreRules:
    """
    Load ignore rules from JSON, merge with defaults.
    Priority: 
        1. Explicit path (if provided)
        2. User config (ensure exists)
        3. Built-in defaults
    """
    builtin_text = read_builtin_defaults_text()
    
    if not builtin_text:
        base = IgnoreRules.defaults()
    else:
        base = parse_ignore_rules_json(json.loads(builtin_text))

    if path is None:
        ensure_user_rules_exist()

    rules_path = path or get_user_rules_path()

    if not rules_path.exists():
        return base

    try:
        raw = json.loads(rules_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        try:
            rules_path_stem = rules_path.stem
            rules_path_suffix = rules_path.suffix
            ts = datetime.now().strftime("_%Y%m%d_%H%M%S")
            backup_path = rules_path.with_name(f"{rules_path_stem + ts + rules_path_suffix + '.bak'}")
            rules_path.rename(backup_path)
            rules_path.write_text(read_builtin_defaults_text(), encoding="utf-8")
        except OSError:
            pass
        return base

    # Merge + normalize
    names = raw.get("names") or []
    suffixes = raw.get("suffixes") or []
    globs = raw.get("globs") or []
    allow_names = raw.get("allow_names") or []

    return IgnoreRules(
        enabled=bool(raw.get("enabled", base.enabled)),
        ignore_dirs=bool(raw.get("ignore_dirs", base.ignore_dirs)),
        hidden=bool(raw.get("hidden", base.hidden)),
        names_cf=base.names_cf | frozenset(str(n).casefold() for n in names),
        suffixes_cf=base.suffixes_cf if not suffixes else tuple(str(s).casefold() for s in suffixes),
        globs_cf=base.globs_cf if not globs else tuple(str(g).casefold() for g in globs),
        allow_names_cf=frozenset(str(a).casefold() for a in allow_names),
    )
