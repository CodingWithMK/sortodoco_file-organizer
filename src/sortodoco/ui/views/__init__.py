"""
Views package for SortoDoco GUI.
"""

from sortodoco.ui.views.dashboard import DashboardView
from sortodoco.ui.views.scan_setup import ScanSetupView
from sortodoco.ui.views.plan_preview import PlanPreviewView
from sortodoco.ui.views.rules_editor import RulesEditorView
from sortodoco.ui.views.ignore_editor import IgnoreEditorView
from sortodoco.ui.views.history import HistoryView
from sortodoco.ui.views.settings import SettingsView

__all__ = [
    "DashboardView",
    "ScanSetupView",
    "PlanPreviewView",
    "RulesEditorView",
    "IgnoreEditorView",
    "HistoryView",
    "SettingsView",
]
