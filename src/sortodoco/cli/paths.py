from pathlib import Path
from .errors import NotFoundError

def resolve_folder(folder: str | None) -> Path:
    """
    Returns folder path, defaulting to ~/Downloads.
    """
    # TODO: implement
    # - if None -> Path.home()/Downloads
    # - expanduser
    # - exists check
    # - raise NotFoundError with a helpful message
    raise NotImplementedError

def resolve_rules_path(rules: str | None) -> Path:
    """
    Resolve rules/extensions.json from:
    1) explicit CLI option
    2) packaged defaults
    3) cwd fallback
    """
    # TODO: implement deterministic resolution order
    # TODO: if not found -> raise NotFoundError
    raise NotImplementedError
