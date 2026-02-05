"""
Application state management for SortoDoco GUI.
Provides centralized state with observer pattern for UI updates.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Any, Literal
from datetime import datetime
import json
import os

from sortodoco.domain.models import Plan, Operation


def get_config_dir() -> Path:
    """Get the application configuration directory."""
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():  # macOS
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    else:
        base = Path.home()

    config_dir = base / "sortodoco"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_state_file() -> Path:
    """Get the path to the state persistence file."""
    return get_config_dir() / "gui_state.json"


@dataclass
class ScanOptions:
    """Options for scanning and planning."""

    create_session_subfolders: bool = True
    use_timestamps: bool = True
    session_prefix: str = "session"
    collision_strategy: Literal["rename", "skip", "overwrite"] = "rename"
    risk_threshold: Literal["low", "medium", "high"] = "medium"
    quarantine_deletes: bool = True


@dataclass
class OperationFilter:
    """Filter settings for operations table."""

    search_text: str = ""
    category: str | None = None
    risk: str | None = None
    show_selected_only: bool = False


@dataclass
class SessionSummary:
    """Summary of a past session."""

    session_id: str
    timestamp: datetime
    root_folders: list[Path]
    total_ops: int
    moved: int
    skipped: int
    errors: int

    @property
    def success_rate(self) -> float:
        if self.total_ops == 0:
            return 100.0
        return (self.moved / self.total_ops) * 100


@dataclass
class RootFolder:
    """A root folder to scan."""

    path: Path
    enabled: bool = True
    last_scanned: datetime | None = None


class AppState:
    """
    Centralized application state with observer pattern.

    Usage:
        state = AppState()
        state.subscribe("current_view", lambda v: print(f"View changed to {v}"))
        state.current_view = "dashboard"  # Triggers callback
    """

    def __init__(self):
        # Private state storage
        self._theme_mode: Literal["light", "dark", "system"] = "system"
        self._current_view: str = "dashboard"
        self._root_folders: list[RootFolder] = []
        self._scan_options: ScanOptions = ScanOptions()
        self._current_plan: Plan | None = None
        self._selected_operations: set[int] = set()
        self._operation_filter: OperationFilter = OperationFilter()
        self._sessions: list[SessionSummary] = []
        self._user_rules: dict[str, list[str]] = {}
        self._user_ignore_patterns: list[str] = []
        self._is_scanning: bool = False
        self._is_applying: bool = False
        self._last_error: str | None = None

        # Observer storage
        self._observers: dict[str, list[Callable[[Any], None]]] = {}

    # ========== Observer Pattern ==========

    def subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        """Subscribe to state changes for a specific key."""
        if key not in self._observers:
            self._observers[key] = []
        self._observers[key].append(callback)

    def unsubscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        """Unsubscribe from state changes."""
        if key in self._observers and callback in self._observers[key]:
            self._observers[key].remove(callback)

    def _notify(self, key: str, value: Any) -> None:
        """Notify all observers of a state change."""
        for callback in self._observers.get(key, []):
            try:
                callback(value)
            except Exception as e:
                print(f"Error in state observer for '{key}': {e}")

    # ========== Theme Mode ==========

    @property
    def theme_mode(self) -> Literal["light", "dark", "system"]:
        return self._theme_mode

    @theme_mode.setter
    def theme_mode(self, value: Literal["light", "dark", "system"]) -> None:
        if value != self._theme_mode:
            self._theme_mode = value
            self._notify("theme_mode", value)

    # ========== Navigation ==========

    @property
    def current_view(self) -> str:
        return self._current_view

    @current_view.setter
    def current_view(self, value: str) -> None:
        if value != self._current_view:
            self._current_view = value
            self._notify("current_view", value)

    def navigate_to(self, view: str) -> None:
        """Navigate to a specific view."""
        self.current_view = view

    # ========== Root Folders ==========

    @property
    def root_folders(self) -> list[RootFolder]:
        return self._root_folders.copy()

    def add_root_folder(self, path: Path) -> None:
        """Add a new root folder."""
        if not any(rf.path == path for rf in self._root_folders):
            self._root_folders.append(RootFolder(path=path))
            self._notify("root_folders", self._root_folders)

    def remove_root_folder(self, path: Path) -> None:
        """Remove a root folder."""
        self._root_folders = [rf for rf in self._root_folders if rf.path != path]
        self._notify("root_folders", self._root_folders)

    def toggle_root_folder(self, path: Path) -> None:
        """Toggle a root folder's enabled state."""
        for rf in self._root_folders:
            if rf.path == path:
                rf.enabled = not rf.enabled
                break
        self._notify("root_folders", self._root_folders)

    def get_enabled_root_folders(self) -> list[Path]:
        """Get list of enabled root folder paths."""
        return [rf.path for rf in self._root_folders if rf.enabled]

    # ========== Scan Options ==========

    @property
    def scan_options(self) -> ScanOptions:
        return self._scan_options

    @scan_options.setter
    def scan_options(self, value: ScanOptions) -> None:
        self._scan_options = value
        self._notify("scan_options", value)

    def update_scan_option(self, key: str, value: Any) -> None:
        """Update a single scan option."""
        if hasattr(self._scan_options, key):
            setattr(self._scan_options, key, value)
            self._notify("scan_options", self._scan_options)

    # ========== Current Plan ==========

    @property
    def current_plan(self) -> Plan | None:
        return self._current_plan

    @current_plan.setter
    def current_plan(self, value: Plan | None) -> None:
        self._current_plan = value
        self._selected_operations = set()  # Reset selection
        if value:
            # Select all operations by default
            self._selected_operations = set(range(len(value.ops)))
        self._notify("current_plan", value)

    # ========== Operation Selection ==========

    @property
    def selected_operations(self) -> set[int]:
        return self._selected_operations.copy()

    def select_operation(self, index: int) -> None:
        """Select an operation by index."""
        self._selected_operations.add(index)
        self._notify("selected_operations", self._selected_operations)

    def deselect_operation(self, index: int) -> None:
        """Deselect an operation by index."""
        self._selected_operations.discard(index)
        self._notify("selected_operations", self._selected_operations)

    def toggle_operation(self, index: int) -> None:
        """Toggle operation selection."""
        if index in self._selected_operations:
            self._selected_operations.discard(index)
        else:
            self._selected_operations.add(index)
        self._notify("selected_operations", self._selected_operations)

    def select_all_operations(self) -> None:
        """Select all operations in current plan."""
        if self._current_plan:
            self._selected_operations = set(range(len(self._current_plan.ops)))
            self._notify("selected_operations", self._selected_operations)

    def deselect_all_operations(self) -> None:
        """Deselect all operations."""
        self._selected_operations = set()
        self._notify("selected_operations", self._selected_operations)

    def get_selected_ops(self) -> list[Operation]:
        """Get list of selected operations."""
        if not self._current_plan:
            return []
        return [self._current_plan.ops[i] for i in sorted(self._selected_operations)]

    # ========== Operation Filter ==========

    @property
    def operation_filter(self) -> OperationFilter:
        return self._operation_filter

    @operation_filter.setter
    def operation_filter(self, value: OperationFilter) -> None:
        self._operation_filter = value
        self._notify("operation_filter", value)

    def update_filter(self, **kwargs) -> None:
        """Update filter settings."""
        for key, value in kwargs.items():
            if hasattr(self._operation_filter, key):
                setattr(self._operation_filter, key, value)
        self._notify("operation_filter", self._operation_filter)

    def clear_filter(self) -> None:
        """Reset filter to defaults."""
        self._operation_filter = OperationFilter()
        self._notify("operation_filter", self._operation_filter)

    # ========== Sessions (History) ==========

    @property
    def sessions(self) -> list[SessionSummary]:
        return self._sessions.copy()

    def add_session(self, session: SessionSummary) -> None:
        """Add a session to history."""
        self._sessions.insert(0, session)  # Most recent first
        self._notify("sessions", self._sessions)

    def clear_sessions(self) -> None:
        """Clear session history."""
        self._sessions = []
        self._notify("sessions", self._sessions)

    @property
    def last_session(self) -> SessionSummary | None:
        """Get the most recent session."""
        return self._sessions[0] if self._sessions else None

    # ========== User Rules ==========

    @property
    def user_rules(self) -> dict[str, list[str]]:
        return self._user_rules.copy()

    @user_rules.setter
    def user_rules(self, value: dict[str, list[str]]) -> None:
        self._user_rules = value
        self._notify("user_rules", value)

    # ========== Ignore Patterns ==========

    @property
    def user_ignore_patterns(self) -> list[str]:
        return self._user_ignore_patterns.copy()

    @user_ignore_patterns.setter
    def user_ignore_patterns(self, value: list[str]) -> None:
        self._user_ignore_patterns = value
        self._notify("user_ignore_patterns", value)

    # ========== Loading States ==========

    @property
    def is_scanning(self) -> bool:
        return self._is_scanning

    @is_scanning.setter
    def is_scanning(self, value: bool) -> None:
        self._is_scanning = value
        self._notify("is_scanning", value)

    @property
    def is_applying(self) -> bool:
        return self._is_applying

    @is_applying.setter
    def is_applying(self, value: bool) -> None:
        self._is_applying = value
        self._notify("is_applying", value)

    # ========== Errors ==========

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @last_error.setter
    def last_error(self, value: str | None) -> None:
        self._last_error = value
        self._notify("last_error", value)

    def clear_error(self) -> None:
        """Clear the last error."""
        self.last_error = None

    # ========== Persistence ==========

    def to_dict(self) -> dict:
        """Serialize state to dictionary for persistence."""
        return {
            "theme_mode": self._theme_mode,
            "root_folders": [
                {"path": str(rf.path), "enabled": rf.enabled}
                for rf in self._root_folders
            ],
            "scan_options": {
                "create_session_subfolders": self._scan_options.create_session_subfolders,
                "use_timestamps": self._scan_options.use_timestamps,
                "session_prefix": self._scan_options.session_prefix,
                "collision_strategy": self._scan_options.collision_strategy,
                "risk_threshold": self._scan_options.risk_threshold,
                "quarantine_deletes": self._scan_options.quarantine_deletes,
            },
            "user_ignore_patterns": self._user_ignore_patterns,
        }

    def from_dict(self, data: dict) -> None:
        """Load state from dictionary."""
        if "theme_mode" in data:
            self._theme_mode = data["theme_mode"]

        if "root_folders" in data:
            self._root_folders = [
                RootFolder(path=Path(rf["path"]), enabled=rf.get("enabled", True))
                for rf in data["root_folders"]
            ]

        if "scan_options" in data:
            opts = data["scan_options"]
            self._scan_options = ScanOptions(
                create_session_subfolders=opts.get("create_session_subfolders", True),
                use_timestamps=opts.get("use_timestamps", True),
                session_prefix=opts.get("session_prefix", "session"),
                collision_strategy=opts.get("collision_strategy", "rename"),
                risk_threshold=opts.get("risk_threshold", "medium"),
                quarantine_deletes=opts.get("quarantine_deletes", True),
            )

        if "user_ignore_patterns" in data:
            self._user_ignore_patterns = data["user_ignore_patterns"]

    def save(self) -> None:
        """Save current state to disk."""
        try:
            state_file = get_state_file()
            with open(state_file, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Failed to save state: {e}")

    def load(self) -> None:
        """Load state from disk."""
        try:
            state_file = get_state_file()
            if state_file.exists():
                with open(state_file, "r") as f:
                    data = json.load(f)
                self.from_dict(data)
        except Exception as e:
            print(f"Failed to load state: {e}")


# Global state instance
_app_state: AppState | None = None


def get_app_state() -> AppState:
    """Get the global application state instance."""
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state


def init_app_state() -> AppState:
    """Initialize a fresh application state."""
    global _app_state
    _app_state = AppState()
    return _app_state
