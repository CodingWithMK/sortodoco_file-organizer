from pathlib import Path
from typing import Set
from sortodoco.domain.ignore_rules import IgnoreRules, SkipReason
import fnmatch, os

def is_ignorable(path: Path, rules: IgnoreRules) -> tuple[bool, Set[SkipReason]]:
    
    if not rules.enabled:
        return (False, set())
    
    reasons: set[SkipReason] = set()
    name = path.name
    name_cf = path.name.casefold()

    # Allow wins
    if name_cf in rules.allow_names_cf:
        return (False, reasons)

    # Ignore all directories
    if rules.ignore_dirs and path.is_dir():
        reasons.add(SkipReason.IS_DIR)
        return (True, reasons)

    # Ignore hidden files (dotfiles - Unix/Mac)
    if rules.hidden and name.startswith("."):
        reasons.add(SkipReason.HIDDEN_DOTFILE)
        return (True, reasons)

    # Exact name
    if name_cf in rules.names_cf:
        reasons.add(SkipReason.NAME_EXACT)
        return (True, reasons)

    # Suffix
    if rules.suffixes_cf and name_cf.endswith(rules.suffixes_cf):
        reasons.add(SkipReason.SUFFIX)
        return (True, reasons)

    # Globs
    if rules.globs_cf:

        for pat in rules.globs_cf:
            if fnmatch.fnmatchcase(name_cf, pat):
                reasons.add(SkipReason.GLOB)
                return (True, reasons)

    return (False, reasons)

def _has_hidden_attr(path: Path) -> bool:
    # TODO: Windows: real hidden-attributes (future)
    return path.name.startswith(".")