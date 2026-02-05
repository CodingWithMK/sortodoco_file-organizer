"""
Rules Editor view - Manage file classification rules.
"""

import customtkinter as ctk
from typing import Optional, Callable
import json
from pathlib import Path

from sortodoco.ui.views.base import BaseView
from sortodoco.ui.widgets.card import Card
from sortodoco.ui.theme import get_theme_manager, CATEGORY_ICONS


class RulesEditorView(BaseView):
    """
    Rules editor view for managing file classification rules.

    Features:
    - View current rules
    - Add/edit/remove extension mappings
    - Test rules with filenames
    - Restore defaults
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(
            master, title="Rules Editor", on_navigate=on_navigate, **kwargs
        )

        self._rules: dict[str, list[str]] = {}
        self._load_rules()
        self._build_content()

    def _load_rules(self) -> None:
        """Load current rules."""
        rules_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "rules"
            / "extensions.json"
        )
        if rules_path.exists():
            try:
                with open(rules_path) as f:
                    self._rules = json.load(f)
            except Exception:
                self._rules = {}

    def _build_content(self) -> None:
        """Build the rules editor content."""
        p = self._theme.palette

        self.content.grid_columnconfigure(0, weight=2)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Left side - Rules list
        rules_card = Card(self.content, title="Extension Rules")
        rules_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_rules_list(rules_card.content_frame)

        # Right side - Test and Add
        right_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right_frame.grid_rowconfigure(1, weight=1)

        # Test rule card
        test_card = Card(right_frame, title="Test Rule")
        test_card.pack(fill="x", pady=(0, 16))
        self._build_test_section(test_card.content_frame)

        # Add rule card
        add_card = Card(right_frame, title="Add Extension")
        add_card.pack(fill="x")
        self._build_add_section(add_card.content_frame)

        # Bottom buttons
        button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, sticky="e", pady=(16, 0))

        restore_btn = ctk.CTkButton(
            button_frame,
            text="Restore Defaults",
            font=ctk.CTkFont(size=13),
            width=130,
            height=40,
            fg_color=p.bg_tertiary,
            hover_color=p.border,
            text_color=p.text_primary,
            command=self._restore_defaults,
        )
        restore_btn.pack(side="left", padx=8)

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Rules",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            height=40,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._save_rules,
        )
        save_btn.pack(side="left")

    def _build_rules_list(self, content: ctk.CTkFrame) -> None:
        """Build the rules list."""
        p = self._theme.palette

        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(content, fg_color="transparent", height=400)
        scroll.pack(fill="both", expand=True)

        for category, extensions in self._rules.items():
            # Category header
            icon = CATEGORY_ICONS.get(category, "📁")
            cat_frame = ctk.CTkFrame(scroll, fg_color=p.bg_tertiary, corner_radius=6)
            cat_frame.pack(fill="x", pady=4)

            cat_label = ctk.CTkLabel(
                cat_frame,
                text=f"{icon} {category}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=p.text_primary,
            )
            cat_label.pack(side="left", padx=12, pady=8)

            # Extensions
            ext_text = ", ".join(f".{ext}" for ext in extensions[:5])
            if len(extensions) > 5:
                ext_text += f" (+{len(extensions) - 5} more)"

            ext_label = ctk.CTkLabel(
                cat_frame,
                text=ext_text,
                font=ctk.CTkFont(size=11),
                text_color=p.text_secondary,
            )
            ext_label.pack(side="left", padx=8)

            # Count
            count_label = ctk.CTkLabel(
                cat_frame,
                text=f"{len(extensions)} ext",
                font=ctk.CTkFont(size=11),
                text_color=p.text_muted,
            )
            count_label.pack(side="right", padx=12)

    def _build_test_section(self, content: ctk.CTkFrame) -> None:
        """Build the test rule section."""
        p = self._theme.palette

        # Input
        test_label = ctk.CTkLabel(
            content,
            text="Enter a filename to see how it would be classified:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        test_label.pack(anchor="w", pady=(0, 8))

        self._test_entry = ctk.CTkEntry(
            content,
            width=250,
            height=32,
            placeholder_text="example.jpg",
            font=ctk.CTkFont(size=12),
        )
        self._test_entry.pack(fill="x", pady=(0, 8))

        test_btn = ctk.CTkButton(
            content,
            text="Test",
            font=ctk.CTkFont(size=12),
            width=80,
            height=32,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._test_rule,
        )
        test_btn.pack(anchor="w", pady=(0, 8))

        # Result
        self._test_result = ctk.CTkLabel(
            content, text="", font=ctk.CTkFont(size=12), text_color=p.text_primary
        )
        self._test_result.pack(anchor="w")

    def _build_add_section(self, content: ctk.CTkFrame) -> None:
        """Build the add extension section."""
        p = self._theme.palette

        # Extension input
        ext_frame = ctk.CTkFrame(content, fg_color="transparent")
        ext_frame.pack(fill="x", pady=4)

        ext_label = ctk.CTkLabel(
            ext_frame,
            text="Extension:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        ext_label.pack(side="left")

        self._new_ext_entry = ctk.CTkEntry(
            ext_frame,
            width=100,
            height=28,
            placeholder_text="xyz",
            font=ctk.CTkFont(size=12),
        )
        self._new_ext_entry.pack(side="right")

        # Category selection
        cat_frame = ctk.CTkFrame(content, fg_color="transparent")
        cat_frame.pack(fill="x", pady=4)

        cat_label = ctk.CTkLabel(
            cat_frame,
            text="Category:",
            font=ctk.CTkFont(size=12),
            text_color=p.text_secondary,
        )
        cat_label.pack(side="left")

        categories = list(self._rules.keys()) + ["_Misc"]
        self._new_cat_var = ctk.StringVar(
            value=categories[0] if categories else "_Misc"
        )
        cat_menu = ctk.CTkOptionMenu(
            cat_frame,
            width=120,
            height=28,
            values=categories,
            variable=self._new_cat_var,
            font=ctk.CTkFont(size=12),
            fg_color=p.bg_tertiary,
            button_color=p.border,
        )
        cat_menu.pack(side="right")

        # Add button
        add_btn = ctk.CTkButton(
            content,
            text="Add Extension",
            font=ctk.CTkFont(size=12),
            width=120,
            height=32,
            fg_color=p.accent,
            hover_color=p.accent_hover,
            text_color="#FFFFFF",
            command=self._add_extension,
        )
        add_btn.pack(anchor="e", pady=8)

    def _test_rule(self) -> None:
        """Test a filename against rules."""
        filename = self._test_entry.get().strip()
        if not filename:
            self._test_result.configure(text="Please enter a filename")
            return

        # Get extension
        if "." in filename:
            ext = filename.rsplit(".", 1)[-1].lower()
        else:
            ext = ""

        # Find category
        category = "_Misc"
        matched_rule = None
        for cat, extensions in self._rules.items():
            if ext in [e.lower() for e in extensions]:
                category = cat
                matched_rule = f".{ext}"
                break

        icon = CATEGORY_ICONS.get(category, "📁")
        result = f"{icon} {category}"
        if matched_rule:
            result += f" (matched: {matched_rule})"
        else:
            result += " (no rule matched)"

        self._test_result.configure(text=result)

    def _add_extension(self) -> None:
        """Add a new extension mapping."""
        ext = self._new_ext_entry.get().strip().lower().lstrip(".")
        category = self._new_cat_var.get()

        if not ext:
            return

        if category not in self._rules:
            self._rules[category] = []

        if ext not in self._rules[category]:
            self._rules[category].append(ext)
            self._new_ext_entry.delete(0, "end")
            self.refresh()

    def _restore_defaults(self) -> None:
        """Restore default rules."""
        self._rules = {
            "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "heic"],
            "Videos": ["mp4", "mov", "avi", "mkv", "webm"],
            "Audios": ["mp3", "wav", "ogg", "m4a", "aac", "flac"],
            "Documents": [
                "doc",
                "docx",
                "pdf",
                "txt",
                "csv",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
            ],
            "Executables": ["exe", "msi"],
            "Archives": ["zip", "rar", "tar", "gz", "7z"],
            "Fonts": ["ttf", "otf"],
            "Code": [
                "py",
                "java",
                "c",
                "cpp",
                "js",
                "css",
                "html",
                "json",
                "jsx",
                "tsx",
            ],
        }
        self.refresh()

    def _save_rules(self) -> None:
        """Save rules to file."""
        rules_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "rules"
            / "extensions.json"
        )
        try:
            with open(rules_path, "w") as f:
                json.dump(self._rules, f, indent=2)
        except Exception as e:
            print(f"Error saving rules: {e}")

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
