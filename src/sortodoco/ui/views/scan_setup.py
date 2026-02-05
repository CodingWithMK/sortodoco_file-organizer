"""
Scan Setup view - Configure and initiate file scanning.
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog
from typing import Optional, Callable

from sortodoco.ui.views.base import BaseView
from sortodoco.ui.widgets.card import Card
from sortodoco.ui.theme import get_theme_manager
from sortodoco.ui.state import RootFolder


class ScanSetupView(BaseView):
    """
    Scan setup view for configuring folders and options.

    Features:
    - Root folders list with add/remove
    - Session options
    - Safety options
    - Scan/Plan buttons
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Optional[Callable[[str], None]] = None,
        on_plan: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(master, title="Scan Setup", on_navigate=on_navigate, **kwargs)

        self._on_plan = on_plan
        self._folder_widgets: list = []

        self._build_content()
        self._refresh_folder_list()

    def _build_content(self) -> None:
        """Build the scan setup content."""
        p = self._theme.palette

        self.content.grid_rowconfigure(0, weight=1)

        # Main container
        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.grid(row=0, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)

        # Folders section
        folders_header = ctk.CTkFrame(main, fg_color="transparent")
        folders_header.pack(fill="x", pady=(0, 8))

        folders_label = ctk.CTkLabel(
            folders_header,
            text="Folders to Organize",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=p.text_primary,
        )
        folders_label.pack(side="left")

        add_btn = ctk.CTkButton(
            folders_header,
            text="+ Add Folder",
            font=ctk.CTkFont(size=12),
            width=100,
            height=28,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._add_folder,
        )
        add_btn.pack(side="right")

        # Folders list card
        self._folders_card = Card(main, width=600)
        self._folders_card.pack(fill="x", pady=(0, 16))

        self._folders_list = ctk.CTkFrame(
            self._folders_card.content_frame, fg_color="transparent"
        )
        self._folders_list.pack(fill="x")

        # Options row
        options_row = ctk.CTkFrame(main, fg_color="transparent")
        options_row.pack(fill="x", pady=(0, 16))
        options_row.grid_columnconfigure((0, 1), weight=1)

        # Session Options Card
        self._session_card = Card(options_row, title="Session Options", width=280)
        self._session_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_session_options()

        # Safety Options Card
        self._safety_card = Card(options_row, title="Safety Options", width=280)
        self._safety_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._build_safety_options()

        # Action buttons
        button_frame = ctk.CTkFrame(main, fg_color="transparent")
        button_frame.pack(fill="x")

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=ctk.CTkFont(size=13),
            width=100,
            height=40,
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            command=lambda: self.navigate_to("dashboard"),
        )
        cancel_btn.pack(side="right", padx=8)

        # Plan button
        plan_btn = ctk.CTkButton(
            button_frame,
            text="Plan & Preview",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140,
            height=40,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._handle_plan,
        )
        plan_btn.pack(side="right")

    def _build_session_options(self) -> None:
        """Build session configuration options."""
        p = self._theme.palette
        content = self._session_card.content_frame
        opts = self._state.scan_options

        # Create session subfolders
        self._subfolder_var = ctk.BooleanVar(value=opts.create_session_subfolders)
        subfolder_cb = ctk.CTkCheckBox(
            content,
            text="Create session subfolders",
            font=ctk.CTkFont(size=12),
            variable=self._subfolder_var,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            command=self._update_options,
        )
        subfolder_cb.pack(anchor="w", pady=4)

        # Use timestamps
        self._timestamp_var = ctk.BooleanVar(value=opts.use_timestamps)
        timestamp_cb = ctk.CTkCheckBox(
            content,
            text="Use timestamps in names",
            font=ctk.CTkFont(size=12),
            variable=self._timestamp_var,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            command=self._update_options,
        )
        timestamp_cb.pack(anchor="w", pady=4)

        # Session prefix
        prefix_frame = ctk.CTkFrame(content, fg_color="transparent")
        prefix_frame.pack(fill="x", pady=8)

        prefix_label = ctk.CTkLabel(
            prefix_frame,
            text="Prefix:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        prefix_label.pack(side="left")

        self._prefix_entry = ctk.CTkEntry(
            prefix_frame,
            width=120,
            height=28,
            font=ctk.CTkFont(size=12),
            placeholder_text="session",
        )
        self._prefix_entry.insert(0, opts.session_prefix)
        self._prefix_entry.pack(side="right")

    def _build_safety_options(self) -> None:
        """Build safety configuration options."""
        p = self._theme.palette
        content = self._safety_card.content_frame
        opts = self._state.scan_options

        # Collision strategy
        collision_frame = ctk.CTkFrame(content, fg_color="transparent")
        collision_frame.pack(fill="x", pady=4)

        collision_label = ctk.CTkLabel(
            collision_frame,
            text="Collision:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        collision_label.pack(side="left")

        self._collision_var = ctk.StringVar(value=opts.collision_strategy)
        collision_menu = ctk.CTkOptionMenu(
            collision_frame,
            width=120,
            height=28,
            values=["rename", "skip", "overwrite"],
            variable=self._collision_var,
            font=ctk.CTkFont(size=12),
            fg_color=p.bg_tertiary,
            button_color=p.border,
            button_hover_color=p.text_muted,
            command=lambda v: self._update_options(),
        )
        collision_menu.pack(side="right")

        # Risk threshold
        risk_frame = ctk.CTkFrame(content, fg_color="transparent")
        risk_frame.pack(fill="x", pady=8)

        risk_label = ctk.CTkLabel(
            risk_frame,
            text="Risk threshold:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        risk_label.pack(side="left")

        self._risk_var = ctk.StringVar(value=opts.risk_threshold)
        risk_menu = ctk.CTkOptionMenu(
            risk_frame,
            width=100,
            height=28,
            values=["low", "medium", "high"],
            variable=self._risk_var,
            font=ctk.CTkFont(size=12),
            fg_color=p.bg_tertiary,
            button_color=p.border,
            button_hover_color=p.text_muted,
            command=lambda v: self._update_options(),
        )
        risk_menu.pack(side="right")

        # Quarantine deletes
        self._quarantine_var = ctk.BooleanVar(value=opts.quarantine_deletes)
        quarantine_cb = ctk.CTkCheckBox(
            content,
            text="Quarantine deleted files",
            font=ctk.CTkFont(size=12),
            variable=self._quarantine_var,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            command=self._update_options,
        )
        quarantine_cb.pack(anchor="w", pady=4)

    def _refresh_folder_list(self) -> None:
        """Refresh the folders list display."""
        # Clear existing
        for widget in self._folder_widgets:
            widget.destroy()
        self._folder_widgets = []

        p = self._theme.palette
        folders = self._state.root_folders

        if not folders:
            # Add default Downloads folder if none
            downloads = Path.home() / "Downloads"
            if downloads.exists():
                self._state.add_root_folder(downloads)
                folders = self._state.root_folders

        if not folders:
            empty_label = ctk.CTkLabel(
                self._folders_list,
                text="No folders added. Click 'Add Folder' to get started.",
                font=ctk.CTkFont(size=13),
                text_color=p.text_muted,
            )
            empty_label.pack(pady=16)
            self._folder_widgets.append(empty_label)
            return

        for rf in folders:
            row = self._create_folder_row(rf)
            row.pack(fill="x", pady=4)
            self._folder_widgets.append(row)

    def _create_folder_row(self, rf: RootFolder) -> ctk.CTkFrame:
        """Create a folder row widget."""
        p = self._theme.palette

        row = ctk.CTkFrame(self._folders_list, fg_color=p.bg_tertiary, corner_radius=6)

        # Checkbox
        enabled_var = ctk.BooleanVar(value=rf.enabled)
        cb = ctk.CTkCheckBox(
            row,
            text="",
            width=24,
            variable=enabled_var,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            command=lambda path=rf.path: self._state.toggle_root_folder(path),
        )
        cb.pack(side="left", padx=8, pady=8)

        # Path
        path_label = ctk.CTkLabel(
            row,
            text=str(rf.path),
            font=ctk.CTkFont(size=12),
            text_color=p.text_primary,
            anchor="w",
        )
        path_label.pack(side="left", fill="x", expand=True, padx=4)

        # Last scanned
        if rf.last_scanned:
            last_text = rf.last_scanned.strftime("%b %d")
        else:
            last_text = "Never"

        last_label = ctk.CTkLabel(
            row,
            text=f"Last: {last_text}",
            font=ctk.CTkFont(size=11),
            text_color=p.text_muted,
            width=80,
        )
        last_label.pack(side="left", padx=8)

        # Remove button
        remove_btn = ctk.CTkButton(
            row,
            text="×",
            width=28,
            height=28,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=p.error,
            text_color=p.text_secondary,
            command=lambda path=rf.path: self._remove_folder(path),
        )
        remove_btn.pack(side="right", padx=4, pady=4)

        return row

    def _add_folder(self) -> None:
        """Add a new folder via file dialog."""
        folder = filedialog.askdirectory(
            title="Select Folder to Organize", initialdir=Path.home()
        )
        if folder:
            self._state.add_root_folder(Path(folder))
            self._refresh_folder_list()

    def _remove_folder(self, path: Path) -> None:
        """Remove a folder from the list."""
        self._state.remove_root_folder(path)
        self._refresh_folder_list()

    def _update_options(self) -> None:
        """Update scan options from form values."""
        self._state.update_scan_option(
            "create_session_subfolders", self._subfolder_var.get()
        )
        self._state.update_scan_option("use_timestamps", self._timestamp_var.get())
        self._state.update_scan_option("session_prefix", self._prefix_entry.get())
        self._state.update_scan_option("collision_strategy", self._collision_var.get())
        self._state.update_scan_option("risk_threshold", self._risk_var.get())
        self._state.update_scan_option("quarantine_deletes", self._quarantine_var.get())

    def _handle_plan(self) -> None:
        """Handle plan button click."""
        # Update options first
        self._update_options()

        # Call the plan callback
        if self._on_plan:
            self._on_plan()
        else:
            # Default: navigate to plan preview
            self.navigate_to("plan_preview")

    def refresh(self) -> None:
        """Refresh the view."""
        self._refresh_folder_list()

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes - rebuild content with new colors."""
        super()._on_theme_change(palette)
        # Rebuild content to apply new theme colors to all widgets
        for widget in self.content.winfo_children():
            widget.destroy()
        self._build_content()
        self._refresh_folder_list()
