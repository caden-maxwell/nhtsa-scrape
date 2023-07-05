import csv
import logging
import os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThreadPool
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QDialog
import pandas

from app.models import ProfileEvents
from app.scrape import ScatterplotWorker
from app.ui.ExitDataViewDialog_ui import Ui_ExitDialog
from app.ui.DataView_ui import Ui_DataView


class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(self, profile_id):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.model = ProfileEvents(profile_id)

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.ui.exitBtn.clicked.connect(self.handle_exit_button_clicked)
        self.ui.listView.setModel(self.model)
        self.ui.listView.doubleClicked.connect(self.open_item_details)

        self.threads = QThreadPool()

    def showEvent(self, event):
        self.model.refresh_data()
        self.ui.listView.clearSelection()
        self.update_scatter_view()
        return super().showEvent(event)

    def handle_exit_button_clicked(self):
        self.exit_dialog_controller = ExitDataViewDialog()
        self.exit_dialog_controller.exec()
        self.exited.emit()

    def open_item_details(self, index):
        self.ui.eventLabel.setText(f"Index selected: {index.row()}")

    @pyqtSlot(dict)
    def add_event(self, event):
        self.model.add_data(event)

        data_dir = Path(__file__).parent.parent / "test"
        scatter_worker = ScatterplotWorker(self.model.all_data(), data_dir)
        scatter_worker.signals.finished.connect(self.update_scatter_view)
        self.threads.start(scatter_worker)

        file = "random.csv"
        df = pandas.DataFrame(self.model.all_data())
        os.makedirs(data_dir, exist_ok=True)
        df.to_csv(data_dir / file, index=False)

        with open(data_dir / file, "a") as f:
            writer = csv.writer(f)

            case_ids = df["case_id"].unique()
            event_str = (
                ", ".join(str(cnum) for cnum in case_ids[:-1])
                + f", and {case_ids[-1]}."
            )

            minval = round(df["NASS_dv"].min(), 1)
            mincase = df.loc[df["NASS_dv"].idxmin(), "case_id"]
            maxval = round(df["NASS_dv"].max(), 1)
            maxcase = df.loc[df["NASS_dv"].idxmax(), "case_id"]

            dv_msg = f"Among these cases, the changes in velocity ranged from as low as {minval} mph ({mincase}) to as high as {maxval} mph ({maxcase})."

            par = event_str + " " + dv_msg
            writer.writerows([[], [par]])

    def scrape_complete(self):
        if not len(self.model.data_list):
            self.ui.summaryEdit.append("Scrape complete. No data found.")
            return

    def update_scatter_view(self):
        dir_path = Path(__file__).parent.parent / "test"
        caseid_path = dir_path / "NASS_Analysis.png"
        if caseid_path.exists():
            self.ui.scatterLabel.setPixmap(QPixmap(str(caseid_path)))
        else:
            self.ui.scatterLabel.setPixmap(QPixmap())


class ExitDataViewDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_ExitDialog()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.ui.buttonBox.accepted.connect(self.handle_accepted)
        self.ui.buttonBox.button(
            self.ui.buttonBox.StandardButton.Discard
        ).clicked.connect(self.handle_rejected)

    def handle_accepted(self):
        ### TODO: Add save logic ###
        profile_name = self.ui.profileNameEdit.text()
        self.logger.info(
            f"User saved changes to profile '{profile_name}' and exited data viewer."
        )
        self.close()

    def handle_rejected(self):
        ### TODO: Add discard logic ###
        self.logger.info("User discarded changes and exited data viewer.")
        self.close()
