import json
from pathlib import Path

import pytest

# Import your module under test
import sortodoco.utils.rules_loader as rl


def _builtin_json(names=None, suffixes=None, globs=None, allow_names=None, enabled=True, ignore_dirs=True, hidden=True):
    """Helper: returns a valid builtin ignore_rules.json as text."""
    payload = {
        "enabled": enabled,
        "ignore_dirs": ignore_dirs,
        "hidden": hidden,
        "allow_names": allow_names or [],
        "names": names or [],
        "suffixes": suffixes or [],
        "globs": globs or [],
    }
    return json.dumps(payload, indent=2)


def test_missing_user_file_seeds_and_loads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Arrange: make platformdirs point to tmp_path
    monkeypatch.setattr(rl.platformdirs, "user_config_dir", lambda *_args, **_kwargs: str(tmp_path))

    # Arrange: builtin defaults exist (package resource emulation)
    monkeypatch.setattr(rl, "read_builtin_defaults_text", lambda: _builtin_json(names=[".git"]))

    user_path = rl.get_user_rules_path()
    assert not user_path.exists()

    # Act: ensure seeds
    status = rl.ensure_user_rules_exist()

    # Assert
    assert status == rl.RulesLoadStatus.SEEDED
    assert user_path.exists()

    # Act: load rules should work
    rules = rl.load_ignore_rules()

    # Assert: contains builtin name
    assert ".git".casefold() in rules.names_cf


def test_invalid_json_creates_backup_and_resets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(rl.platformdirs, "user_config_dir", lambda *_args, **_kwargs: str(tmp_path))
    monkeypatch.setattr(rl, "read_builtin_defaults_text", lambda: _builtin_json(names=[".git"]))

    user_path = rl.get_user_rules_path()
    user_path.parent.mkdir(parents=True, exist_ok=True)
    user_path.write_text("{bad json", encoding="utf-8")  # invalid

    # Act
    rules = rl.load_ignore_rules()

    # Assert: loader returns base/default rules (at least builtin)
    assert ".git".casefold() in rules.names_cf

    # Assert: backup exists (timestamped name + .bak suffix)
    # TODO: implement a robust check: find any file in tmp_path with name starting with "ignore_rules"
    # and ending with ".bak"
    backups = list(tmp_path.glob("ignore_rules*.bak"))
    assert backups, "Expected a .bak backup file to be created"

    # Assert: user_path now contains valid JSON (reset)
    text = user_path.read_text(encoding="utf-8")
    json.loads(text)  # should not raise


def test_valid_json_extends_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(rl.platformdirs, "user_config_dir", lambda *_args, **_kwargs: str(tmp_path))

    # Builtin has ".git"
    monkeypatch.setattr(rl, "read_builtin_defaults_text", lambda: _builtin_json(names=[".git"]))

    # Seed user file with "node_modules"
    user_path = rl.get_user_rules_path()
    user_path.parent.mkdir(parents=True, exist_ok=True)
    user_path.write_text(_builtin_json(names=["node_modules"]), encoding="utf-8")

    # Act
    rules = rl.load_ignore_rules()

    # Assert: union/extend behavior
    assert ".git".casefold() in rules.names_cf
    assert "node_modules".casefold() in rules.names_cf
