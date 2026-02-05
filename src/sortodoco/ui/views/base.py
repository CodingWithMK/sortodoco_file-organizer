"""
Base view class for all views.
"""

import customtkinter as ctk
from typing import Optional, Callable

from sortodoco.ui.theme import get_theme_manager
from sortodoco.ui.state import get_app_state


class BaseView(ctk.CTkFrame):
    """
    Base class for all views.

    Provides common functionality:
    - Access to theme and state
    - Standard layout with header
    - Navigation callback
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        title: str = "View",
        on_navigate: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette

        super().__init__(master, fg_color=p.bg_primary, corner_radius=0, **kwargs)

        self._theme = theme
        self._state = get_app_state()
        self._title = title
        self._on_navigate = on_navigate

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self._build_header()

        # Content area
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Subscribe to theme changes
        theme.subscribe(self._on_theme_change)

    def _build_header(self) -> None:
        """Build the view header."""
        p = self._theme.palette

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))

        self._title_label = ctk.CTkLabel(
            header,
            text=self._title,
            font=ctk.CTkFont(size=self._theme.fonts.h1_size, weight="bold"),
            text_color=p.text_primary,
        )
        self._title_label.pack(side="left")

    def navigate_to(self, view_name: str) -> None:
        """Navigate to another view."""
        if self._on_navigate:
            self._on_navigate(view_name)

    def refresh(self) -> None:
        """Refresh the view. Override in subclasses."""
        pass

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes."""
        self.configure(fg_color=palette.bg_primary)
        if hasattr(self, "_title_label"):
            self._title_label.configure(text_color=palette.text_primary)

    def destroy(self):
        """Clean up theme subscription on destroy."""
        self._theme.unsubscribe(self._on_theme_change)
        super().destroy()
