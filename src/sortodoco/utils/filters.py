from pathlib import Path
from typing import Set
from domain.ignore_rules import IgnoreRules, SkipReason
import fnmatch, os

def is_ignorable(path: Path, rules: IgnoreRules) -> tuple[bool, Set[SkipReason]]:
    reasons: set[SkipReason] = set()
    name_cf = path.name.casefold()

    # TODO: NAME exact
    # TODO: SUFFIX on complete name (endswith(tuple))
    # TODO: GLOB (fnmatch.fnmatchcase(name_cf, pat))
    # TODO: HIDDEN_ATTR (if rules.hidden then True)

    return (len(reasons) > 0, reasons)

def _has_hidden_attr(path: Path) -> bool:
    # TODO: Unix: leading point
    # TODO: Windows: real hidden-attributes (future)
    pass