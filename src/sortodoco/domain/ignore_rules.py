from enum import Enum, auto
from dataclasses import dataclass, field

class SkipReason(Enum):
    SUFFIX = auto()
    NAME = auto()
    GLOB = auto()
    HIDDEN_ATTR = auto()

@dataclass(frozen=True)
class IgnoreRules:
    suffixes: tuple[str, ...] = field(default_factory=tuple)
    names: tuple[str, ...] = field(default_factory=tuple)
    globs: tuple[str, ...] = field(default_factory=tuple)
    hidden: bool = True # whether hidden attributes should be taken into account