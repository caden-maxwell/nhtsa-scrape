from datetime import datetime
import logging
from pathlib import Path
import re

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from . import SummaryTab, EventsTab, ScatterTab, CSVTab, BaseTab
from app.models import DatabaseHandler
from app.ui.DataView_ui import Ui_DataView


class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(self, db_handler: DatabaseHandler, profile_id, new_profile=False):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.profile = db_handler.get_profile(profile_id)

        # Get a filename-safe string for the new directory
        created = datetime.fromtimestamp(float(self.profile[12])).strftime(
            "%Y-%m-%d %H-%M-%S"
        )

        dir_name = f"{self.profile[1]}_{created}".replace(" ", "_")
        filename_safe = ["_", "-", "(", ")"]
        dir_name = "".join(
            c if c.isalnum() or c in filename_safe else "_" for c in dir_name
        )
        dir_name = re.sub(r"[_-]{2,}", "_", dir_name)
        self.data_dir = (Path(__file__).parent.parent / "data" / dir_name).resolve()

        self.summary_tab = SummaryTab(self.profile)
        self.events_tab = EventsTab(db_handler, profile_id, self.data_dir)
        self.scatter_tab = ScatterTab(db_handler, profile_id, self.data_dir)
        self.csv_tab = CSVTab(db_handler, profile_id, self.data_dir)

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
        widget: BaseTab = self.ui.tabWidget.currentWidget()
        widget.refresh_tab()

    def closeEvent(self, event):
        self.exited.emit()
        return super().closeEvent(event)
