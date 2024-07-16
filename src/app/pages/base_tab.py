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
    def refresh(self):
        """Refreshes the tab's contents."""

    def set_data_dir(self, data_dir):
        """Sets the data directory for the tab."""
        self._data_dir = data_dir
