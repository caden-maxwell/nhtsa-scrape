import csv
import logging
import os
from pathlib import Path

from app.pages import BaseTab
from app.models import EventTable, Profile
from app.ui import Ui_CSVTab


class CSVTab(BaseTab):
    def __init__(self, db_handler, profile: Profile, data_dir: Path):
        super().__init__()
        self.ui = Ui_CSVTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = EventTable(db_handler, profile)
        self.ui.tableView.setModel(self.model)
        self.ui.saveBtn.clicked.connect(self.save_csv)

        self.data_dir = data_dir

    def refresh_tab(self):
        self.model.refresh_data()
        self.ui.tableView.hideColumn(0)

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
