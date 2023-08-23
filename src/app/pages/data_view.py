from datetime import datetime
import logging
from pathlib import Path
import re

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget

from . import SummaryTab, EventsTab, ScatterTab, CSVTab
from app.models import DatabaseHandler, ProfileEvents
from app.ui.DataView_ui import Ui_DataView


class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(self, db_handler: DatabaseHandler, profile_id):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.model = ProfileEvents(db_handler, profile_id)

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.profile = db_handler.get_profile(profile_id)
        # Get a filename-safe string for the new directory
        profile_name = str(self.profile[1])
        # "make": self.ui.makeCombo.currentText().upper(),
        # "model": self.ui.modelCombo.currentText().upper(),
        # "start_year": self.ui.startYearCombo.currentText().upper(),
        # "end_year": self.ui.endYearCombo.currentText().upper(),
        # "primary_dmg": self.ui.pDmgCombo.currentText().upper(),
        # "secondary_dmg": self.ui.sDmgCombo.currentText().upper(),
        # "min_dv": self.ui.dvMinSpin.value(),
        # "max_dv": self.ui.dvMaxSpin.value(),
        # "max_cases": case_limit,
        # "created": int(now.timestamp()),
        # "modified": int(now.timestamp()),
        created = datetime.fromtimestamp(float(self.profile[10])).strftime(
            "%Y-%m-%d %H-%M-%S"
        )
        dir_name = f"{profile_name}_{created}".replace(" ", "_")
        filename_safe = ["_", "-", "(", ")"]
        dir_name = "".join(
            c if c.isalnum() or c in filename_safe else "_" for c in dir_name
        )
        dir_name = re.sub(r"[_-]{2,}", "_", dir_name)
        self.data_dir = (Path(__file__).parent.parent / "data" / dir_name).resolve()

        self.summary_tab = SummaryTab()
        self.events_tab = EventsTab(self.model, self.data_dir)
        self.scatter_tab = ScatterTab(self.model, self.data_dir)
        self.csv_tab = CSVTab(db_handler, profile_id, self.data_dir)

        self.ui.tabWidget.addTab(self.summary_tab, "Summary")
        self.ui.tabWidget.addTab(self.events_tab, "Events")
        self.ui.tabWidget.addTab(self.scatter_tab, "Scatterplot")
        self.ui.tabWidget.addTab(self.csv_tab, "Data Table")

    @pyqtSlot(dict, bytes, str)
    def add_event(self, event, response_content, cookie):
        self.model.add_event(event)
        self.events_tab.cache_response(int(event["case_id"]), response_content, cookie)
        self.scatter_tab.update_plot()
        self.csv_tab.refresh()

    def closeEvent(self, event):
        self.exited.emit()
        return super().closeEvent(event)
