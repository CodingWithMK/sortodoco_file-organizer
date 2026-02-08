from enum import Enum, auto
from dataclasses import dataclass, field

DEFAULT_NAMES = frozenset({
    ".git", "node_modules", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "desktop.ini", "thumbs.db", "ds_store",
    ".idea", ".vscode", "dist", "build", ".next", ".turbo",
})

DEFAULT_SUFFIXES = (".tmp", ".swp", ".log")
DEFAULT_GLOBS = ("*.part", "*.crdownload")


class SkipReason(Enum):
    # Skip reasons for files and directories
    IS_DIR = auto()
    SUFFIX = auto()
    NAME_EXACT = auto()
    GLOB = auto()
    # Hidden attributes for hidden Windows files
    HIDDEN_ATTR = auto()
    # Hidden attributes for hidden Unix files
    HIDDEN_DOTFILE = auto()

@dataclass(frozen=True, slots=True)
class IgnoreRules:
    enabled: bool = True
    ignore_dirs: bool = True
    
    names_cf: frozenset[str] = frozenset()
    allow_names_cf: frozenset[str] = frozenset()
    suffixes_cf: tuple[str, ...] = ()
    globs_cf: tuple[str, ...] = ()
    hidden: bool = True # whether hidden attributes should be taken into account
    

    @classmethod
    def defaults(cls) -> "IgnoreRules":
        return cls(
            hidden=True,
            enabled=True,
            ignore_dirs=True,
            names_cf=DEFAULT_NAMES,
            suffixes_cf=DEFAULT_SUFFIXES,
            globs_cf=DEFAULT_GLOBS,
            allow_names_cf=frozenset()
        )