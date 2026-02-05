"""
Settings view - Application preferences.
"""

import customtkinter as ctk
from typing import Optional, Callable

from sortodoco.ui.views.base import BaseView
from sortodoco.ui.widgets.card import Card
from sortodoco.ui.theme import get_theme_manager


class SettingsView(BaseView):
    """
    Settings view for application preferences.

    Features:
    - Theme selection (Light/Dark/System)
    - Safety settings
    - Logging settings
    - About section
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, title="Settings", on_navigate=on_navigate, **kwargs)

        self._build_content()

    def _build_content(self) -> None:
        """Build the settings content."""
        p = self._theme.palette

        self.content.grid_columnconfigure(0, weight=1)

        # Appearance Card
        appearance_card = Card(self.content, title="Appearance")
        appearance_card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._build_appearance_section(appearance_card.content_frame)

        # Safety Card
        safety_card = Card(self.content, title="Safety")
        safety_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        self._build_safety_section(safety_card.content_frame)

        # Logging Card
        logging_card = Card(self.content, title="Logging")
        logging_card.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        self._build_logging_section(logging_card.content_frame)

        # About Card
        about_card = Card(self.content, title="About")
        about_card.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        self._build_about_section(about_card.content_frame)

        # Action buttons
        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="e")

        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            font=ctk.CTkFont(size=13),
            width=140,
            height=40,
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            command=self._reset_settings,
        )
        reset_btn.pack(side="left", padx=8)

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            height=40,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._save_settings,
        )
        save_btn.pack(side="left")

    def _build_appearance_section(self, content: ctk.CTkFrame) -> None:
        """Build appearance settings."""
        p = self._theme.palette

        # Theme selection
        theme_frame = ctk.CTkFrame(content, fg_color="transparent")
        theme_frame.pack(fill="x", pady=8)

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=13),
            text_color=p.text_primary,
        )
        theme_label.pack(side="left")

        # Radio buttons for theme
        self._theme_var = ctk.StringVar(value=self._theme.mode)

        themes = [("Light", "light"), ("Dark", "dark"), ("System", "system")]

        for text, value in themes:
            rb = ctk.CTkRadioButton(
                theme_frame,
                text=text,
                variable=self._theme_var,
                value=value,
                font=ctk.CTkFont(size=12),
                fg_color=p.accent,
                hover_color=p.accent_hover,
                command=self._on_theme_select,
            )
            rb.pack(side="left", padx=16)

    def _build_safety_section(self, content: ctk.CTkFrame) -> None:
        """Build safety settings."""
        p = self._theme.palette

        # Confirm before applying
        self._confirm_apply_var = ctk.BooleanVar(value=True)
        confirm_cb = ctk.CTkCheckBox(
            content,
            text="Confirm before applying plans",
            font=ctk.CTkFont(size=12),
            variable=self._confirm_apply_var,
            fg_color=p.accent,
            hover_color=p.accent_hover,
        )
        confirm_cb.pack(anchor="w", pady=4)

        # Confirm high-risk
        self._confirm_risk_var = ctk.BooleanVar(value=True)
        risk_cb = ctk.CTkCheckBox(
            content,
            text="Confirm high-risk operations",
            font=ctk.CTkFont(size=12),
            variable=self._confirm_risk_var,
            fg_color=p.accent,
            hover_color=p.accent_hover,
        )
        risk_cb.pack(anchor="w", pady=4)

        # Quarantine
        self._quarantine_var = ctk.BooleanVar(value=True)
        quarantine_cb = ctk.CTkCheckBox(
            content,
            text="Move deleted files to quarantine",
            font=ctk.CTkFont(size=12),
            variable=self._quarantine_var,
            fg_color=p.accent,
            hover_color=p.accent_hover,
        )
        quarantine_cb.pack(anchor="w", pady=4)

        # Quarantine path
        path_frame = ctk.CTkFrame(content, fg_color="transparent")
        path_frame.pack(fill="x", pady=8)

        path_label = ctk.CTkLabel(
            path_frame,
            text="Quarantine path:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        path_label.pack(side="left")

        self._quarantine_path = ctk.CTkEntry(
            path_frame,
            width=250,
            height=28,
            font=ctk.CTkFont(size=11),
            placeholder_text="~/.sortodoco/quarantine",
        )
        self._quarantine_path.pack(side="right")

    def _build_logging_section(self, content: ctk.CTkFrame) -> None:
        """Build logging settings."""
        p = self._theme.palette

        # Log level
        level_frame = ctk.CTkFrame(content, fg_color="transparent")
        level_frame.pack(fill="x", pady=4)

        level_label = ctk.CTkLabel(
            level_frame,
            text="Log level:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        level_label.pack(side="left")

        self._log_level_var = ctk.StringVar(value="Info")
        level_menu = ctk.CTkOptionMenu(
            level_frame,
            width=100,
            height=28,
            values=["Debug", "Info", "Warning", "Error"],
            variable=self._log_level_var,
            font=ctk.CTkFont(size=12),
            fg_color=p.bg_tertiary,
            button_color=p.border,
        )
        level_menu.pack(side="right")

        # Retention
        retention_frame = ctk.CTkFrame(content, fg_color="transparent")
        retention_frame.pack(fill="x", pady=4)

        retention_label = ctk.CTkLabel(
            retention_frame,
            text="Retention:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        retention_label.pack(side="left")

        self._retention_var = ctk.StringVar(value="30 days")
        retention_menu = ctk.CTkOptionMenu(
            retention_frame,
            width=100,
            height=28,
            values=["7 days", "14 days", "30 days", "90 days", "Forever"],
            variable=self._retention_var,
            font=ctk.CTkFont(size=12),
            fg_color=p.bg_tertiary,
            button_color=p.border,
        )
        retention_menu.pack(side="right")

    def _build_about_section(self, content: ctk.CTkFrame) -> None:
        """Build about section."""
        p = self._theme.palette

        # Version
        version_label = ctk.CTkLabel(
            content,
            text="SortoDoco v0.1.0",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=p.text_primary,
        )
        version_label.pack(anchor="w", pady=(0, 4))

        # Description
        desc_label = ctk.CTkLabel(
            content,
            text="Local-first file organizer.\nSafe, transparent, and private.",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
            justify="left",
        )
        desc_label.pack(anchor="w", pady=(0, 8))

        # Links
        links_frame = ctk.CTkFrame(content, fg_color="transparent")
        links_frame.pack(anchor="w")

        github_btn = ctk.CTkButton(
            links_frame,
            text="View on GitHub",
            font=ctk.CTkFont(size=12),
            width=120,
            height=28,
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            command=self._open_github,
        )
        github_btn.pack(side="left", padx=(0, 8))

    def _on_theme_select(self) -> None:
        """Handle theme selection change."""
        mode = self._theme_var.get()
        self._theme.set_mode(mode)
        self._state.theme_mode = mode

    def _reset_settings(self) -> None:
        """Reset all settings to defaults."""
        self._theme_var.set("system")
        self._confirm_apply_var.set(True)
        self._confirm_risk_var.set(True)
        self._quarantine_var.set(True)
        self._log_level_var.set("Info")
        self._retention_var.set("30 days")
        self._on_theme_select()

    def _save_settings(self) -> None:
        """Save settings."""
        # Save state to disk
        self._state.save()

        # Show confirmation (if we had toast access)
        print("Settings saved")

    def _open_github(self) -> None:
        """Open GitHub repository."""
        import webbrowser

        webbrowser.open("https://github.com/CodingWithMK/sortodoco_file-organizer")

    def refresh(self) -> None:
        """Refresh the view."""
        for widget in self.content.winfo_children():
            widget.destroy()
        self._build_content()

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes - rebuild content with new colors."""
        super()._on_theme_change(palette)
        # Rebuild content to apply new theme colors to all widgets
        self.refresh()
