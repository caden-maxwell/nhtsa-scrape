import csv
import logging
import os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

import logging
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy

from app.models import ProfileEvents
from app.ui.DataView_ui import Ui_DataView

logging.getLogger("matplotlib").setLevel(logging.WARNING)


class DataView(QWidget):
    exited = pyqtSignal()

    def __init__(self, profile_id):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.model = ProfileEvents(profile_id)
        self.model.refresh_data()

        self.ui = Ui_DataView()
        self.ui.setupUi(self)

        self.ui.listView.setModel(self.model)
        self.ui.listView.doubleClicked.connect(self.open_item_details)

        self.data_dir = (Path(__file__).parent.parent / "test").resolve()
        os.makedirs(self.data_dir, exist_ok=True)

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        toolbar = NavigationToolbar(self.canvas, self)

        icon_path = Path(__file__).parent.parent / "resources" / "toggle.png"
        action = QAction(QIcon(str(icon_path)), "Toggles", self)

        toolbar.insertAction(toolbar.actions()[8], action)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        self.ui.scatterTab.setLayout(layout)

        self.toggle_window = QWidget()
        action.triggered.connect(self.toggle_window.show)

        toggle_layout = QVBoxLayout()

        self.nass_toggle = QCheckBox("NASS_dv")
        self.nass_toggle.setChecked(True)
        toggle_layout.addWidget(self.nass_toggle)

        self.total_toggle = QCheckBox("TOT_dv")
        self.total_toggle.setChecked(False)
        toggle_layout.addWidget(QCheckBox("TOT_dv"))

        self.toggle_window.setLayout(toggle_layout)

        self.update_scatter_view()

    def open_item_details(self, index):
        self.ui.eventLabel.setText(f"Index selected: {index.row()}")

    @pyqtSlot(dict)
    def add_event(self, event):
        self.model.add_data(event)
        self.update_scatter_view()
        return
        file = "random.csv"
        df = pandas.DataFrame(self.model.all_data())
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

    def update_scatter_view(self):
        self.ax.clear()

        xdata = []
        y1data = []
        y2data = []
        case_ids = []
        for event in self.model.all_data():
            xdata.append(event["c_bar"])
            y1data.append(event["NASS_dv"])
            y2data.append(event["TOT_dv"])
            case_ids.append(event["case_id"])

        if len(xdata) < 2:
            self.canvas.draw()
            return

        # NASS_dv plot and fit
        self.ax.scatter(xdata, y1data, c="darkblue", s=10)

        coeffs = numpy.polyfit(xdata, y1data, 1)
        polynomial = numpy.poly1d(coeffs)

        x_fit = numpy.linspace(min(xdata), max(xdata))
        y_fit = polynomial(x_fit)

        self.ax.plot(x_fit, y_fit, color="darkblue", linewidth=1)[0]

        # NASS_dv R^2 calculation
        y_pred = polynomial(xdata)
        ssr = numpy.sum((y_pred - numpy.mean(y1data)) ** 2)
        sst = numpy.sum((y1data - numpy.mean(y1data)) ** 2)
        r_squared = ssr / sst

        self.ax.legend(
            [
                "NASS_dv",
                f"$y = {str(polynomial).strip()}$\n$R^2$ = {r_squared:.2f}",
            ],
            loc="upper left",
        ).set_draggable(True)

        # TOT_dv plot and fit
        self.ax.scatter(xdata, y2data, c="red", s=10)

        coeffs_e = numpy.polyfit(xdata, y2data, 1)
        polynomial_e = numpy.poly1d(coeffs_e)

        x_fit_e = numpy.linspace(min(xdata), max(xdata))
        y_fit_e = polynomial_e(x_fit_e)

        self.ax.plot(x_fit_e, y_fit_e, color="red")[0]

        y_pred_e = polynomial_e(xdata)
        ssr_e = numpy.sum((y_pred_e - numpy.mean(y2data)) ** 2)
        sst_e = numpy.sum((y2data - numpy.mean(y2data)) ** 2)
        r_squared_e = ssr_e / sst_e

        leg_e = self.ax.legend(
            [
                f"NASS, $y = {str(polynomial).strip()}$\n$R^2= {r_squared:.2f}$",
                f"TOT, $y = {str(polynomial_e).strip()}$\n$R^2= {r_squared_e:.2f}$",
            ],
            loc="upper left",
        )
        leg_e.set_draggable(True)

        # Case ID labels
        for i, case_id in enumerate(case_ids):
            ann = self.ax.annotate(case_id, (xdata[i], y1data[i]))
            ann.draggable(True)
            ann1 = self.ax.annotate(case_id, (xdata[i], y2data[i]))
            ann1.draggable(True)

        self.ax.set_xlabel("Crush (inches)", fontsize=14)
        self.ax.set_ylabel("Change in Velocity (mph)", fontsize=14)

        self.canvas.draw()

        crush_est = numpy.array([0, 1.0])
        print(polynomial(crush_est))
        print(polynomial_e(crush_est))
        # print(df)

    def toggle_nass_dv(self):
        self.nass_label_button.setEnabled(self.nass_dv_button.isChecked())
        self.update_scatter_view()

    def toggle_nass_labels(self):
        self.update_scatter_view()

    def toggle_total_dv(self):
        self.total_label_button.setEnabled(self.total_dv_button.isChecked())
        self.update_scatter_view()

    def toggle_total_labels(self):
        self.update_scatter_view()

    def scrape_complete(self):
        if not len(self.model.data_list):
            self.ui.summaryEdit.append("Scrape complete. No data found.")
        else:
            self.ui.summaryEdit.append("Scrape complete.")
