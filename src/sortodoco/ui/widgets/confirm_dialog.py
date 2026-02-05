"""
Confirmation dialog widget.
"""

import customtkinter as ctk
from typing import Optional, Callable

from sortodoco.ui.theme import get_theme_manager


class ConfirmDialog(ctk.CTkToplevel):
    """
    A modal confirmation dialog.

    Features:
    - Title and message
    - Confirm and Cancel buttons
    - Optional destructive styling
    - Keyboard shortcuts (Enter/Escape)
    """

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        title: str = "Confirm",
        message: str = "Are you sure?",
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        destructive: bool = False,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

        theme = get_theme_manager()
        p = theme.palette

        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._result: Optional[bool] = None

        # Window setup
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - 400) // 2
        y = parent_y + (parent_h - 180) // 2
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=p.bg_primary)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=p.text_primary,
        )
        title_label.grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")

        # Message
        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=p.text_secondary,
            wraplength=350,
            justify="left",
        )
        message_label.grid(row=1, column=0, padx=24, pady=8, sticky="nw")

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=24, pady=24, sticky="e")

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=cancel_text,
            width=100,
            font=ctk.CTkFont(size=13),
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            command=self._handle_cancel,
        )
        cancel_btn.pack(side="left", padx=(0, 8))

        # Confirm button
        confirm_color = p.error if destructive else p.accent
        confirm_hover = "#DC2626" if destructive else p.accent_hover

        confirm_btn = ctk.CTkButton(
            button_frame,
            text=confirm_text,
            width=100,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=confirm_color,
            hover_color=confirm_hover,
            text_color="#FFFFFF",
            command=self._handle_confirm,
        )
        confirm_btn.pack(side="left")

        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self._handle_confirm())
        self.bind("<Escape>", lambda e: self._handle_cancel())

        # Focus on cancel button for safety
        cancel_btn.focus_set()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._handle_cancel)

    def _handle_confirm(self) -> None:
        """Handle confirm action."""
        self._result = True
        if self._on_confirm:
            self._on_confirm()
        self.destroy()

    def _handle_cancel(self) -> None:
        """Handle cancel action."""
        self._result = False
        if self._on_cancel:
            self._on_cancel()
        self.destroy()

    @property
    def result(self) -> Optional[bool]:
        """Get dialog result after it's closed."""
        return self._result


def show_confirm_dialog(
    parent: ctk.CTkBaseClass,
    title: str = "Confirm",
    message: str = "Are you sure?",
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    destructive: bool = False,
) -> bool:
    """
    Show a confirmation dialog and wait for result.

    Returns:
        True if confirmed, False if cancelled
    """
    result = [False]

    def on_confirm():
        result[0] = True

    dialog = ConfirmDialog(
        parent,
        title=title,
        message=message,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        destructive=destructive,
        on_confirm=on_confirm,
    )

    dialog.wait_window()
    return result[0]
