import csv
import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QWidget

from app.models import CSVGrid

from app.ui.CSVTab_ui import Ui_CSVTab


class CSVTab(QWidget):
    def __init__(self, db_handler, profile_id, data_dir: Path):
        super().__init__()
        self.ui = Ui_CSVTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = CSVGrid(db_handler, profile_id)
        self.ui.tableView.setModel(self.model)
        self.ui.saveBtn.clicked.connect(self.save_csv)

        self.data_dir = data_dir

    def showEvent(self, event):
        self.refresh()
        return super().showEvent(event)

    def refresh(self):
        if not self.isVisible():
            return
        self.model.refresh_grid()
        IGNORED_COL = 31
        self.ui.tableView.setColumnHidden(IGNORED_COL, True)

    def save_csv(self):
        self.ui.saveBtn.setEnabled(False)
        self.ui.saveBtn.setText("Saving...")
        self.ui.saveBtn.repaint()
        os.makedirs(self.data_dir, exist_ok=True)
        csv_path = self.data_dir / "scrape_data.csv"
        i = 1
        while csv_path.exists():
            csv_path = self.data_dir / f"scrape_data({i}).csv"
            i += 1
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.model.get_headers())
            writer.writerows(self.model.all_events())
        self.ui.saveBtn.setEnabled(True)
        self.ui.saveBtn.setText("Save CSV")
        self.logger.info(f"Saved CSV to {csv_path}.")

        # minval = round(df["NASS_dv"].min(), 1)
        # mincase = df.loc[df["NASS_dv"].idxmin(), "case_id"]
        # maxval = round(df["NASS_dv"].max(), 1)
        # maxcase = df.loc[df["NASS_dv"].idxmax(), "case_id"]
        # dv_msg = f"Among these cases, the changes in velocity ranged from as low as {minval} mph ({mincase}) to as high as {maxval} mph ({maxcase})."
