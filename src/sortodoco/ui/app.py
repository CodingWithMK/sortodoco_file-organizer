"""
Main application entry point for SortoDoco GUI.
"""

import customtkinter as ctk
from pathlib import Path
from datetime import datetime
from typing import Optional

from sortodoco.ui.theme import init_theme, get_theme_manager
from sortodoco.ui.state import init_app_state, get_app_state, SessionSummary
from sortodoco.ui.components.sidebar import Sidebar
from sortodoco.ui.widgets.toast import ToastManager
from sortodoco.ui.widgets.loading import LoadingOverlay
from sortodoco.ui.views.dashboard import DashboardView
from sortodoco.ui.views.scan_setup import ScanSetupView
from sortodoco.ui.views.plan_preview import PlanPreviewView
from sortodoco.ui.views.rules_editor import RulesEditorView
from sortodoco.ui.views.ignore_editor import IgnoreEditorView
from sortodoco.ui.views.history import HistoryView
from sortodoco.ui.views.settings import SettingsView

from sortodoco.services.planner import plan_downloads
from sortodoco.services.executor import apply_plan


class SortoDocoApp(ctk.CTk):
    """
    Main application window for SortoDoco.

    Features:
    - Sidebar navigation
    - View routing
    - Service integration (planner/executor)
    - Toast notifications
    """

    APP_NAME = "SortoDoco"
    APP_VERSION = "0.1.0"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WIDTH = 900
    MIN_HEIGHT = 600

    def __init__(self):
        # Initialize theme and state before CTk
        self._theme = init_theme("system")
        self._state = init_app_state()

        # Load persisted state
        self._state.load()

        # Apply loaded theme mode
        if self._state.theme_mode != "system":
            self._theme.set_mode(self._state.theme_mode)

        super().__init__()

        # Window setup
        self.title(f"{self.APP_NAME} - File Organizer")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Center window on screen
        self._center_window()

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize components
        self._views: dict[str, ctk.CTkFrame] = {}
        self._current_view: Optional[ctk.CTkFrame] = None

        # Build UI
        self._build_sidebar()
        self._build_content_area()

        # Initialize toast manager
        self._toast_manager = ToastManager(self._content_area)

        # Initialize loading overlay
        self._loading_overlay = LoadingOverlay(self._content_area, text="Loading...")

        # Subscribe to state changes
        self._state.subscribe("current_view", self._on_view_change)

        # Show initial view
        self._navigate_to("dashboard")

        # Bind keyboard shortcuts
        self._bind_shortcuts()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self) -> None:
        """Center the window on screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.WINDOW_WIDTH) // 2
        y = (screen_height - self.WINDOW_HEIGHT) // 2
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")

    def _build_sidebar(self) -> None:
        """Build the navigation sidebar."""
        self._sidebar = Sidebar(
            self, on_navigate=self._navigate_to, current_view="dashboard"
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")

    def _build_content_area(self) -> None:
        """Build the main content area."""
        p = self._theme.palette

        self._content_area = ctk.CTkFrame(self, fg_color=p.bg_primary, corner_radius=0)
        self._content_area.grid(row=0, column=1, sticky="nsew")
        self._content_area.grid_columnconfigure(0, weight=1)
        self._content_area.grid_rowconfigure(0, weight=1)

        # Subscribe to theme changes
        self._theme.subscribe(self._on_theme_change)

    def _navigate_to(self, view_name: str) -> None:
        """Navigate to a specific view."""
        # Hide current view
        if self._current_view:
            self._current_view.grid_forget()

        # Get or create view
        view = self._get_view(view_name)

        # Show view
        view.grid(row=0, column=0, sticky="nsew")
        self._current_view = view

        # Update sidebar
        self._sidebar.set_active_view(view_name)

        # Refresh view
        if hasattr(view, "refresh"):
            view.refresh()

    def _get_view(self, view_name: str) -> ctk.CTkFrame:
        """Get or create a view by name."""
        if view_name not in self._views:
            self._views[view_name] = self._create_view(view_name)
        return self._views[view_name]

    def _create_view(self, view_name: str) -> ctk.CTkFrame:
        """Create a view instance by name."""
        views = {
            "dashboard": lambda: DashboardView(
                self._content_area, on_navigate=self._navigate_to
            ),
            "scan_setup": lambda: ScanSetupView(
                self._content_area,
                on_navigate=self._navigate_to,
                on_plan=self._handle_plan,
            ),
            "plan_preview": lambda: PlanPreviewView(
                self._content_area,
                on_navigate=self._navigate_to,
                on_apply=self._handle_apply,
            ),
            "rules_editor": lambda: RulesEditorView(
                self._content_area, on_navigate=self._navigate_to
            ),
            "ignore_editor": lambda: IgnoreEditorView(
                self._content_area, on_navigate=self._navigate_to
            ),
            "history": lambda: HistoryView(
                self._content_area, on_navigate=self._navigate_to
            ),
            "settings": lambda: SettingsView(
                self._content_area, on_navigate=self._navigate_to
            ),
        }

        if view_name in views:
            return views[view_name]()

        # Fallback - return dashboard
        return views["dashboard"]()

    def _on_view_change(self, view_name: str) -> None:
        """Handle state-driven view changes."""
        self._navigate_to(view_name)

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes."""
        self._content_area.configure(fg_color=palette.bg_primary)

    def _handle_plan(self) -> None:
        """Handle plan generation request."""
        # Get enabled root folders
        root_folders = self._state.get_enabled_root_folders()

        if not root_folders:
            self._toast_manager.warning("Please add and enable at least one folder")
            return

        # For now, use the first folder
        root_folder = root_folders[0]

        # Get rules path
        rules_path = Path(__file__).parent.parent.parent / "rules" / "extensions.json"

        if not rules_path.exists():
            # Try alternative path
            rules_path = Path.cwd() / "rules" / "extensions.json"

        if not rules_path.exists():
            self._toast_manager.error("Rules file not found")
            return

        # Show loading overlay
        self._loading_overlay.set_text("Scanning files...")
        self._loading_overlay.set_progress(0)
        self._loading_overlay.show()

        try:
            self._state.is_scanning = True
            self._loading_overlay.set_progress(0.3)

            # Generate plan
            plan = plan_downloads(root_folder, rules_path)
            self._loading_overlay.set_progress(0.9)

            # Store in state
            self._state.current_plan = plan
            self._loading_overlay.set_progress(1.0)

            self._toast_manager.success(f"Plan generated: {len(plan.ops)} operations")

            # Navigate to preview
            self._navigate_to("plan_preview")

        except Exception as e:
            self._toast_manager.error(f"Error generating plan: {str(e)}")
        finally:
            self._state.is_scanning = False
            self._loading_overlay.hide()

    def _handle_apply(self) -> None:
        """Handle plan application request."""
        plan = self._state.current_plan

        if not plan:
            self._toast_manager.warning("No plan to apply")
            return

        # Show loading overlay
        self._loading_overlay.set_text("Applying plan...")
        self._loading_overlay.set_progress(0)
        self._loading_overlay.show()

        try:
            self._state.is_applying = True
            self._loading_overlay.set_progress(0.2)

            # Apply the plan
            report = apply_plan(plan)
            self._loading_overlay.set_progress(0.8)

            # Create session summary
            session = SessionSummary(
                session_id=plan.session_ts,
                timestamp=datetime.now(),
                root_folders=self._state.get_enabled_root_folders(),
                total_ops=len(plan.ops),
                moved=report.get("moved", 0),
                skipped=report.get("skipped", 0),
                errors=len(report.get("errors", [])),
            )

            # Add to history
            self._state.add_session(session)
            self._loading_overlay.set_progress(0.95)

            # Clear current plan
            self._state.current_plan = None
            self._loading_overlay.set_progress(1.0)

            # Show result
            if session.errors > 0:
                self._toast_manager.warning(
                    f"Completed with {session.errors} errors. {session.moved} files moved."
                )
            else:
                self._toast_manager.success(
                    f"Successfully moved {session.moved} files!"
                )

            # Navigate to dashboard
            self._navigate_to("dashboard")

        except Exception as e:
            self._toast_manager.error(f"Error applying plan: {str(e)}")
        finally:
            self._state.is_applying = False
            self._loading_overlay.hide()

    def _on_close(self) -> None:
        """Handle window close."""
        # Save state before closing
        self._state.save()
        self.destroy()

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        # Use Command on macOS, Control on other platforms
        import sys

        modifier = "Command" if sys.platform == "darwin" else "Control"

        # Navigation shortcuts
        self.bind(
            f"<{modifier}-n>", lambda e: self._navigate_to("scan_setup")
        )  # New scan
        self.bind(
            f"<{modifier}-p>", lambda e: self._navigate_to("plan_preview")
        )  # Plan preview
        self.bind(f"<{modifier}-h>", lambda e: self._navigate_to("history"))  # History
        self.bind(
            f"<{modifier}-r>", lambda e: self._navigate_to("rules_editor")
        )  # Rules
        self.bind(
            f"<{modifier}-i>", lambda e: self._navigate_to("ignore_editor")
        )  # Ignore
        self.bind(
            f"<{modifier}-comma>", lambda e: self._navigate_to("settings")
        )  # Settings (Cmd+,)
        self.bind(
            f"<{modifier}-d>", lambda e: self._navigate_to("dashboard")
        )  # Dashboard

        # Action shortcuts
        self.bind(
            f"<{modifier}-Return>", lambda e: self._handle_plan()
        )  # Generate plan
        self.bind(
            f"<{modifier}-Shift-Return>", lambda e: self._handle_apply()
        )  # Apply plan

        # Theme toggle
        self.bind(f"<{modifier}-t>", lambda e: self._toggle_theme())

        # Escape to go back to dashboard
        self.bind("<Escape>", lambda e: self._navigate_to("dashboard"))

    def _toggle_theme(self) -> None:
        """Toggle between light and dark theme."""
        current = self._state.theme_mode
        if current == "light":
            new_mode = "dark"
        elif current == "dark":
            new_mode = "light"
        else:  # system
            # If system, switch to the opposite of current appearance
            new_mode = (
                "light" if self._theme.palette.text_primary == "#FFFFFF" else "dark"
            )

        self._theme.set_mode(new_mode)
        self._state.theme_mode = new_mode


def run_app():
    """Run the SortoDoco application."""
    app = SortoDocoApp()
    app.mainloop()


# Entry point
if __name__ == "__main__":
    run_app()
