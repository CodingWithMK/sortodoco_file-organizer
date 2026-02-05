"""
History view - Browse past organization sessions.
"""

import customtkinter as ctk
from typing import Optional, Callable
from datetime import datetime

from sortodoco.ui.views.base import BaseView
from sortodoco.ui.widgets.card import Card
from sortodoco.ui.widgets.data_table import DataTable, TableColumn
from sortodoco.ui.theme import get_theme_manager


class HistoryView(BaseView):
    """
    History view for browsing past sessions.

    Features:
    - Sessions table
    - Session details
    - Export reports
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, title="History", on_navigate=on_navigate, **kwargs)

        self._build_content()

    def _build_content(self) -> None:
        """Build the history content."""
        p = self._theme.palette

        self.content.grid_columnconfigure(0, weight=2)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Left - Sessions table
        sessions_card = Card(self.content, title="Sessions")
        sessions_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_sessions_table(sessions_card.content_frame)

        # Right - Session details
        self._details_card = Card(self.content, title="Session Details")
        self._details_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._build_details_panel(self._details_card.content_frame)

    def _build_sessions_table(self, content: ctk.CTkFrame) -> None:
        """Build sessions table."""
        p = self._theme.palette
        sessions = self._state.sessions

        if not sessions:
            # No sessions yet
            empty_frame = ctk.CTkFrame(content, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True)

            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No sessions yet.\n\nOrganize some files to see your history here.",
                font=ctk.CTkFont(size=14),
                text_color=p.text_muted,
                justify="center",
            )
            empty_label.pack(expand=True)
            return

        # Build table
        columns = [
            TableColumn(key="date", header="Date", width=100),
            TableColumn(key="time", header="Time", width=80),
            TableColumn(key="files", header="Files", width=60),
            TableColumn(key="status", header="Status", width=80),
        ]

        data = []
        for i, session in enumerate(sessions):
            data.append(
                {
                    "index": i,
                    "date": session.timestamp.strftime("%b %d, %Y"),
                    "time": session.timestamp.strftime("%H:%M"),
                    "files": str(session.moved),
                    "status": "Success"
                    if session.errors == 0
                    else f"{session.errors} errors",
                }
            )

        self._table = DataTable(
            content,
            columns=columns,
            data=data,
            on_row_click=self._on_session_click,
            show_checkboxes=False,
            height=400,
        )
        self._table.pack(fill="both", expand=True)

    def _build_details_panel(self, content: ctk.CTkFrame) -> None:
        """Build details panel."""
        p = self._theme.palette

        self._details_content = content

        empty_label = ctk.CTkLabel(
            content,
            text="Select a session to view details",
            font=ctk.CTkFont(size=12),
            text_color=p.text_muted,
        )
        empty_label.pack(pady=20)

    def _on_session_click(self, row_idx: int, row_data: dict) -> None:
        """Handle session selection."""
        sessions = self._state.sessions
        if row_idx >= len(sessions):
            return

        session = sessions[row_idx]
        self._show_session_details(session)

    def _show_session_details(self, session) -> None:
        """Show details for a session."""
        p = self._theme.palette

        # Clear existing content
        for widget in self._details_content.winfo_children():
            widget.destroy()

        # Session ID
        id_label = ctk.CTkLabel(
            self._details_content,
            text=session.session_id,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=p.text_primary,
        )
        id_label.pack(anchor="w", pady=(0, 8))

        # Timestamp
        ts_label = ctk.CTkLabel(
            self._details_content,
            text=session.timestamp.strftime("%B %d, %Y at %H:%M:%S"),
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        ts_label.pack(anchor="w", pady=(0, 12))

        # Stats
        stats = [
            ("Total operations", session.total_ops),
            ("Files moved", session.moved),
            ("Files skipped", session.skipped),
            ("Errors", session.errors),
        ]

        for label, value in stats:
            row = ctk.CTkFrame(self._details_content, fg_color="transparent")
            row.pack(fill="x", pady=2)

            label_widget = ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=ctk.CTkFont(size=12),
                text_color=p.text_secondary,
            )
            label_widget.pack(side="left")

            value_color = p.error if label == "Errors" and value > 0 else p.text_primary
            value_widget = ctk.CTkLabel(
                row,
                text=str(value),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=value_color,
            )
            value_widget.pack(side="right")

        # Success rate
        rate = session.success_rate
        rate_color = p.success if rate == 100 else (p.warning if rate > 80 else p.error)

        rate_row = ctk.CTkFrame(self._details_content, fg_color="transparent")
        rate_row.pack(fill="x", pady=(8, 0))

        rate_label = ctk.CTkLabel(
            rate_row,
            text="Success rate:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        rate_label.pack(side="left")

        rate_value = ctk.CTkLabel(
            rate_row,
            text=f"{rate:.1f}%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=rate_color,
        )
        rate_value.pack(side="right")

        # Root folders
        if session.root_folders:
            roots_label = ctk.CTkLabel(
                self._details_content,
                text="\nFolders organized:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=p.text_primary,
            )
            roots_label.pack(anchor="w", pady=(12, 4))

            for folder in session.root_folders:
                folder_label = ctk.CTkLabel(
                    self._details_content,
                    text=f"  • {folder}",
                    font=ctk.CTkFont(size=11),
                    text_color=p.text_secondary,
                )
                folder_label.pack(anchor="w")

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
