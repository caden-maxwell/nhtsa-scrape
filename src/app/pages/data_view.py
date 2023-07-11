import csv
import logging
import os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget

import logging
from matplotlib import rcParams, style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy

from app.models import ProfileEvents
from app.ui.DataView_ui import Ui_DataView

logging.getLogger("matplotlib").setLevel(logging.WARNING)
rcParams["savefig.dpi"] = 300
rcParams["savefig.bbox"] = "tight"
rcParams["savefig.pad_inches"] = 0.75
rcParams["savefig.format"] = "png"
style.use("seaborn-deep")


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
        self.ui.nassDataBtn.clicked.connect(self.update_nass_data)
        self.ui.nassLabelBtn.clicked.connect(self.update_nass_labels)
        self.ui.totalDataBtn.clicked.connect(self.update_tot_data)
        self.ui.totalLabelBtn.clicked.connect(self.update_tot_labels)

        self.data_dir = (Path(__file__).parent.parent / "test").resolve()
        os.makedirs(self.data_dir, exist_ok=True)

        self.figure = Figure(tight_layout=True, dpi=60)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: none;")

        self.ui.scatterLayout.addWidget(toolbar)
        self.ui.scatterLayout.addWidget(self.canvas)

        self.nass_plots = []
        self.nass_labels = []
        self.nass_legend = []
        self.tot_plots = []
        self.tot_labels = []
        self.tot_legend = []
        self.update_scatter_view()

    def update_nass_data(self):
        checked = self.ui.nassDataBtn.isChecked()
        for plot in self.nass_plots:
            plot.set_visible(checked)
        self.canvas.draw()
        self.ui.nassLabelBtn.setEnabled(checked)

        self.update_nass_labels()
        self.update_legend()

    def update_nass_labels(self):
        visible = self.ui.nassLabelBtn.isChecked() and self.ui.nassLabelBtn.isEnabled()
        for label in self.nass_labels:
            label.set_visible(visible)
        self.canvas.draw()

    def update_tot_data(self):
        checked = self.ui.totalDataBtn.isChecked()
        for plot in self.tot_plots:
            plot.set_visible(checked)
        self.canvas.draw()
        self.ui.totalLabelBtn.setEnabled(checked)

        self.update_tot_labels()
        self.update_legend()

    def update_tot_labels(self):
        visible = (
            self.ui.totalLabelBtn.isChecked() and self.ui.totalLabelBtn.isEnabled()
        )
        for label in self.tot_labels:
            label.set_visible(visible)
        self.canvas.draw()

    def update_legend(self):
        self.ax.get_legend().remove()
        if self.ui.nassDataBtn.isChecked() and self.ui.totalDataBtn.isChecked():
            self.ax.legend(
                self.nass_plots + self.tot_plots,
                self.nass_legend + self.tot_legend,
                loc="upper left",
            )
        elif self.ui.nassDataBtn.isChecked():
            self.ax.legend(self.nass_plots, self.nass_legend, loc="upper left")
        elif self.ui.totalDataBtn.isChecked():
            self.ax.legend(self.tot_plots, self.tot_legend, loc="upper left")
        else:
            self.ax.legend(loc="upper left").set_visible(False)
        self.canvas.draw()

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

        # NASS_dv
        coeffs = numpy.polyfit(xdata, y1data, 1)
        polynomial = numpy.poly1d(coeffs)

        x_fit = numpy.linspace(min(xdata), max(xdata))
        y_fit = polynomial(x_fit)

        scatter_nass = self.ax.scatter(xdata, y1data, c="darkblue", s=10)
        reg_nass = self.ax.plot(x_fit, y_fit, color="darkblue", linewidth=2)[0]
        self.nass_plots = [scatter_nass, reg_nass]

        # NASS_dv R^2 calculation
        y_pred = polynomial(xdata)
        ssr = numpy.sum((y_pred - numpy.mean(y1data)) ** 2)
        sst = numpy.sum((y1data - numpy.mean(y1data)) ** 2)
        r_squared = ssr / sst

        self.nass_legend = [
            f"NASS, $R^2= {r_squared:.2f}$",
            f"$y = {str(polynomial).strip()}$",
        ]

        # TOT_dv
        coeffs_e = numpy.polyfit(xdata, y2data, 1)
        polynomial_e = numpy.poly1d(coeffs_e)

        x_fit_e = numpy.linspace(min(xdata), max(xdata))
        y_fit_e = polynomial_e(x_fit_e)

        scatter_tot = self.ax.scatter(xdata, y2data, c="red", s=10)
        reg_tot = self.ax.plot(x_fit_e, y_fit_e, color="red", linewidth=2)[0]
        self.tot_plots = [scatter_tot, reg_tot]

        y_pred_e = polynomial_e(xdata)
        ssr_e = numpy.sum((y_pred_e - numpy.mean(y2data)) ** 2)
        sst_e = numpy.sum((y2data - numpy.mean(y2data)) ** 2)
        r_squared_e = ssr_e / sst_e

        self.tot_legend = [
            f"TOT, $R^2= {r_squared_e:.2f}$",
            f"$y = {str(polynomial_e).strip()}$",
        ]

        # Case ID labels
        self.nass_labels = []
        self.tot_labels = []
        for i, case_id in enumerate(case_ids):
            nass_label = self.ax.annotate(case_id, (xdata[i], y1data[i]), size=8)
            nass_label.draggable(True)
            self.nass_labels.append(nass_label)
            tot_label = self.ax.annotate(case_id, (xdata[i], y2data[i]), size=8)
            tot_label.draggable(True)
            self.tot_labels.append(tot_label)

        self.ax.set_xlabel("Crush (inches)", fontsize=20)
        self.ax.set_ylabel("Change in Velocity (mph)", fontsize=20)
        self.ax.legend(self.nass_legend + self.tot_legend, loc="upper left")

        self.canvas.draw()

        self.update_nass_data()
        self.update_tot_data()

        crush_est = numpy.array([0, 1.0])
        print(polynomial(crush_est))
        print(polynomial_e(crush_est))
        # print(df)

    def scrape_complete(self):
        if not len(self.model.data_list):
            self.ui.summaryEdit.append("Scrape complete. No data found.")
        else:
            self.ui.summaryEdit.append("Scrape complete.")
