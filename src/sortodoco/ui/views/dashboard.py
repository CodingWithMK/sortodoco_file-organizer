"""
Dashboard view - Quick status and actions.
"""

import customtkinter as ctk
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

from sortodoco.ui.views.base import BaseView
from sortodoco.ui.widgets.card import Card
from sortodoco.ui.theme import get_theme_manager


class DashboardView(BaseView):
    """
    Dashboard view showing quick status and actions.

    Features:
    - Last session summary card
    - Quick actions card
    - Disk health card
    - Recent activity list
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, title="Dashboard", on_navigate=on_navigate, **kwargs)

        self._build_content()

    def _build_content(self) -> None:
        """Build the dashboard content."""
        p = self._theme.palette

        # Top row - 3 cards
        top_row = ctk.CTkFrame(self.content, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        top_row.grid_columnconfigure((0, 1, 2), weight=1)

        # Last Session Card
        self._last_session_card = Card(top_row, title="Last Session", width=280)
        self._last_session_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_last_session_content()

        # Quick Actions Card
        self._actions_card = Card(top_row, title="Quick Actions", width=280)
        self._actions_card.grid(row=0, column=1, sticky="nsew", padx=8)
        self._build_quick_actions()

        # Disk Health Card
        self._health_card = Card(top_row, title="Folder Status", width=280)
        self._health_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        self._build_disk_health()

        # Recent Activity Card
        self._activity_card = Card(
            self.content,
            title="Recent Activity",
            subtitle="Your last 5 organization sessions",
        )
        self._activity_card.grid(row=1, column=0, sticky="nsew", pady=(0, 16))
        self._build_recent_activity()

        # Welcome message (if no sessions yet)
        self._build_welcome_message()

    def _build_last_session_content(self) -> None:
        """Build last session summary."""
        p = self._theme.palette
        content = self._last_session_card.content_frame

        last_session = self._state.last_session

        if last_session:
            # Timestamp
            ts_label = ctk.CTkLabel(
                content,
                text=last_session.timestamp.strftime("%b %d, %H:%M"),
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=p.text_primary,
            )
            ts_label.pack(anchor="w", pady=(0, 4))

            # Stats
            stats_text = f"{last_session.moved} files organized"
            if last_session.errors > 0:
                stats_text += f"\n{last_session.errors} errors"
            else:
                stats_text += "\n0 errors"

            stats_label = ctk.CTkLabel(
                content,
                text=stats_text,
                font=ctk.CTkFont(size=13),
                text_color=p.text_secondary,
                justify="left",
            )
            stats_label.pack(anchor="w")
        else:
            # No sessions yet
            empty_label = ctk.CTkLabel(
                content,
                text="No sessions yet",
                font=ctk.CTkFont(size=13),
                text_color=p.text_muted,
            )
            empty_label.pack(anchor="w")

    def _build_quick_actions(self) -> None:
        """Build quick action buttons."""
        p = self._theme.palette
        content = self._actions_card.content_frame

        # Plan Now button
        plan_btn = ctk.CTkButton(
            content,
            text="Plan Now",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            height=36,
            command=lambda: self.navigate_to("scan_setup"),
        )
        plan_btn.pack(fill="x", pady=(0, 8))

        # View History button
        history_btn = ctk.CTkButton(
            content,
            text="View History",
            font=ctk.CTkFont(size=13),
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            height=36,
            command=lambda: self.navigate_to("history"),
        )
        history_btn.pack(fill="x", pady=(0, 8))

        # Settings button
        settings_btn = ctk.CTkButton(
            content,
            text="Settings",
            font=ctk.CTkFont(size=13),
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            height=36,
            command=lambda: self.navigate_to("settings"),
        )
        settings_btn.pack(fill="x")

    def _build_disk_health(self) -> None:
        """Build disk/folder health status."""
        p = self._theme.palette
        content = self._health_card.content_frame

        # Check common folders
        folders = [
            ("Downloads", Path.home() / "Downloads"),
            ("Desktop", Path.home() / "Desktop"),
            ("Documents", Path.home() / "Documents"),
        ]

        for name, path in folders:
            status_frame = ctk.CTkFrame(content, fg_color="transparent")
            status_frame.pack(fill="x", pady=2)

            exists = path.exists()
            icon = "✓" if exists else "✗"
            color = p.success if exists else p.error

            icon_label = ctk.CTkLabel(
                status_frame,
                text=icon,
                font=ctk.CTkFont(size=12),
                text_color=color,
                width=20,
            )
            icon_label.pack(side="left")

            name_label = ctk.CTkLabel(
                status_frame,
                text=name,
                font=ctk.CTkFont(size=12),
                text_color=p.text_primary,
            )
            name_label.pack(side="left")

            status_text = "OK" if exists else "Not found"
            status_label = ctk.CTkLabel(
                status_frame,
                text=status_text,
                font=ctk.CTkFont(size=11),
                text_color=p.text_secondary,
            )
            status_label.pack(side="right")

    def _build_recent_activity(self) -> None:
        """Build recent activity list."""
        p = self._theme.palette
        content = self._activity_card.content_frame

        sessions = self._state.sessions[:5]  # Last 5 sessions

        if sessions:
            for session in sessions:
                row = ctk.CTkFrame(content, fg_color="transparent")
                row.pack(fill="x", pady=4)

                # Bullet
                bullet = ctk.CTkLabel(
                    row,
                    text="●",
                    font=ctk.CTkFont(size=10),
                    text_color=p.accent,
                    width=20,
                )
                bullet.pack(side="left")

                # Timestamp
                ts = ctk.CTkLabel(
                    row,
                    text=session.timestamp.strftime("%b %d, %H:%M"),
                    font=ctk.CTkFont(size=12),
                    text_color=p.text_secondary,
                    width=100,
                )
                ts.pack(side="left")

                # Description
                desc = f"{session.moved} files organized"
                desc_label = ctk.CTkLabel(
                    row, text=desc, font=ctk.CTkFont(size=12), text_color=p.text_primary
                )
                desc_label.pack(side="left", padx=8)

                # Status
                status = (
                    "Success" if session.errors == 0 else f"{session.errors} errors"
                )
                status_color = p.success if session.errors == 0 else p.warning
                status_label = ctk.CTkLabel(
                    row, text=status, font=ctk.CTkFont(size=11), text_color=status_color
                )
                status_label.pack(side="right")
        else:
            # No sessions
            empty_label = ctk.CTkLabel(
                content,
                text="No recent activity. Start by clicking 'Plan Now' above.",
                font=ctk.CTkFont(size=13),
                text_color=p.text_muted,
            )
            empty_label.pack(pady=20)

    def _build_welcome_message(self) -> None:
        """Build welcome message for first-time users."""
        if not self._state.sessions:
            p = self._theme.palette

            welcome_card = Card(
                self.content,
                title="Welcome to SortoDoco!",
                subtitle="Your local-first file organizer",
            )
            welcome_card.grid(row=2, column=0, sticky="ew")

            content = welcome_card.content_frame

            steps = [
                "1. Click 'Plan Now' to select folders to organize",
                "2. Review the plan before applying",
                "3. Apply to organize your files safely",
            ]

            for step in steps:
                step_label = ctk.CTkLabel(
                    content,
                    text=step,
                    font=ctk.CTkFont(size=13),
                    text_color=p.text_secondary,
                    anchor="w",
                )
                step_label.pack(anchor="w", pady=2)

    def refresh(self) -> None:
        """Refresh the dashboard."""
        # Clear and rebuild content
        for widget in self.content.winfo_children():
            widget.destroy()
        self._build_content()

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes - rebuild content with new colors."""
        super()._on_theme_change(palette)
        # Rebuild content to apply new theme colors to all widgets
        self.refresh()
