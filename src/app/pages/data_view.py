import csv
from datetime import datetime
import logging
from pathlib import Path
import re

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget

import pandas

from . import ScatterTab
from . import EventsTab
from app.models import ProfileEvents
from app.ui.DataView_ui import Ui_DataView


class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(self, profile_id):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.model = ProfileEvents(profile_id)
        self.model.refresh_events()

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        # Get a filename-safe string for the new directory
        profile_name = str(self.model.profile[1])
        created = datetime.fromtimestamp(float(self.model.profile[3])).strftime(
            "%Y-%m-%d %H-%M-%S"
        )
        dir_name = f"{profile_name}_{created}".replace(" ", "_")
        filename_safe = ["_", "-", "(", ")"]
        dir_name = "".join(
            c if c.isalnum() or c in filename_safe else "_" for c in dir_name
        )
        dir_name = re.sub(r"[_-]{2,}", "_", dir_name)
        self.data_dir = (Path(__file__).parent.parent.parent / "data" / dir_name).resolve()

        self.events_tab = EventsTab(self.model)
        self.scatter_tab = ScatterTab(self.model, self.data_dir)

        self.ui.tabWidget.addTab(QWidget(), "Summary")
        self.ui.tabWidget.addTab(self.events_tab, "Events")
        self.ui.tabWidget.addTab(self.scatter_tab, "Scatterplot")
        self.ui.tabWidget.addTab(QWidget(), "Data Table")

        self.scatter_tab.update_plot()

    @pyqtSlot(dict)
    def add_event(self, event):
        self.model.add_event(event)
        self.scatter_tab.update_plot()

        file = "random.csv"
        df = pandas.DataFrame(self.model.all_events())
        df.to_csv(self.data_dir / file, index=False)
        with open(self.data_dir / file, "a") as f:
            writer = csv.writer(f)

            case_ids = df["case_id"].unique()
            event_str = ", ".join(str(id) for id in case_ids[:-1])
            event_str = (
                event_str + f", and {case_ids[-1]}."
                if len(case_ids) > 1
                else event_str + "."
            )

            minval = round(df["NASS_dv"].min(), 1)
            mincase = df.loc[df["NASS_dv"].idxmin(), "case_id"]
            maxval = round(df["NASS_dv"].max(), 1)
            maxcase = df.loc[df["NASS_dv"].idxmax(), "case_id"]

            dv_msg = f"Among these cases, the changes in velocity ranged from as low as {minval} mph ({mincase}) to as high as {maxval} mph ({maxcase})."

            par = event_str + " " + dv_msg
            writer.writerows([[], [par]])

    @pyqtSlot()
    def scrape_complete(self):
        # if not len(self.model.data_list):
        #     self.ui.summaryEdit.append("Scrape complete. No data found.")
        # else:
        #     self.ui.summaryEdit.append("Scrape complete.")
        pass
