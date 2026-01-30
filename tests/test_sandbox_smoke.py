from pathlib import Path
from sortodoco.services.planner import plan_downloads

def test_plan_downloads_creates_ops(tmp_path: Path):
    rules = Path("rules/extensions.json")
    # Dummy files
    for name in ["pic.JPG", "readme.PDF", "clip.mp4", "data.csv"]:
        (tmp_path / name).write_bytes(b"dummy")

    plan = plan_downloads(tmp_path, rules)

    # Assertions (minimal, but valid)
    assert plan is not None
    assert len(plan.ops) > 0
