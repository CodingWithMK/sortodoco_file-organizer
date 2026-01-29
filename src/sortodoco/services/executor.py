from pathlib import Path
import shutil
import os
from domain.models import Plan, Operation

def unique_target(dst: Path) -> Path:
    """
    Rename-with-suffix. If destiation exists, try renaming with 
    "name (1).txt, name (2).txt, ..."
    Stops when a non-existing path found.
    """
    if not dst.exists():
        return dst
    
    parent = dst.parent
    stem = dst.stem
    suffix = dst.suffix

    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"

        if not candidate.exists():
            return candidate
        
        i += 1


def apply_plan(plan: Plan) -> dict:
    """
    Performs all Ops and and reports every action:
    {"moved": N, "skipped": M, errors: [(src, reason), ...]}
    """

    report = {"moved": 0, "skipped": 0, "errors": []}
    for op in plan.ops:
        if op.kind != "move":
            report["skipped"] += 1
            continue

        try:
            target = unique_target(op.dst)
            target.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(op.src), str(target))
            report["moved"] += 1
        except PermissionError as e:
            report["errors"].append((str(op.src), f"permission: {e}"))
        except FileNotFoundError as e:
            report["errors"].append((str(op.src), f"notfound: {e}"))
        except Exception as e:
            report["errors"].append((str(op.src), f"error: {e}"))

        # TODO: report for conflicts (useful for GUI-feedback)
        
    return report