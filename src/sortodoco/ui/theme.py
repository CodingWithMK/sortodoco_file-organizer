"""
Theme management for SortoDoco GUI.
Supports Light, Dark, and System (auto-detect) modes with orange accents.
"""

from dataclasses import dataclass
from typing import Literal, Callable
import darkdetect
import customtkinter as ctk

ThemeMode = Literal["light", "dark", "system"]


@dataclass(frozen=True)
class ColorPalette:
    """Color palette for a theme."""

    # Backgrounds
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str

    # Text
    text_primary: str
    text_secondary: str
    text_muted: str

    # Accent (Orange)
    accent: str
    accent_hover: str
    accent_light: str

    # Status colors
    success: str
    warning: str
    error: str

    # Borders
    border: str

    # Sidebar
    sidebar_bg: str
    sidebar_hover: str
    sidebar_active: str


# Light mode palette
LIGHT_PALETTE = ColorPalette(
    bg_primary="#FFFFFF",
    bg_secondary="#F5F5F5",
    bg_tertiary="#E8E8E8",
    text_primary="#1A1A1A",
    text_secondary="#666666",
    text_muted="#999999",
    accent="#FF6B00",
    accent_hover="#E55D00",
    accent_light="#FFF0E6",
    success="#22C55E",
    warning="#F59E0B",
    error="#EF4444",
    border="#E0E0E0",
    sidebar_bg="#F0F0F0",
    sidebar_hover="#E5E5E5",
    sidebar_active="#FFE5D4",
)

# Dark mode palette
DARK_PALETTE = ColorPalette(
    bg_primary="#1A1A1A",
    bg_secondary="#242424",
    bg_tertiary="#2E2E2E",
    text_primary="#FFFFFF",
    text_secondary="#A0A0A0",
    text_muted="#666666",
    accent="#FF7A1A",
    accent_hover="#FF8C33",
    accent_light="#2D2013",
    success="#22C55E",
    warning="#F59E0B",
    error="#EF4444",
    border="#3A3A3A",
    sidebar_bg="#1E1E1E",
    sidebar_hover="#2A2A2A",
    sidebar_active="#3D2810",
)


@dataclass
class FontConfig:
    """Font configuration."""

    family: str = "Segoe UI"
    h1_size: int = 24
    h2_size: int = 18
    h3_size: int = 14
    body_size: int = 13
    small_size: int = 11


@dataclass
class SpacingConfig:
    """Spacing configuration."""

    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass
class StyleConfig:
    """Style configuration."""

    border_radius_card: int = 8
    border_radius_button: int = 6
    border_radius_input: int = 4
    sidebar_width: int = 240


class ThemeManager:
    """
    Manages application theming with light, dark, and system modes.
    Provides color palettes and notifies observers on theme changes.
    """

    def __init__(self, initial_mode: ThemeMode = "system"):
        self._mode: ThemeMode = initial_mode
        self._observers: list[Callable[[ColorPalette], None]] = []
        self._fonts = FontConfig()
        self._spacing = SpacingConfig()
        self._style = StyleConfig()

        # Apply initial theme
        self._apply_theme()

    @property
    def mode(self) -> ThemeMode:
        """Current theme mode."""
        return self._mode

    @property
    def palette(self) -> ColorPalette:
        """Current color palette based on effective theme."""
        return self._get_effective_palette()

    @property
    def fonts(self) -> FontConfig:
        """Font configuration."""
        return self._fonts

    @property
    def spacing(self) -> SpacingConfig:
        """Spacing configuration."""
        return self._spacing

    @property
    def style(self) -> StyleConfig:
        """Style configuration."""
        return self._style

    @property
    def is_dark(self) -> bool:
        """Check if current effective theme is dark."""
        if self._mode == "system":
            return darkdetect.isDark() or False
        return self._mode == "dark"

    def set_mode(self, mode: ThemeMode) -> None:
        """Set theme mode and notify observers."""
        if mode != self._mode:
            self._mode = mode
            self._apply_theme()
            self._notify_observers()

    def toggle_mode(self) -> None:
        """Toggle between light and dark modes."""
        if self._mode == "light":
            self.set_mode("dark")
        elif self._mode == "dark":
            self.set_mode("light")
        else:
            # If system, switch to opposite of current system theme
            if self.is_dark:
                self.set_mode("light")
            else:
                self.set_mode("dark")

    def subscribe(self, callback: Callable[[ColorPalette], None]) -> None:
        """Subscribe to theme changes."""
        self._observers.append(callback)

    def unsubscribe(self, callback: Callable[[ColorPalette], None]) -> None:
        """Unsubscribe from theme changes."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _get_effective_palette(self) -> ColorPalette:
        """Get the effective color palette based on current mode."""
        if self._mode == "system":
            return DARK_PALETTE if (darkdetect.isDark() or False) else LIGHT_PALETTE
        return DARK_PALETTE if self._mode == "dark" else LIGHT_PALETTE

    def _apply_theme(self) -> None:
        """Apply theme to CustomTkinter."""
        if self._mode == "system":
            ctk.set_appearance_mode("system")
        elif self._mode == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

        # Set default color theme (we use custom colors, so this is minimal)
        ctk.set_default_color_theme("blue")  # Base theme, we override colors

    def _notify_observers(self) -> None:
        """Notify all observers of theme change. Handles destroyed widgets gracefully."""
        palette = self.palette
        dead_observers = []

        for callback in self._observers:
            try:
                callback(palette)
            except Exception:
                # Widget was likely destroyed, mark for removal
                dead_observers.append(callback)

        # Clean up dead observers
        for callback in dead_observers:
            if callback in self._observers:
                self._observers.remove(callback)

    def get_button_colors(self) -> dict:
        """Get colors for primary buttons."""
        p = self.palette
        return {
            "fg_color": p.accent,
            "hover_color": p.accent_hover,
            "text_color": "#FFFFFF",
        }

    def get_secondary_button_colors(self) -> dict:
        """Get colors for secondary buttons."""
        p = self.palette
        return {
            "fg_color": p.bg_tertiary,
            "hover_color": p.border,
            "text_color": p.text_primary,
        }

    def get_card_colors(self) -> dict:
        """Get colors for card components."""
        p = self.palette
        return {
            "fg_color": p.bg_secondary,
            "border_color": p.border,
        }

    def get_input_colors(self) -> dict:
        """Get colors for input fields."""
        p = self.palette
        return {
            "fg_color": p.bg_primary,
            "border_color": p.border,
            "text_color": p.text_primary,
            "placeholder_text_color": p.text_muted,
        }

    def get_sidebar_colors(self) -> dict:
        """Get colors for sidebar."""
        p = self.palette
        return {
            "bg": p.sidebar_bg,
            "hover": p.sidebar_hover,
            "active": p.sidebar_active,
            "text": p.text_primary,
            "text_muted": p.text_secondary,
        }


# Category colors for badges
CATEGORY_COLORS = {
    "Images": "#3B82F6",  # Blue
    "Videos": "#8B5CF6",  # Purple
    "Audios": "#EC4899",  # Pink
    "Documents": "#10B981",  # Green
    "Executables": "#F59E0B",  # Amber
    "Archives": "#6366F1",  # Indigo
    "Fonts": "#14B8A6",  # Teal
    "Code": "#EF4444",  # Red
    "_Misc": "#6B7280",  # Gray
}

# Category icons (modern, minimal Unicode)
CATEGORY_ICONS = {
    "Images": "◫",
    "Videos": "▶",
    "Audios": "♪",
    "Documents": "☰",
    "Executables": "⚡",
    "Archives": "▤",
    "Fonts": "A",
    "Code": "</>",
    "_Misc": "◇",
}

# Risk level colors
RISK_COLORS = {
    "low": "#22C55E",
    "medium": "#F59E0B",
    "high": "#EF4444",
}

# Risk level icons (colored dots rendered in badge)
RISK_ICONS = {
    "low": "●",
    "medium": "●",
    "high": "●",
}

# Navigation icons (modern, minimal)
NAV_ICONS = {
    "dashboard": "◉",
    "scan_setup": "⊕",
    "plan_preview": "☰",
    "rules_editor": "≡",
    "ignore_editor": "⊘",
    "history": "↺",
    "settings": "⚙",
}


# Global theme manager instance
_theme_manager: ThemeManager | None = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def init_theme(mode: ThemeMode = "system") -> ThemeManager:
    """Initialize the theme manager with a specific mode."""
    global _theme_manager
    _theme_manager = ThemeManager(initial_mode=mode)
    return _theme_manager
