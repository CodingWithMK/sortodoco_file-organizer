"""
Badge widgets - Status and category labels.
"""

import customtkinter as ctk
from typing import Optional

from sortodoco.ui.theme import (
    get_theme_manager,
    CATEGORY_COLORS,
    CATEGORY_ICONS,
    RISK_COLORS,
    RISK_ICONS,
)


class Badge(ctk.CTkFrame):
    """
    A badge/pill component for displaying labels.

    Features:
    - Colored background
    - Icon + text format
    - Pill shape (rounded)
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        text: str,
        icon: Optional[str] = None,
        color: str = "#6B7280",
        text_color: str = "#FFFFFF",
        **kwargs,
    ):
        super().__init__(master, corner_radius=12, fg_color=color, **kwargs)

        self._color = color
        self._text_color = text_color

        # Build content
        display_text = f"{icon} {text}" if icon else text

        self._label = ctk.CTkLabel(
            self,
            text=display_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=text_color,
        )
        self._label.pack(padx=8, pady=3)

    def set_text(self, text: str, icon: Optional[str] = None) -> None:
        """Update badge text."""
        display_text = f"{icon} {text}" if icon else text
        self._label.configure(text=display_text)

    def set_color(self, color: str) -> None:
        """Update badge color."""
        self._color = color
        self.configure(fg_color=color)


class CategoryBadge(Badge):
    """
    A badge for file categories (Images, Documents, etc.).
    Automatically uses category-specific colors and icons.
    """

    def __init__(
        self, master: ctk.CTkBaseClass, category: str, show_icon: bool = True, **kwargs
    ):
        color = CATEGORY_COLORS.get(category, "#6B7280")
        icon = CATEGORY_ICONS.get(category, "📁") if show_icon else None

        super().__init__(
            master,
            text=category,
            icon=icon,
            color=color,
            text_color="#FFFFFF",
            **kwargs,
        )

        self._category = category

    def set_category(self, category: str, show_icon: bool = True) -> None:
        """Update the category."""
        self._category = category
        color = CATEGORY_COLORS.get(category, "#6B7280")
        icon = CATEGORY_ICONS.get(category, "📁") if show_icon else None

        self.set_color(color)
        self.set_text(category, icon)


class RiskBadge(Badge):
    """
    A badge for risk levels (low, medium, high).
    Automatically uses risk-specific colors and icons.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        risk: str = "low",
        show_text: bool = False,
        **kwargs,
    ):
        color = RISK_COLORS.get(risk, "#6B7280")
        icon = RISK_ICONS.get(risk, "⚪")
        text = risk.capitalize() if show_text else ""

        super().__init__(
            master, text=text, icon=icon, color=color, text_color="#FFFFFF", **kwargs
        )

        self._risk = risk

        # Make smaller if no text
        if not show_text:
            self._label.configure(font=ctk.CTkFont(size=12))
            self._label.pack_configure(padx=4, pady=2)

    def set_risk(self, risk: str, show_text: bool = False) -> None:
        """Update the risk level."""
        self._risk = risk
        color = RISK_COLORS.get(risk, "#6B7280")
        icon = RISK_ICONS.get(risk, "⚪")
        text = risk.capitalize() if show_text else ""

        self.set_color(color)
        self.set_text(text, icon)
