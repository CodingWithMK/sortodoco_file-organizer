from pathlib import Path
import json
from sortodoco.domain.ignore_rules import IgnoreRules

BUILTIN_IGNORE = IgnoreRules(
    suffixes=(".crdownload", ".part", ".tmp", ".download"),
    names=("desktop.ini", ".ds_store", "thumbs.db"),
    globs=("~$*", ".~lock.*#"),
    hidden=True,
)


def load_ignore_rules(config_path: Path | None) -> IgnoreRules:
    """Load ignore rules from a JSON config file and merge with built-in rules.

    Args:
        config_path: Path to a JSON file containing user ignore rules.
                    If None, only built-in rules are returned.

    Returns:
        Merged IgnoreRules combining built-in and user rules.
    """
    if config_path is None or not config_path.exists():
        return _normalize_rules(BUILTIN_IGNORE)

    try:
        with open(config_path, "r") as f:
            data = json.load(f)

        user = IgnoreRules(
            suffixes=tuple(data.get("suffixes", [])),
            names=tuple(data.get("names", [])),
            globs=tuple(data.get("globs", [])),
            hidden=data.get("hidden", True),
        )

        # Merge user rules with built-in rules
        merged = IgnoreRules(
            suffixes=BUILTIN_IGNORE.suffixes + user.suffixes,
            names=BUILTIN_IGNORE.names + user.names,
            globs=BUILTIN_IGNORE.globs + user.globs,
            hidden=BUILTIN_IGNORE.hidden and user.hidden,
        )

        return _normalize_rules(merged)
    except (json.JSONDecodeError, KeyError, TypeError):
        # If config is invalid, fall back to built-in rules
        return _normalize_rules(BUILTIN_IGNORE)


def _normalize_rules(r: IgnoreRules) -> IgnoreRules:
    """Normalize ignore rules by lowercasing and deduplicating entries.

    Args:
        r: The IgnoreRules to normalize.

    Returns:
        A new IgnoreRules with normalized values.
    """
    # Lowercase and deduplicate suffixes (ensure they start with .)
    normalized_suffixes = tuple(
        sorted(
            set(s.lower() if s.startswith(".") else f".{s.lower()}" for s in r.suffixes)
        )
    )

    # Lowercase and deduplicate names
    normalized_names = tuple(sorted(set(n.lower() for n in r.names)))

    # Deduplicate globs (keep case for pattern matching)
    normalized_globs = tuple(sorted(set(r.globs)))

    return IgnoreRules(
        suffixes=normalized_suffixes,
        names=normalized_names,
        globs=normalized_globs,
        hidden=r.hidden,
    )


def load_rules(json_path: Path) -> dict[str, list[str]]:
    with open(json_path, "r") as file:
        extensions = json.load(file)

    cleaned_extensions: dict[str, list[str]] = {}
    for category, ext_list in extensions.items():
        cleaned_extensions[category] = [
            ext.lower().removeprefix(".") for ext in ext_list
        ]

    return cleaned_extensions


def build_ext_map(rules: dict[str, list[str]]) -> dict[str, str]:
    ext_map: dict[str, str] = {}

    for category, ext_list in rules.items():
        for ext in ext_list:
            if ext in ext_map and ext_map[ext] != category:
                raise ValueError(
                    f"Extension '{ext}' already mapped to '{ext_map[ext]}', also found in '{category}'."
                )
            ext_map[ext] = category

    return ext_map
