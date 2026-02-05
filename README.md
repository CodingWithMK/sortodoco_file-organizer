# SortoDoco — Local-First File Organizer (v0.1.0)

**Keep your desktop and user folders tidy — locally and privately.**

IMPORTANT: **GUI under development — not available for end users.** Only the CLI `plan` command (preview mode) is supported at this time. See Safety & Limitations below.

---

## Table of contents

- Project overview
- Installation
- Quick start (CLI)
- CLI usage (detailed)
- Safety & limitations
- Development & contributing
- Roadmap & next steps
- License & contact

---

## Project overview

SortoDoco scans common user folders (Desktop, Downloads, Documents, Pictures, Music, Videos) and generates an ordered plan to organize files into categorized folders based on extension maps and user-provided rules. It is a local-first, offline tool focused on privacy and repeatable file organization workflows.

Current availability
- Version: `v0.1.0`
- Status: ALPHA — the CLI `plan` command (preview only) is available. The GUI is a work in progress and is currently not functional for end users.

Key concepts
- Planner: scans folders and builds a preview plan (no changes applied).
- Executor: (internal) component that would apply moves — not exposed for safe automatic use yet.
- Rules: JSON or YAML-driven rules that map extensions and patterns to target categories. Default mappings live in `rules/extensions.json`.

---

## Installation

Prerequisites
- Python 3.10+ (3.11 recommended)
- Git (to clone repository, optional)

Recommended (editable install)

```bash
# Clone repository
git clone https://github.com/CodingWithMK/sortodoco_file-organizer.git
cd sortodoco_file-organizer

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate    # Windows (PowerShell: .\.venv\Scripts\Activate.ps1)

# Install in editable mode
python -m pip install --upgrade pip
pip install -e .
```

Notes
- The project may include optional GUI dependencies (CustomTkinter, Pillow). If you only need CLI functionality, installing the package as above is sufficient in most environments. If the package declares extras, use `pip install -e .[gui]` to include GUI dependencies.
- If your packaging uses `pyproject.toml`, you can also use `pip install -e .` directly from the project root.

Platform-specific state locations (where the app stores small GUI state files)
- macOS: `~/Library/Application Support/sortodoco/gui_state.json`
- Linux: `~/.config/sortodoco/gui_state.json` or `$XDG_CONFIG_HOME/sortodoco/gui_state.json`
- Windows: `%APPDATA%\sortodoco\gui_state.json`

---

## Quick start (CLI)

After installation the `sortodoco` console script should be available. If you installed with `pip install -e .`, run:

```bash
# Show available commands
sortodoco --help

# Generate a preview plan for your Downloads folder
sortodoco plan ~/Downloads
```

Example output (preview summary)

```text
Plan summary (preview):
------------------------
Scanned: 125 files
Moves suggested: 78
Top target folders:
- Documents/Archives: 24
- Downloads/Images: 18
- Downloads/Executables: 12

Detailed plan saved to: /tmp/sortodoco_plan_2026-02-05.json
```

---

## CLI usage (detailed)

Commands
- `sortodoco plan [FOLDER] [--rules FILE]` — Scan `FOLDER` and generate a preview plan. If `FOLDER` is omitted, a default set of user folders may be scanned depending on configuration.
- `sortodoco gui` — Launch the GUI. NOTE: GUI is under development and may not run for end users.
- `sortodoco version` — Print the installed SortoDoco version.

Common options for `plan`
- `--rules, -r FILE` — Use a custom rules file (JSON or YAML). If omitted the package default `rules/extensions.json` is used.
- `--output, -o FILE` — Write the plan JSON to `FILE` (default: temporary file)
- `--dry-run` — Explicitly request preview-only behavior (the planner is preview-only by default)

Examples

- Basic preview of Downloads

```bash
sortodoco plan ~/Downloads
```

- Use a custom rules file

```bash
sortodoco plan ~/Downloads --rules ./my_rules.json
```

- Run help for a command

```bash
sortodoco plan --help
```

Interpreting the plan
- The planner produces a JSON plan with per-file operations and a human-friendly summary. Review the summary carefully before applying any manual changes. At present SortoDoco does not offer an automatic, safe "apply" command for end users — the planner is intended to help you review organization suggestions.

Exit codes & errors
- 0 — success (preview generated)
- non-zero — error (invalid path, unreadable rules file, or other runtime error). Error messages are printed to stderr.

---

## Safety & limitations

IMPORTANT SAFETY NOTES

**No undo / rollback implemented.** Applying any file operations without an undo mechanism may cause irreversible changes. The current CLI primarily generates previews and summaries — prefer manual review.

**Path validation & protected paths are minimal.** System folders, mounted volumes, or important app data may not be protected by the current implementation. Do not run any apply/automatic moves until safeguards are implemented.

**Ignore rules are partial / draft.** Some ignore patterns and rules are placeholders; test rules on non-critical folders first.

Recommendations
- Always run `sortodoco plan` and inspect the produced JSON/summary before doing anything that moves files.
- Back up important data before experimenting.
- Use smaller test folders (copies) to validate custom rules.

---

## Development & contributing

Getting the code for development

```bash
git clone https://github.com/CodingWithMK/sortodoco_file-organizer.git
cd sortodoco_file-organizer
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run tests (if present)

```bash
# If the repo provides tests; run
pytest
```

Developer notes
- Main CLI entry point: `src/sortodoco/cli/main.py` (console script `sortodoco`).
- Planner implementation: `src/sortodoco/services/planner.py` — generates `Plan` objects with `.ops` and `.summary`.
- Default rules: `rules/extensions.json`.
- GUI code lives under `src/sortodoco/ui/` — it is under active development and not ready for end users.

Contributing
- Open issues for bugs or feature requests.
- Fork, branch, and open pull requests. Use descriptive commit messages and include tests where possible.

More technical analysis
- See `SORTODOCO_NEW_FEATURES_ANALYSIS.md` in the repository root for architecture notes, diagrams, and recommended next steps.

---

## Roadmap & next steps

Short-term priorities
1. Add a safe, audited `apply` flow with explicit confirmations and a reversible/transactional undo mechanism.
2. Implement robust path validation and a built-in list of protected system locations.
3. Harden ignore rules and provide examples for common workflows.
4. Add automated tests for planner and executor components.

Longer-term
- Complete GUI and provide separate install extras for GUI dependencies.
- Add optional local ML models for image classification (opt-in).

---

## License

MIT

---

## Contact

Project: https://github.com/CodingWithMK/sortodoco_file-organizer
Issues: open an issue on the repository
