from pathlib import Path
from typing import Iterable

def ensure_session_dirs(downloads_dir: Path,
                        categories: Iterable[str],
                        session_ts: str) -> dict[str, Path]:
    """
    Returns mapping {category: session_dir} and ensures they exist.
    Also ensures _Misc/session_ts exists.
    """
    mapping: dict[str, Path] = {}
    
    for category in categories:
        session_dir: Path = downloads_dir / category / session_ts
        session_dir.mkdir(parents=True, exist_ok=True)
        mapping[category] = session_dir
    
    if "_Misc" not in mapping:
        misc_dir = downloads_dir / "_Misc" / session_ts
        misc_dir.mkdir(parents=True, exist_ok=True)
        mapping["_Misc"] = misc_dir

    return mapping