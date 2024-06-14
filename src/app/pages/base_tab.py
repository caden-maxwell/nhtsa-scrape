from abc import ABC, abstractmethod

from PyQt6.QtWidgets import QWidget


class _Meta(type(QWidget), type(ABC)):
    """Metaclass for BaseTab."""


class BaseTab(QWidget, ABC, metaclass=_Meta):
    """Base class for tabs in DataViewer."""

    @abstractmethod
    def __init__(self):
        super().__init__()

    @abstractmethod
    def refresh_tab(self):
        """Refreshes the tab's contents."""
