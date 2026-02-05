"""
Sidebar navigation component.
"""

import customtkinter as ctk
from typing import Callable, Optional, Literal

from sortodoco.ui.theme import get_theme_manager, NAV_ICONS, ThemeMode


class NavItem(ctk.CTkButton):
    """A single navigation item in the sidebar."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        text: str,
        icon: str,
        view_name: str,
        on_click: Callable[[str], None],
        is_active: bool = False,
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette
        sidebar_colors = theme.get_sidebar_colors()

        self._view_name = view_name
        self._on_click = on_click
        self._is_active = is_active
        self._theme = theme

        # Determine colors based on active state
        fg = sidebar_colors["active"] if is_active else "transparent"
        text_color = p.accent if is_active else sidebar_colors["text"]

        super().__init__(
            master,
            text=f"  {icon}  {text}",
            font=ctk.CTkFont(size=13, weight="bold" if is_active else "normal"),
            fg_color=fg,
            hover_color=sidebar_colors["hover"],
            text_color=text_color,
            anchor="w",
            height=44,
            corner_radius=8,
            command=self._handle_click,
            **kwargs,
        )

        # Subscribe to theme changes
        theme.subscribe(self._on_theme_change)

    def _handle_click(self) -> None:
        """Handle click on nav item."""
        self._on_click(self._view_name)

    def set_active(self, active: bool) -> None:
        """Set the active state."""
        self._is_active = active
        self._update_colors()

    def _update_colors(self) -> None:
        """Update colors based on current theme and active state."""
        p = self._theme.palette
        sidebar_colors = self._theme.get_sidebar_colors()

        fg = sidebar_colors["active"] if self._is_active else "transparent"
        text_color = p.accent if self._is_active else sidebar_colors["text"]

        self.configure(
            fg_color=fg,
            hover_color=sidebar_colors["hover"],
            text_color=text_color,
            font=ctk.CTkFont(size=13, weight="bold" if self._is_active else "normal"),
        )

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes."""
        self._update_colors()

    def destroy(self):
        """Clean up theme subscription on destroy."""
        self._theme.unsubscribe(self._on_theme_change)
        super().destroy()


class ThemeSelector(ctk.CTkFrame):
    """Theme selector dropdown."""

    THEME_OPTIONS = {
        "Light": "light",
        "Dark": "dark",
        "System": "system",
    }

    THEME_LABELS = {
        "light": "Light",
        "dark": "Dark",
        "system": "System",
    }

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette

        super().__init__(master, fg_color="transparent", **kwargs)

        self._theme = theme
        self._on_change = on_change

        # Label
        self._label = ctk.CTkLabel(
            self,
            text="Theme",
            font=ctk.CTkFont(size=11),
            text_color=p.text_muted,
        )
        self._label.pack(anchor="w", pady=(0, 4))

        # Get current theme label
        current_label = self.THEME_LABELS.get(theme.mode, "System")

        # Option menu - use button_hover_color for better contrast
        self._option_menu = ctk.CTkOptionMenu(
            self,
            values=list(self.THEME_OPTIONS.keys()),
            command=self._on_theme_select,
            width=140,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=p.bg_tertiary,
            button_color=p.accent,
            button_hover_color=p.accent_hover,
            dropdown_fg_color=p.bg_secondary,
            dropdown_hover_color=p.accent_light,
            dropdown_text_color=p.text_primary,
            text_color=p.text_primary,
        )
        self._option_menu.set(current_label)
        self._option_menu.pack(fill="x")

        # Subscribe to external theme changes
        theme.subscribe(self._on_external_theme_change)

    def _on_theme_select(self, choice: str) -> None:
        """Handle theme selection from dropdown."""
        mode = self.THEME_OPTIONS.get(choice, "system")
        self._theme.set_mode(mode)  # type: ignore
        if self._on_change:
            self._on_change(mode)

    def _on_external_theme_change(self, palette) -> None:
        """Handle external theme changes (keyboard shortcuts, settings)."""
        # Update label colors
        self._label.configure(text_color=palette.text_muted)

        # Update option menu colors - use accent for button to ensure visibility
        self._option_menu.configure(
            fg_color=palette.bg_tertiary,
            button_color=palette.accent,
            button_hover_color=palette.accent_hover,
            dropdown_fg_color=palette.bg_secondary,
            dropdown_hover_color=palette.accent_light,
            dropdown_text_color=palette.text_primary,
            text_color=palette.text_primary,
        )
        # Update selected value to reflect current theme
        current_label = self.THEME_LABELS.get(self._theme.mode, "System")
        self._option_menu.set(current_label)

    def destroy(self):
        """Clean up theme subscription on destroy."""
        self._theme.unsubscribe(self._on_external_theme_change)
        super().destroy()


class Sidebar(ctk.CTkFrame):
    """
    Navigation sidebar component.

    Features:
    - Logo/branding area
    - Navigation items with clear sections
    - Theme selector dropdown at bottom
    """

    # Main navigation items
    NAV_MAIN = [
        ("Dashboard", "dashboard"),
        ("New Scan", "scan_setup"),
        ("Plan Preview", "plan_preview"),
    ]

    # Configuration items
    NAV_CONFIG = [
        ("Rules", "rules_editor"),
        ("Ignore Patterns", "ignore_editor"),
    ]

    # Secondary items
    NAV_SECONDARY = [
        ("History", "history"),
        ("Settings", "settings"),
    ]

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Callable[[str], None],
        current_view: str = "dashboard",
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette

        super().__init__(
            master,
            width=260,  # Slightly wider for better readability
            corner_radius=0,
            fg_color=p.sidebar_bg,
            **kwargs,
        )

        self._theme = theme
        self._on_navigate = on_navigate
        self._current_view = current_view
        self._nav_items: dict[str, NavItem] = {}
        self._section_labels: list[ctk.CTkLabel] = []
        self._dividers: list[ctk.CTkFrame] = []

        # Prevent resizing
        self.grid_propagate(False)
        self.pack_propagate(False)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Logo area
        self._build_logo_area()

        # Navigation items
        self._build_nav_items()

        # Theme toggle at bottom
        self._build_theme_selector()

        # Subscribe to theme changes
        theme.subscribe(self._on_theme_change)

    def _build_logo_area(self) -> None:
        """Build the logo/branding area."""
        p = self._theme.palette

        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(24, 16), sticky="ew")

        # App icon (simple, professional)
        icon_label = ctk.CTkLabel(
            logo_frame,
            text="◈",
            font=ctk.CTkFont(size=28),
            text_color=p.accent,
        )
        icon_label.pack(side="left")

        # App name
        name_label = ctk.CTkLabel(
            logo_frame,
            text="SortoDoco",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=p.text_primary,
        )
        name_label.pack(side="left", padx=10)

        self._logo_icon = icon_label
        self._logo_name = name_label

    def _build_nav_items(self) -> None:
        """Build the navigation items with sections."""
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.grid(row=1, column=0, padx=16, sticky="new")

        # Main navigation section
        self._build_nav_section(nav_frame, "", self.NAV_MAIN)

        # Divider
        self._build_divider(nav_frame)

        # Configuration section
        self._build_nav_section(nav_frame, "Configure", self.NAV_CONFIG)

        # Divider
        self._build_divider(nav_frame)

        # Secondary section
        self._build_nav_section(nav_frame, "", self.NAV_SECONDARY)

    def _build_nav_section(
        self, parent: ctk.CTkFrame, title: str, items: list[tuple[str, str]]
    ) -> None:
        """Build a navigation section with optional title."""
        p = self._theme.palette

        if title:
            section_label = ctk.CTkLabel(
                parent,
                text=title.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=p.text_muted,
            )
            section_label.pack(fill="x", pady=(16, 8), padx=4)
            self._section_labels.append(section_label)

        for text, view_name in items:
            icon = NAV_ICONS.get(view_name, "◇")
            is_active = view_name == self._current_view

            item = NavItem(
                parent,
                text=text,
                icon=icon,
                view_name=view_name,
                on_click=self._handle_nav_click,
                is_active=is_active,
            )
            item.pack(fill="x", pady=2)
            self._nav_items[view_name] = item

    def _build_divider(self, parent: ctk.CTkFrame) -> None:
        """Build a subtle divider line."""
        p = self._theme.palette
        divider = ctk.CTkFrame(
            parent,
            height=1,
            fg_color=p.border,
        )
        divider.pack(fill="x", pady=12, padx=8)
        self._dividers.append(divider)

    def _build_theme_selector(self) -> None:
        """Build the theme selector at the bottom."""
        p = self._theme.palette

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self._theme_selector = ThemeSelector(bottom_frame)
        self._theme_selector.pack(fill="x")

    def _handle_nav_click(self, view_name: str) -> None:
        """Handle navigation item click."""
        if view_name != self._current_view:
            # Update active states
            for name, item in self._nav_items.items():
                item.set_active(name == view_name)

            self._current_view = view_name
            self._on_navigate(view_name)

    def set_active_view(self, view_name: str) -> None:
        """Set the active view externally."""
        self._current_view = view_name
        for name, item in self._nav_items.items():
            item.set_active(name == view_name)

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes."""
        self.configure(fg_color=palette.sidebar_bg)

        # Update logo
        if hasattr(self, "_logo_icon"):
            self._logo_icon.configure(text_color=palette.accent)
        if hasattr(self, "_logo_name"):
            self._logo_name.configure(text_color=palette.text_primary)

        # Update section labels
        for label in self._section_labels:
            try:
                label.configure(text_color=palette.text_muted)
            except Exception:
                pass

        # Update dividers
        for divider in self._dividers:
            try:
                divider.configure(fg_color=palette.border)
            except Exception:
                pass

    def destroy(self):
        """Clean up theme subscription on destroy."""
        self._theme.unsubscribe(self._on_theme_change)
        super().destroy()
