import csv
import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox

from app.pages import BaseTab
from app.pages.utils import open_path
from app.models import EventTable, Profile
from app.ui import Ui_CSVTab


class CSVTab(BaseTab):
    def __init__(self, db_handler, profile: Profile, data_dir: Path):
        super().__init__()
        self.ui = Ui_CSVTab()
        self.ui.setupUi(self)
        self._logger = logging.getLogger(__name__)

        self._model = EventTable(db_handler, profile)
        self.ui.tableView.setModel(self._model)
        self.ui.saveBtn.clicked.connect(self._save_csv)

        self._data_dir = data_dir

    def refresh(self):
        self._model.refresh_data()
        self.ui.tableView.hideColumn(0)
        self.ui.tableView.hideColumn(1)

    def _save_csv(self):
        self.ui.saveBtn.setEnabled(False)
        self.ui.saveBtn.setText("Saving...")
        self.ui.saveBtn.update()
        os.makedirs(self._data_dir, exist_ok=True)
        csv_path = self._data_dir / "scrape_data.csv"
        i = 1
        while csv_path.exists():
            csv_path = self._data_dir / f"scrape_data({i}).csv"
            i += 1
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self._model.get_headers())
            writer.writerows(self._model.all_events())
        self.ui.saveBtn.setEnabled(True)
        self.ui.saveBtn.setText("Save as CSV")
        self._logger.info(f"Saved CSV to {csv_path}.")

        box = QMessageBox()
        box.setWindowTitle("CSV Saved")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText("CSV saved to:")
        box.setInformativeText(str(csv_path))
        box.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open
        )
        box.setDefaultButton(QMessageBox.StandardButton.Ok)
        button_result = box.exec()

        if button_result == QMessageBox.StandardButton.Open:
            success = open_path(self._data_dir)
            if not success:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to open directory. See log for details.",
                    QMessageBox.StandardButton.Ok,
                )

        # minval = round(df["NASS_dv"].min(), 1)
        # mincase = df.loc[df["NASS_dv"].idxmin(), "case_id"]
        # maxval = round(df["NASS_dv"].max(), 1)
        # maxcase = df.loc[df["NASS_dv"].idxmax(), "case_id"]
        # dv_msg = f"Among these cases, the changes in velocity ranged from as low as {minval} mph ({mincase}) to as high as {maxval} mph ({maxcase})."
