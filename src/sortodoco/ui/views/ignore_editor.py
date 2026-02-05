"""
Ignore Editor view - Manage ignore patterns.
"""

import customtkinter as ctk
from typing import Optional, Callable

from sortodoco.ui.views.base import BaseView
from sortodoco.ui.widgets.card import Card
from sortodoco.ui.theme import get_theme_manager
from sortodoco.infra.config import BUILTIN_IGNORE


class IgnoreEditorView(BaseView):
    """
    Ignore editor view for managing ignore patterns.

    Features:
    - View default ignore patterns
    - Add/remove user patterns
    - Test patterns
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(
            master, title="Ignore Patterns", on_navigate=on_navigate, **kwargs
        )

        self._build_content()

    def _build_content(self) -> None:
        """Build the ignore editor content."""
        p = self._theme.palette

        self.content.grid_columnconfigure((0, 1), weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Left - Default patterns
        default_card = Card(
            self.content, title="Default Patterns", subtitle="Built-in (read-only)"
        )
        default_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_default_patterns(default_card.content_frame)

        # Right - User patterns
        user_card = Card(
            self.content, title="User Patterns", subtitle="Your custom patterns"
        )
        user_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._build_user_patterns(user_card.content_frame)

        # Test section
        test_card = Card(self.content, title="Test Pattern")
        test_card.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        self._build_test_section(test_card.content_frame)

    def _build_default_patterns(self, content: ctk.CTkFrame) -> None:
        """Build default patterns display."""
        p = self._theme.palette

        scroll = ctk.CTkScrollableFrame(content, fg_color="transparent", height=300)
        scroll.pack(fill="both", expand=True)

        # Suffixes
        section = ctk.CTkLabel(
            scroll,
            text="Ignored Suffixes:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p.text_primary,
        )
        section.pack(anchor="w", pady=(0, 4))

        for suffix in BUILTIN_IGNORE.suffixes:
            item = ctk.CTkLabel(
                scroll,
                text=f"  • {suffix}",
                font=ctk.CTkFont(size=11),
                text_color=p.text_secondary,
            )
            item.pack(anchor="w")

        # Names
        section = ctk.CTkLabel(
            scroll,
            text="\nIgnored Names:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p.text_primary,
        )
        section.pack(anchor="w", pady=(8, 4))

        for name in BUILTIN_IGNORE.names:
            item = ctk.CTkLabel(
                scroll,
                text=f"  • {name}",
                font=ctk.CTkFont(size=11),
                text_color=p.text_secondary,
            )
            item.pack(anchor="w")

        # Globs
        section = ctk.CTkLabel(
            scroll,
            text="\nGlob Patterns:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p.text_primary,
        )
        section.pack(anchor="w", pady=(8, 4))

        for glob in BUILTIN_IGNORE.globs:
            item = ctk.CTkLabel(
                scroll,
                text=f"  • {glob}",
                font=ctk.CTkFont(size=11),
                text_color=p.text_secondary,
            )
            item.pack(anchor="w")

    def _build_user_patterns(self, content: ctk.CTkFrame) -> None:
        """Build user patterns section."""
        p = self._theme.palette

        user_patterns = self._state.user_ignore_patterns

        # Add pattern input
        add_frame = ctk.CTkFrame(content, fg_color="transparent")
        add_frame.pack(fill="x", pady=(0, 8))

        self._pattern_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="e.g., node_modules, *.log",
            height=32,
            font=ctk.CTkFont(size=12),
        )
        self._pattern_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        add_btn = ctk.CTkButton(
            add_frame,
            text="Add",
            width=60,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._add_pattern,
        )
        add_btn.pack(side="right")

        # Patterns list
        self._patterns_list = ctk.CTkScrollableFrame(
            content, fg_color="transparent", height=250
        )
        self._patterns_list.pack(fill="both", expand=True)

        self._refresh_user_patterns()

    def _refresh_user_patterns(self) -> None:
        """Refresh user patterns list."""
        p = self._theme.palette

        for widget in self._patterns_list.winfo_children():
            widget.destroy()

        user_patterns = self._state.user_ignore_patterns

        if not user_patterns:
            empty_label = ctk.CTkLabel(
                self._patterns_list,
                text="No user patterns added",
                font=ctk.CTkFont(size=12),
                text_color=p.text_muted,
            )
            empty_label.pack(pady=20)
            return

        for pattern in user_patterns:
            row = ctk.CTkFrame(
                self._patterns_list, fg_color=p.bg_tertiary, corner_radius=4
            )
            row.pack(fill="x", pady=2)

            pattern_label = ctk.CTkLabel(
                row, text=pattern, font=ctk.CTkFont(size=12), text_color=p.text_primary
            )
            pattern_label.pack(side="left", padx=8, pady=4)

            remove_btn = ctk.CTkButton(
                row,
                text="×",
                width=24,
                height=24,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color=p.error,
                text_color=p.text_secondary,
                command=lambda pat=pattern: self._remove_pattern(pat),
            )
            remove_btn.pack(side="right", padx=4)

    def _build_test_section(self, content: ctk.CTkFrame) -> None:
        """Build test section."""
        p = self._theme.palette

        test_frame = ctk.CTkFrame(content, fg_color="transparent")
        test_frame.pack(fill="x")

        test_label = ctk.CTkLabel(
            test_frame,
            text="Test path:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        test_label.pack(side="left")

        self._test_entry = ctk.CTkEntry(
            test_frame,
            width=300,
            height=32,
            placeholder_text="/path/to/node_modules/file.js",
            font=ctk.CTkFont(size=12),
        )
        self._test_entry.pack(side="left", padx=8)

        test_btn = ctk.CTkButton(
            test_frame,
            text="Test",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._test_pattern,
        )
        test_btn.pack(side="left")

        self._test_result = ctk.CTkLabel(
            test_frame, text="", font=ctk.CTkFont(size=12), text_color=p.text_primary
        )
        self._test_result.pack(side="left", padx=16)

    def _add_pattern(self) -> None:
        """Add a user pattern."""
        pattern = self._pattern_entry.get().strip()
        if pattern:
            patterns = self._state.user_ignore_patterns
            if pattern not in patterns:
                patterns.append(pattern)
                self._state.user_ignore_patterns = patterns
                self._pattern_entry.delete(0, "end")
                self._refresh_user_patterns()

    def _remove_pattern(self, pattern: str) -> None:
        """Remove a user pattern."""
        patterns = self._state.user_ignore_patterns
        if pattern in patterns:
            patterns.remove(pattern)
            self._state.user_ignore_patterns = patterns
            self._refresh_user_patterns()

    def _test_pattern(self) -> None:
        """Test if a path would be ignored."""
        path = self._test_entry.get().strip()
        if not path:
            self._test_result.configure(text="")
            return

        p = self._theme.palette

        # Check against patterns
        ignored = False
        matched = None

        path_lower = path.lower()

        # Check suffixes
        for suffix in BUILTIN_IGNORE.suffixes:
            if path_lower.endswith(suffix):
                ignored = True
                matched = f"suffix: {suffix}"
                break

        # Check names
        if not ignored:
            for name in BUILTIN_IGNORE.names:
                if name.lower() in path_lower:
                    ignored = True
                    matched = f"name: {name}"
                    break

        # Check user patterns
        if not ignored:
            for pattern in self._state.user_ignore_patterns:
                if pattern.lower() in path_lower:
                    ignored = True
                    matched = f"user pattern: {pattern}"
                    break

        if ignored:
            self._test_result.configure(
                text=f"✗ Ignored ({matched})", text_color=p.warning
            )
        else:
            self._test_result.configure(text="✓ Not ignored", text_color=p.success)

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
