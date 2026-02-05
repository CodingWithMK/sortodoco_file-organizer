"""
Data table widget for displaying operations and other tabular data.
"""

import customtkinter as ctk
from typing import Optional, Callable, Any
from dataclasses import dataclass

from sortodoco.ui.theme import get_theme_manager


@dataclass
class TableColumn:
    """Definition of a table column."""

    key: str
    header: str
    width: int = 100
    anchor: str = "w"
    sortable: bool = True


class DataTable(ctk.CTkFrame):
    """
    A scrollable data table widget.

    Features:
    - Column headers with sorting
    - Row selection (checkbox)
    - Scrollable content
    - Pagination (optional)
    - Row click callback
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        columns: list[TableColumn],
        data: list[dict] = None,
        on_row_select: Optional[Callable[[int, bool], None]] = None,
        on_row_click: Optional[Callable[[int, dict], None]] = None,
        show_checkboxes: bool = True,
        height: int = 400,
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette

        super().__init__(
            master,
            corner_radius=8,
            fg_color=p.bg_secondary,
            border_width=1,
            border_color=p.border,
            **kwargs,
        )

        self._theme = theme
        self._columns = columns
        self._data = data or []
        self._on_row_select = on_row_select
        self._on_row_click = on_row_click
        self._show_checkboxes = show_checkboxes
        self._selected_rows: set[int] = set()
        self._row_widgets: list[dict] = []
        self._sort_column: Optional[str] = None
        self._sort_ascending: bool = True

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header row
        self._header_frame = ctk.CTkFrame(self, fg_color=p.bg_tertiary, corner_radius=0)
        self._header_frame.grid(row=0, column=0, sticky="ew")
        self._build_header()

        # Scrollable content
        self._scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=height, corner_radius=0
        )
        self._scroll_frame.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)

        # Build initial content
        if self._data:
            self._build_rows()

        # Subscribe to theme changes
        theme.subscribe(self._on_theme_change)

    def _build_header(self) -> None:
        """Build the header row."""
        p = self._theme.palette

        col_index = 0

        # Checkbox column
        if self._show_checkboxes:
            self._select_all_var = ctk.BooleanVar(value=False)
            self._select_all_cb = ctk.CTkCheckBox(
                self._header_frame,
                text="",
                width=30,
                variable=self._select_all_var,
                command=self._toggle_all,
                fg_color=p.accent,
                hover_color=p.accent_hover,
            )
            self._select_all_cb.grid(row=0, column=col_index, padx=8, pady=8)
            col_index += 1

        # Data columns
        for column in self._columns:
            header_btn = ctk.CTkButton(
                self._header_frame,
                text=column.header,
                width=column.width,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                hover_color=p.bg_secondary,
                text_color=p.text_primary,
                anchor=column.anchor,
                command=lambda c=column: self._sort_by(c) if c.sortable else None,
            )
            header_btn.grid(row=0, column=col_index, padx=4, pady=8, sticky="ew")
            self._header_frame.grid_columnconfigure(
                col_index, weight=1, minsize=column.width
            )
            col_index += 1

    def _build_rows(self) -> None:
        """Build all data rows."""
        # Clear existing rows
        for widget_dict in self._row_widgets:
            for widget in widget_dict.values():
                if hasattr(widget, "destroy"):
                    widget.destroy()
        self._row_widgets = []

        p = self._theme.palette

        for row_idx, row_data in enumerate(self._data):
            row_widgets = self._build_row(row_idx, row_data)
            self._row_widgets.append(row_widgets)

    def _build_row(self, row_idx: int, row_data: dict) -> dict:
        """Build a single data row."""
        p = self._theme.palette

        # Row frame
        row_bg = p.bg_primary if row_idx % 2 == 0 else p.bg_secondary
        row_frame = ctk.CTkFrame(self._scroll_frame, fg_color=row_bg, corner_radius=0)
        row_frame.pack(fill="x", pady=1)
        row_frame.bind(
            "<Enter>", lambda e, rf=row_frame: rf.configure(fg_color=p.bg_tertiary)
        )
        row_frame.bind(
            "<Leave>", lambda e, rf=row_frame, bg=row_bg: rf.configure(fg_color=bg)
        )
        row_frame.bind("<Button-1>", lambda e, idx=row_idx: self._handle_row_click(idx))

        widgets = {"frame": row_frame}
        col_index = 0

        # Checkbox
        if self._show_checkboxes:
            cb_var = ctk.BooleanVar(value=row_idx in self._selected_rows)
            cb = ctk.CTkCheckBox(
                row_frame,
                text="",
                width=30,
                variable=cb_var,
                command=lambda idx=row_idx, var=cb_var: self._toggle_row(
                    idx, var.get()
                ),
                fg_color=p.accent,
                hover_color=p.accent_hover,
            )
            cb.grid(row=0, column=col_index, padx=8, pady=6)
            widgets["checkbox"] = cb
            widgets["cb_var"] = cb_var
            col_index += 1

        # Data columns
        for column in self._columns:
            value = row_data.get(column.key, "")

            # Handle custom renderers (if value is a widget factory)
            if callable(value):
                cell_widget = value(row_frame)
            else:
                cell_widget = ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    font=ctk.CTkFont(size=12),
                    text_color=p.text_primary,
                    anchor=column.anchor,
                    width=column.width,
                )

            cell_widget.grid(row=0, column=col_index, padx=4, pady=6, sticky="ew")
            cell_widget.bind(
                "<Button-1>", lambda e, idx=row_idx: self._handle_row_click(idx)
            )
            row_frame.grid_columnconfigure(col_index, weight=1, minsize=column.width)

            widgets[column.key] = cell_widget
            col_index += 1

        return widgets

    def _toggle_row(self, row_idx: int, selected: bool) -> None:
        """Toggle row selection."""
        if selected:
            self._selected_rows.add(row_idx)
        else:
            self._selected_rows.discard(row_idx)

        # Update select all checkbox
        if self._show_checkboxes:
            all_selected = len(self._selected_rows) == len(self._data)
            self._select_all_var.set(all_selected)

        if self._on_row_select:
            self._on_row_select(row_idx, selected)

    def _toggle_all(self) -> None:
        """Toggle all row selections."""
        select_all = self._select_all_var.get()

        if select_all:
            self._selected_rows = set(range(len(self._data)))
        else:
            self._selected_rows = set()

        # Update checkboxes
        for idx, row_widgets in enumerate(self._row_widgets):
            if "cb_var" in row_widgets:
                row_widgets["cb_var"].set(select_all)

        if self._on_row_select:
            for idx in range(len(self._data)):
                self._on_row_select(idx, select_all)

    def _handle_row_click(self, row_idx: int) -> None:
        """Handle row click."""
        if self._on_row_click and row_idx < len(self._data):
            self._on_row_click(row_idx, self._data[row_idx])

    def _sort_by(self, column: TableColumn) -> None:
        """Sort table by column."""
        if self._sort_column == column.key:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = column.key
            self._sort_ascending = True

        self._data.sort(
            key=lambda x: str(x.get(column.key, "")), reverse=not self._sort_ascending
        )
        self._build_rows()

    def set_data(self, data: list[dict]) -> None:
        """Update the table data."""
        self._data = data
        self._selected_rows = set()
        self._build_rows()

    def get_selected_indices(self) -> list[int]:
        """Get indices of selected rows."""
        return sorted(self._selected_rows)

    def get_selected_data(self) -> list[dict]:
        """Get data of selected rows."""
        return [
            self._data[i] for i in sorted(self._selected_rows) if i < len(self._data)
        ]

    def select_row(self, row_idx: int) -> None:
        """Select a row."""
        if row_idx < len(self._row_widgets):
            self._selected_rows.add(row_idx)
            if "cb_var" in self._row_widgets[row_idx]:
                self._row_widgets[row_idx]["cb_var"].set(True)

    def deselect_row(self, row_idx: int) -> None:
        """Deselect a row."""
        if row_idx < len(self._row_widgets):
            self._selected_rows.discard(row_idx)
            if "cb_var" in self._row_widgets[row_idx]:
                self._row_widgets[row_idx]["cb_var"].set(False)

    def select_all(self) -> None:
        """Select all rows."""
        self._select_all_var.set(True)
        self._toggle_all()

    def deselect_all(self) -> None:
        """Deselect all rows."""
        self._select_all_var.set(False)
        self._toggle_all()

    def _on_theme_change(self, palette) -> None:
        """Handle theme changes."""
        self.configure(fg_color=palette.bg_secondary, border_color=palette.border)
        self._header_frame.configure(fg_color=palette.bg_tertiary)
        self._build_rows()

    def destroy(self):
        """Clean up theme subscription on destroy."""
        self._theme.unsubscribe(self._on_theme_change)
        super().destroy()
