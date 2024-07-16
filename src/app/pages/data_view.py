import logging
import os
from pathlib import Path
import re

from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget

from app.pages import SummaryTab, EventsTab, ScatterTab, CSVTab, BaseTab
from app.models import DatabaseHandler, Profile, Event
from app.scrape import RequestHandler
from app.ui import Ui_DataView


class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(
        self,
        req_handler: RequestHandler,
        db_handler: DatabaseHandler,
        profile: Profile,
        data_dir: Path,
    ):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._logger = logging.getLogger(__name__)

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self._profile = profile
        profile_dir = (data_dir / self._get_profile_dir()).resolve()
        self._prev_profile_dir = profile_dir  # Used if the profile is renamed
        self._data_dir = data_dir

        self._summary_tab = SummaryTab(profile, profile_dir)
        self._events_tab = EventsTab(req_handler, db_handler, profile, profile_dir)
        self._scatter_tab = ScatterTab(db_handler, profile, profile_dir)
        self._csv_tab = CSVTab(db_handler, profile, profile_dir)
        self._tabs: list[BaseTab] = [
            self._summary_tab,
            self._events_tab,
            self._scatter_tab,
            self._csv_tab,
        ]

        self.ui.tabWidget.addTab(self._events_tab, "Events")
        self.ui.tabWidget.addTab(self._scatter_tab, "Scatterplot")
        self.ui.tabWidget.addTab(self._csv_tab, "Data Table")
        self.ui.tabWidget.addTab(self._summary_tab, "Scrape")

        self.ui.tabWidget.setCurrentWidget(self._events_tab)
        self.ui.tabWidget.currentChanged.connect(self.update_current_tab)

    def _get_profile_dir(self) -> str:
        """Generate a directory name for the profile."""
        dir_name = f"{self._profile.name}".replace(" ", "_")
        filename_safe = ["_", "-", "(", ")"]
        dir_name = "".join(
            c if c.isalnum() or c in filename_safe else "_" for c in dir_name
        )
        return re.sub(r"[_-]{2,}", "_", dir_name)

    def update_current_tab(self):
        """Refresh the currently selected tab."""
        widget: BaseTab = self.ui.tabWidget.currentWidget()
        widget.refresh()

    def set_data_dir(self, data_dir: Path):
        self._data_dir = data_dir
        self._set_tabs_profile_dir()

    def _set_tabs_profile_dir(self):
        profile_dir = (self._data_dir / self._get_profile_dir()).resolve()
        if profile_dir == self._prev_profile_dir:
            return

        # Move the old profile directory to the new location
        try:
            os.rename(self._prev_profile_dir, profile_dir)
        except Exception as e:
            self._logger.error(f"Failed to move profile directory: {e}", exc_info=True)
            return
        self._prev_profile_dir = profile_dir

        for tab in self._tabs:
            tab.set_data_dir(profile_dir)

    @pyqtSlot(Profile)
    def handle_profile_updated(self, profile: Profile):
        if profile.id == self._profile.id:
            self._set_tabs_profile_dir()

    @pyqtSlot(Event)
    def handle_event_added(self, event):
        for tab in self._tabs:
            tab.refresh()

    def get_profile(self):
        return self._profile

    def closeEvent(self, event):
        self.exited.emit()
        self._events_tab.closeEvent(event)
        return super().closeEvent(event)
