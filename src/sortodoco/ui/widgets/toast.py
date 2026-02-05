"""
Toast notification widget.
"""

import customtkinter as ctk
from typing import Literal, Optional, Callable
from dataclasses import dataclass

from sortodoco.ui.theme import get_theme_manager


ToastType = Literal["success", "warning", "error", "info"]


@dataclass
class ToastConfig:
    """Configuration for a toast notification."""

    message: str
    toast_type: ToastType = "info"
    duration: int = 4000  # milliseconds
    on_click: Optional[Callable] = None


class Toast(ctk.CTkFrame):
    """
    A single toast notification.

    Features:
    - Icon based on type
    - Auto-dismiss after duration
    - Click to dismiss early
    - Fade animation (if supported)
    """

    ICONS = {
        "success": "✓",
        "warning": "⚠",
        "error": "✗",
        "info": "ℹ",
    }

    COLORS = {
        "success": "#22C55E",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#3B82F6",
    }

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        config: ToastConfig,
        on_dismiss: Optional[Callable] = None,
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette

        color = self.COLORS.get(config.toast_type, self.COLORS["info"])

        super().__init__(
            master,
            corner_radius=8,
            fg_color=p.bg_secondary,
            border_width=2,
            border_color=color,
            **kwargs,
        )

        self._config = config
        self._on_dismiss = on_dismiss
        self._dismiss_job = None

        # Layout
        self.grid_columnconfigure(1, weight=1)

        # Icon
        icon = self.ICONS.get(config.toast_type, "ℹ")
        self._icon_label = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=18), text_color=color, width=30
        )
        self._icon_label.grid(row=0, column=0, padx=(12, 8), pady=12)

        # Message
        self._message_label = ctk.CTkLabel(
            self,
            text=config.message,
            font=ctk.CTkFont(size=13),
            text_color=p.text_primary,
            anchor="w",
        )
        self._message_label.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="ew")

        # Close button
        self._close_btn = ctk.CTkButton(
            self,
            text="×",
            width=24,
            height=24,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=p.bg_tertiary,
            text_color=p.text_secondary,
            command=self.dismiss,
        )
        self._close_btn.grid(row=0, column=2, padx=(0, 8), pady=8)

        # Click to dismiss
        self.bind("<Button-1>", lambda e: self._handle_click())
        self._message_label.bind("<Button-1>", lambda e: self._handle_click())

        # Start auto-dismiss timer
        if config.duration > 0:
            self._dismiss_job = self.after(config.duration, self.dismiss)

    def _handle_click(self) -> None:
        """Handle click on toast."""
        if self._config.on_click:
            self._config.on_click()
        self.dismiss()

    def dismiss(self) -> None:
        """Dismiss the toast."""
        if self._dismiss_job:
            self.after_cancel(self._dismiss_job)
            self._dismiss_job = None

        if self._on_dismiss:
            self._on_dismiss(self)

        self.destroy()


class ToastManager:
    """
    Manages toast notifications for the application.

    Features:
    - Stack multiple toasts
    - Position in top-right corner
    - Auto-dismiss and removal
    """

    def __init__(self, parent: ctk.CTkBaseClass):
        self._parent = parent
        self._toasts: list[Toast] = []
        self._container: Optional[ctk.CTkFrame] = None

    def _ensure_container(self) -> ctk.CTkFrame:
        """Ensure the toast container exists."""
        if self._container is None or not self._container.winfo_exists():
            self._container = ctk.CTkFrame(self._parent, fg_color="transparent")
            self._container.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        return self._container

    def show(
        self,
        message: str,
        toast_type: ToastType = "info",
        duration: int = 4000,
        on_click: Optional[Callable] = None,
    ) -> Toast:
        """Show a toast notification."""
        container = self._ensure_container()

        config = ToastConfig(
            message=message, toast_type=toast_type, duration=duration, on_click=on_click
        )

        toast = Toast(container, config=config, on_dismiss=self._on_toast_dismiss)
        toast.pack(pady=5, fill="x")

        self._toasts.append(toast)
        return toast

    def _on_toast_dismiss(self, toast: Toast) -> None:
        """Handle toast dismissal."""
        if toast in self._toasts:
            self._toasts.remove(toast)

        # Clean up container if empty
        if not self._toasts and self._container:
            self._container.destroy()
            self._container = None

    def success(self, message: str, duration: int = 4000) -> Toast:
        """Show a success toast."""
        return self.show(message, "success", duration)

    def warning(self, message: str, duration: int = 4000) -> Toast:
        """Show a warning toast."""
        return self.show(message, "warning", duration)

    def error(self, message: str, duration: int = 5000) -> Toast:
        """Show an error toast."""
        return self.show(message, "error", duration)

    def info(self, message: str, duration: int = 4000) -> Toast:
        """Show an info toast."""
        return self.show(message, "info", duration)

    def clear_all(self) -> None:
        """Dismiss all toasts."""
        for toast in self._toasts.copy():
            toast.dismiss()
