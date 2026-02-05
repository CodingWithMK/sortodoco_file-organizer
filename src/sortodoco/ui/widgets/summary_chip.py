"""
Summary chip widgets for displaying category counts.
"""

import customtkinter as ctk
from typing import Optional

from sortodoco.ui.theme import get_theme_manager, CATEGORY_COLORS, CATEGORY_ICONS


class SummaryChip(ctk.CTkFrame):
    """
    A chip showing category name and count.

    Example: [📷 Images: 12]
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        category: str,
        count: int,
        show_icon: bool = True,
        **kwargs,
    ):
        theme = get_theme_manager()
        p = theme.palette

        color = CATEGORY_COLORS.get(category, "#6B7280")

        super().__init__(master, corner_radius=16, fg_color=color, **kwargs)

        self._category = category
        self._count = count

        # Build content
        icon = CATEGORY_ICONS.get(category, "📁") if show_icon else ""
        text = f"{icon} {category}: {count}" if icon else f"{category}: {count}"

        self._label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFFFFF",
        )
        self._label.pack(padx=12, pady=6)

    def set_count(self, count: int) -> None:
        """Update the count."""
        self._count = count
        icon = CATEGORY_ICONS.get(self._category, "📁")
        self._label.configure(text=f"{icon} {self._category}: {count}")


class SummaryChipBar(ctk.CTkFrame):
    """
    A horizontal bar of summary chips for plan overview.

    Shows counts per category in a visually appealing way.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        summary: Optional[dict[str, int]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._chips: dict[str, SummaryChip] = {}

        if summary:
            self.set_summary(summary)

    def set_summary(self, summary: dict[str, int]) -> None:
        """Update the summary display."""
        # Clear existing chips
        for chip in self._chips.values():
            chip.destroy()
        self._chips = {}

        # Create new chips (only for non-zero counts)
        for category, count in summary.items():
            if count > 0:
                chip = SummaryChip(self, category=category, count=count)
                chip.pack(side="left", padx=4, pady=4)
                self._chips[category] = chip

    def get_total_count(self) -> int:
        """Get total count across all categories."""
        return sum(chip._count for chip in self._chips.values())
