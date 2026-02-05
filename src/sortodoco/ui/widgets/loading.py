"""
Loading indicator widgets for SortoDoco GUI.
"""

import customtkinter as ctk
from typing import Optional
import math

from sortodoco.ui.theme import get_theme_manager


class LoadingSpinner(ctk.CTkFrame):
    """
    Animated loading spinner widget.

    Uses a simple text-based animation for compatibility.
    """

    FRAMES = ["◐", "◓", "◑", "◒"]

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        size: int = 24,
        text: str = "",
        **kwargs,
    ):
        self._theme = get_theme_manager()
        p = self._theme.palette

        super().__init__(master, fg_color="transparent", **kwargs)

        self._size = size
        self._text = text
        self._frame_index = 0
        self._is_running = False
        self._after_id: Optional[str] = None

        # Spinner label
        self._spinner_label = ctk.CTkLabel(
            self,
            text=self.FRAMES[0],
            font=ctk.CTkFont(size=size),
            text_color=p.accent,
            width=size + 8,
        )
        self._spinner_label.pack(side="left")

        # Text label
        if text:
            self._text_label = ctk.CTkLabel(
                self,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color=p.text_secondary,
            )
            self._text_label.pack(side="left", padx=(8, 0))
        else:
            self._text_label = None

    def start(self) -> None:
        """Start the spinner animation."""
        if not self._is_running:
            self._is_running = True
            self._animate()

    def stop(self) -> None:
        """Stop the spinner animation."""
        self._is_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _animate(self) -> None:
        """Animate the spinner."""
        if not self._is_running:
            return

        self._frame_index = (self._frame_index + 1) % len(self.FRAMES)
        self._spinner_label.configure(text=self.FRAMES[self._frame_index])
        self._after_id = self.after(100, self._animate)

    def set_text(self, text: str) -> None:
        """Update the loading text."""
        self._text = text
        if self._text_label:
            self._text_label.configure(text=text)
        elif text:
            p = self._theme.palette
            self._text_label = ctk.CTkLabel(
                self,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color=p.text_secondary,
            )
            self._text_label.pack(side="left", padx=(8, 0))


class LoadingOverlay(ctk.CTkFrame):
    """
    Full overlay with loading spinner.

    Covers the parent widget with a semi-transparent overlay.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        text: str = "Loading...",
        **kwargs,
    ):
        self._theme = get_theme_manager()
        p = self._theme.palette

        # Semi-transparent overlay
        super().__init__(
            master,
            fg_color=p.bg_primary,
            corner_radius=0,
            **kwargs,
        )

        self._text = text

        # Center container
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Spinner
        self._spinner = LoadingSpinner(center_frame, size=32)
        self._spinner.pack(pady=(0, 16))

        # Text
        self._text_label = ctk.CTkLabel(
            center_frame,
            text=text,
            font=ctk.CTkFont(size=15),
            text_color=p.text_primary,
        )
        self._text_label.pack()

        # Progress bar (optional)
        self._progress = ctk.CTkProgressBar(
            center_frame,
            width=200,
            height=4,
            fg_color=p.bg_tertiary,
            progress_color=p.accent,
        )
        self._progress.pack(pady=(16, 0))
        self._progress.set(0)

        # Subscribe to theme changes
        self._theme.subscribe(self._on_theme_change)

    def show(self) -> None:
        """Show the overlay and start animation."""
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self._spinner.start()

    def hide(self) -> None:
        """Hide the overlay and stop animation."""
        self._spinner.stop()
        self.place_forget()

    def set_text(self, text: str) -> None:
        """Update the loading text."""
        self._text = text
        self._text_label.configure(text=text)

    def set_progress(self, value: float) -> None:
        """Set progress value (0.0 to 1.0)."""
        self._progress.set(max(0.0, min(1.0, value)))

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes."""
        self.configure(fg_color=palette.bg_primary)
        self._text_label.configure(text_color=palette.text_primary)
        self._progress.configure(
            fg_color=palette.bg_tertiary,
            progress_color=palette.accent,
        )

    def destroy(self):
        """Clean up theme subscription on destroy."""
        self._theme.unsubscribe(self._on_theme_change)
        super().destroy()


class ProgressIndicator(ctk.CTkFrame):
    """
    Inline progress indicator with text and percentage.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        text: str = "Processing...",
        **kwargs,
    ):
        self._theme = get_theme_manager()
        p = self._theme.palette

        super().__init__(master, fg_color="transparent", **kwargs)

        # Text row
        text_row = ctk.CTkFrame(self, fg_color="transparent")
        text_row.pack(fill="x", pady=(0, 4))

        self._text_label = ctk.CTkLabel(
            text_row,
            text=text,
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        self._text_label.pack(side="left")

        self._percent_label = ctk.CTkLabel(
            text_row,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color=p.text_muted,
        )
        self._percent_label.pack(side="right")

        # Progress bar
        self._progress = ctk.CTkProgressBar(
            self,
            height=6,
            fg_color=p.bg_tertiary,
            progress_color=p.accent,
        )
        self._progress.pack(fill="x")
        self._progress.set(0)

    def set_progress(self, value: float, text: Optional[str] = None) -> None:
        """Set progress value and optionally update text."""
        clamped = max(0.0, min(1.0, value))
        self._progress.set(clamped)
        self._percent_label.configure(text=f"{int(clamped * 100)}%")
        if text:
            self._text_label.configure(text=text)
