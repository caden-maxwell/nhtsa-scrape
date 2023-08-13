import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QWidget

from app.models import CSVGrid

from app.ui.CSVTab_ui import Ui_CSVTab


class CSVTab(QWidget):
    def __init__(self, profile_id, data_dir: Path):
        super().__init__()
        self.ui = Ui_CSVTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = CSVGrid(profile_id)
        self.ui.tableView.setModel(self.model)
        IGNORED_COL = 31
        self.ui.tableView.setColumnHidden(IGNORED_COL, True)
        self.ui.saveBtn.clicked.connect(self.save_csv)

        self.data_dir = data_dir

    def showEvent(self, event):
        self.model.refresh_grid()
        return super().showEvent(event)

    def save_csv(self):
        os.makedirs(self.data_dir, exist_ok=True)
        try:
            csv_path = self.data_dir / "scrape_data.csv"
            i = 1
            while csv_path.exists():
                csv_path = self.data_dir / f"scrape_data({i}).csv"
                i += 1
            with open(csv_path, "w") as f:
                for event in self.model.all_data():
                    f.write(",".join([str(x) for x in event[:31]]) + "\n")
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
            return
        self.logger.info(f"Saved CSV to {csv_path}.")
