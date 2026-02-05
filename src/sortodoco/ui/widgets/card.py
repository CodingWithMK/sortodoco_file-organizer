"""
Card widget - A styled container component.
"""

import customtkinter as ctk
from typing import Optional

from sortodoco.ui.theme import get_theme_manager


class Card(ctk.CTkFrame):
    """
    A card container with styling for grouping related content.

    Features:
    - Rounded corners
    - Subtle border
    - Optional title and subtitle
    - Content area
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        width: int = 300,
        height: Optional[int] = None,
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette

        # Build frame kwargs - only include height if specified
        frame_kwargs = {
            "width": width,
            "corner_radius": theme.style.border_radius_card,
            "fg_color": p.bg_secondary,
            "border_width": 1,
            "border_color": p.border,
            **kwargs,
        }
        if height is not None:
            frame_kwargs["height"] = height

        super().__init__(master, **frame_kwargs)

        self._theme = theme
        self._title = title
        self._subtitle = subtitle

        # Configure internal layout
        self.grid_columnconfigure(0, weight=1)

        current_row = 0

        # Title area
        if title:
            self._title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=theme.fonts.h3_size, weight="bold"),
                text_color=p.text_primary,
                anchor="w",
            )
            self._title_label.grid(
                row=current_row,
                column=0,
                sticky="ew",
                padx=theme.spacing.md,
                pady=(theme.spacing.md, theme.spacing.xs),
            )
            current_row += 1

        # Subtitle
        if subtitle:
            self._subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=theme.fonts.small_size),
                text_color=p.text_secondary,
                anchor="w",
            )
            self._subtitle_label.grid(
                row=current_row,
                column=0,
                sticky="ew",
                padx=theme.spacing.md,
                pady=(0, theme.spacing.sm),
            )
            current_row += 1

        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(
            row=current_row,
            column=0,
            sticky="nsew",
            padx=theme.spacing.md,
            pady=(theme.spacing.sm, theme.spacing.md),
        )
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(current_row, weight=1)

        # Subscribe to theme changes
        theme.subscribe(self._on_theme_change)

    def _on_theme_change(self, palette):
        """Handle theme changes."""
        self.configure(fg_color=palette.bg_secondary, border_color=palette.border)
        if hasattr(self, "_title_label"):
            self._title_label.configure(text_color=palette.text_primary)
        if hasattr(self, "_subtitle_label"):
            self._subtitle_label.configure(text_color=palette.text_secondary)

    def destroy(self):
        """Clean up theme subscription on destroy."""
        self._theme.unsubscribe(self._on_theme_change)
        super().destroy()

    def set_title(self, title: str) -> None:
        """Update the card title."""
        if hasattr(self, "_title_label"):
            self._title_label.configure(text=title)

    def set_subtitle(self, subtitle: str) -> None:
        """Update the card subtitle."""
        if hasattr(self, "_subtitle_label"):
            self._subtitle_label.configure(text=subtitle)
