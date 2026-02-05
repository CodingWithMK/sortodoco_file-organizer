"""
Plan Preview view - Review and apply organization plan.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional, Callable

from sortodoco.ui.views.base import BaseView
from sortodoco.ui.widgets.card import Card
from sortodoco.ui.widgets.summary_chip import SummaryChipBar
from sortodoco.ui.widgets.data_table import DataTable, TableColumn
from sortodoco.ui.widgets.badge import CategoryBadge, RiskBadge
from sortodoco.ui.widgets.confirm_dialog import show_confirm_dialog
from sortodoco.ui.theme import get_theme_manager, CATEGORY_ICONS


class PlanPreviewView(BaseView):
    """
    Plan preview view for reviewing and applying organization plans.

    Features:
    - Summary chips showing counts per category
    - Operations table with filtering
    - Details panel for selected operation
    - Apply/Export buttons
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Optional[Callable[[str], None]] = None,
        on_apply: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(
            master, title="Plan Preview", on_navigate=on_navigate, **kwargs
        )

        self._on_apply = on_apply
        self._selected_op_index: Optional[int] = None

        self._build_content()

    def _build_content(self) -> None:
        """Build the plan preview content."""
        p = self._theme.palette
        plan = self._state.current_plan

        self.content.grid_columnconfigure(0, weight=3)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        # Summary chips
        summary_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        summary_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        if plan:
            self._summary_bar = SummaryChipBar(summary_frame, summary=plan.summary)
            self._summary_bar.pack(side="left")

            # Session info
            session_label = ctk.CTkLabel(
                summary_frame,
                text=f"Session: {plan.session_ts}",
                font=ctk.CTkFont(size=12),
                text_color=p.text_secondary,
            )
            session_label.pack(side="right")
        else:
            no_plan_label = ctk.CTkLabel(
                summary_frame,
                text="No plan generated. Go to Scan Setup first.",
                font=ctk.CTkFont(size=14),
                text_color=p.text_muted,
            )
            no_plan_label.pack(side="left")

        # Left side - Operations table
        self._build_operations_panel()

        # Right side - Details panel
        self._build_details_panel()

        # Bottom - Action buttons
        self._build_action_buttons()

    def _build_operations_panel(self) -> None:
        """Build the operations table panel."""
        p = self._theme.palette
        plan = self._state.current_plan

        # Container
        ops_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        ops_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        ops_frame.grid_columnconfigure(0, weight=1)
        ops_frame.grid_rowconfigure(1, weight=1)

        # Filter bar
        filter_frame = ctk.CTkFrame(ops_frame, fg_color=p.bg_secondary, corner_radius=8)
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Search
        self._search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            filter_frame,
            width=200,
            height=32,
            placeholder_text="Search files...",
            textvariable=self._search_var,
            font=ctk.CTkFont(size=12),
        )
        search_entry.pack(side="left", padx=8, pady=8)
        self._search_var.trace_add("write", lambda *args: self._apply_filters())

        # Category filter
        categories = ["All Categories"] + list(CATEGORY_ICONS.keys())
        self._category_var = ctk.StringVar(value="All Categories")
        category_menu = ctk.CTkOptionMenu(
            filter_frame,
            width=140,
            height=32,
            values=categories,
            variable=self._category_var,
            font=ctk.CTkFont(size=12),
            fg_color=p.bg_tertiary,
            button_color=p.border,
            command=lambda v: self._apply_filters(),
        )
        category_menu.pack(side="left", padx=4, pady=8)

        # Operations table
        if plan and plan.ops:
            columns = [
                TableColumn(key="name", header="Filename", width=200),
                TableColumn(key="destination", header="Destination", width=200),
                TableColumn(key="category", header="Category", width=100),
                TableColumn(key="kind", header="Action", width=60),
            ]

            data = self._prepare_table_data(plan.ops)

            self._table = DataTable(
                ops_frame,
                columns=columns,
                data=data,
                on_row_select=self._on_row_select,
                on_row_click=self._on_row_click,
                show_checkboxes=True,
                height=400,
            )
            self._table.grid(row=1, column=0, sticky="nsew")

            # Select all by default
            self._table.select_all()
        else:
            empty_label = ctk.CTkLabel(
                ops_frame,
                text="No operations to display",
                font=ctk.CTkFont(size=14),
                text_color=p.text_muted,
            )
            empty_label.grid(row=1, column=0, pady=50)

    def _build_details_panel(self) -> None:
        """Build the details panel."""
        p = self._theme.palette

        self._details_card = Card(self.content, title="Details", width=300)
        self._details_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))

        # Details content (empty initially)
        self._details_content = self._details_card.content_frame

        empty_label = ctk.CTkLabel(
            self._details_content,
            text="Select an operation to view details",
            font=ctk.CTkFont(size=12),
            text_color=p.text_muted,
        )
        empty_label.pack(pady=20)

    def _build_action_buttons(self) -> None:
        """Build the action buttons."""
        p = self._theme.palette
        plan = self._state.current_plan

        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 0))

        # Export button
        export_btn = ctk.CTkButton(
            button_frame,
            text="Export Plan",
            font=ctk.CTkFont(size=13),
            width=120,
            height=40,
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            command=self._export_plan,
        )
        export_btn.pack(side="left")

        # Back button
        back_btn = ctk.CTkButton(
            button_frame,
            text="Back",
            font=ctk.CTkFont(size=13),
            width=100,
            height=40,
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            command=lambda: self.navigate_to("scan_setup"),
        )
        back_btn.pack(side="right", padx=8)

        # Apply button
        if plan and plan.ops:
            apply_btn = ctk.CTkButton(
                button_frame,
                text=f"Apply ({len(plan.ops)} ops)",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=140,
                height=40,
                fg_color=p.accent,
                hover_color=p.accent_hover,
                text_color="#FFFFFF",
                command=self._handle_apply,
            )
            apply_btn.pack(side="right")

    def _prepare_table_data(self, ops) -> list[dict]:
        """Prepare operations data for the table."""
        data = []
        for i, op in enumerate(ops):
            # Determine category from destination path
            category = "_Misc"
            if op.dst:
                parts = op.dst.parts
                for p in parts:
                    if p in CATEGORY_ICONS:
                        category = p
                        break

            data.append(
                {
                    "index": i,
                    "name": op.src.name,
                    "destination": str(op.dst.parent.name) if op.dst else "-",
                    "category": category,
                    "kind": op.kind.upper(),
                    "src": str(op.src),
                    "dst": str(op.dst) if op.dst else "-",
                }
            )
        return data

    def _on_row_select(self, row_idx: int, selected: bool) -> None:
        """Handle row selection change."""
        if selected:
            self._state.select_operation(row_idx)
        else:
            self._state.deselect_operation(row_idx)

    def _on_row_click(self, row_idx: int, row_data: dict) -> None:
        """Handle row click to show details."""
        self._selected_op_index = row_idx
        self._show_details(row_data)

    def _show_details(self, row_data: dict) -> None:
        """Show details for a selected operation."""
        p = self._theme.palette

        # Clear existing content
        for widget in self._details_content.winfo_children():
            widget.destroy()

        # Filename
        name_label = ctk.CTkLabel(
            self._details_content,
            text=row_data.get("name", ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=p.text_primary,
        )
        name_label.pack(anchor="w", pady=(0, 8))

        # Category badge
        category = row_data.get("category", "_Misc")
        badge = CategoryBadge(self._details_content, category=category)
        badge.pack(anchor="w", pady=(0, 12))

        # Source path
        src_title = ctk.CTkLabel(
            self._details_content,
            text="Source:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=p.text_secondary,
        )
        src_title.pack(anchor="w")

        src_path = ctk.CTkLabel(
            self._details_content,
            text=row_data.get("src", ""),
            font=ctk.CTkFont(size=11),
            text_color=p.text_primary,
            wraplength=260,
        )
        src_path.pack(anchor="w", pady=(0, 8))

        # Destination path
        dst_title = ctk.CTkLabel(
            self._details_content,
            text="Destination:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=p.text_secondary,
        )
        dst_title.pack(anchor="w")

        dst_path = ctk.CTkLabel(
            self._details_content,
            text=row_data.get("dst", ""),
            font=ctk.CTkFont(size=11),
            text_color=p.text_primary,
            wraplength=260,
        )
        dst_path.pack(anchor="w", pady=(0, 8))

        # Action
        action_title = ctk.CTkLabel(
            self._details_content,
            text="Action:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=p.text_secondary,
        )
        action_title.pack(anchor="w")

        action_label = ctk.CTkLabel(
            self._details_content,
            text=row_data.get("kind", "").capitalize(),
            font=ctk.CTkFont(size=11),
            text_color=p.accent,
        )
        action_label.pack(anchor="w")

    def _apply_filters(self) -> None:
        """Apply search and category filters."""
        if not hasattr(self, "_table"):
            return

        plan = self._state.current_plan
        if not plan:
            return

        search_text = self._search_var.get().lower()
        category_filter = self._category_var.get()

        # Filter operations
        filtered_data = []
        for i, op in enumerate(plan.ops):
            # Get category
            category = "_Misc"
            if op.dst:
                for p in op.dst.parts:
                    if p in CATEGORY_ICONS:
                        category = p
                        break

            # Apply filters
            if search_text and search_text not in op.src.name.lower():
                continue
            if category_filter != "All Categories" and category != category_filter:
                continue

            filtered_data.append(
                {
                    "index": i,
                    "name": op.src.name,
                    "destination": str(op.dst.parent.name) if op.dst else "-",
                    "category": category,
                    "kind": op.kind.upper(),
                    "src": str(op.src),
                    "dst": str(op.dst) if op.dst else "-",
                }
            )

        self._table.set_data(filtered_data)

    def _export_plan(self) -> None:
        """Export the current plan to a file."""
        from tkinter import filedialog
        import json

        plan = self._state.current_plan
        if not plan:
            return

        filepath = filedialog.asksaveasfilename(
            title="Export Plan",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"plan_{plan.session_ts}.json",
        )

        if filepath:
            export_data = {
                "session_ts": plan.session_ts,
                "summary": plan.summary,
                "operations": [
                    {"kind": op.kind, "src": str(op.src), "dst": str(op.dst)}
                    for op in plan.ops
                ],
            }
            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)

    def _handle_apply(self) -> None:
        """Handle apply button click."""
        plan = self._state.current_plan
        if not plan:
            return

        # Confirm dialog
        confirmed = show_confirm_dialog(
            self,
            title="Apply Plan",
            message=f"Are you sure you want to apply this plan?\n\nThis will move {len(plan.ops)} files.",
            confirm_text="Apply",
            cancel_text="Cancel",
        )

        if confirmed and self._on_apply:
            self._on_apply()

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
