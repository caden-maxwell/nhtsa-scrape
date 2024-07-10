from datetime import datetime
import logging
from pathlib import Path
import re

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget

from app.pages import SummaryTab, EventsTab, ScatterTab, CSVTab, BaseTab
from app.models import DatabaseHandler, Profile
from app.ui import Ui_DataView


class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(
        self, db_handler: DatabaseHandler, profile: Profile, new_profile=False
    ):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.logger = logging.getLogger(__name__)

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        # Get a filename-safe string for the new directory
        created = datetime.fromtimestamp(float(profile.created)).strftime(
            "%Y-%m-%d %H-%M-%S"
        )

        dir_name = f"{profile.name}_{created}".replace(" ", "_")
        filename_safe = ["_", "-", "(", ")"]
        dir_name = "".join(
            c if c.isalnum() or c in filename_safe else "_" for c in dir_name
        )
        dir_name = re.sub(r"[_-]{2,}", "_", dir_name)
        self.data_dir = (Path(__file__).parent.parent / "data" / dir_name).resolve()

        self.summary_tab = SummaryTab(profile)
        self.events_tab = EventsTab(db_handler, profile, self.data_dir)
        self.scatter_tab = ScatterTab(db_handler, profile, self.data_dir)
        self.csv_tab = CSVTab(db_handler, profile, self.data_dir)

        self.ui.tabWidget.addTab(self.summary_tab, "Summary")
        self.ui.tabWidget.addTab(self.events_tab, "Events")
        self.ui.tabWidget.addTab(self.scatter_tab, "Scatterplot")
        self.ui.tabWidget.addTab(self.csv_tab, "Data Table")

        if new_profile:
            self.ui.tabWidget.setCurrentWidget(self.events_tab)
        else:
            self.ui.tabWidget.setCurrentWidget(self.summary_tab)
        self.ui.tabWidget.currentChanged.connect(self.update_current_tab)

    def update_current_tab(self):
        """Refresh the current tab when it is switched to."""
        widget: BaseTab = self.ui.tabWidget.currentWidget()
        widget.refresh_tab()

    def closeEvent(self, event):
        self.exited.emit()
        self.events_tab.closeEvent(event)
        return super().closeEvent(event)
