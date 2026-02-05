"""
Legacy main window module - deprecated.

Use sortodoco.ui.app.SortoDocoApp instead.
"""

# This file is kept for backwards compatibility
# The new GUI is in app.py

from sortodoco.ui.app import SortoDocoApp, run_app

__all__ = ["SortoDocoApp", "run_app"]
