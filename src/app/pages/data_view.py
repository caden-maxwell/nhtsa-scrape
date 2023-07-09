import csv
import logging
import os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout

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

        self.figure = Figure(figsize=(16, 12), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        self.ui.scatterTab.setLayout(layout)

        self.xdata = []
        self.y1data = []
        self.y2data = []

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

        all_data = self.model.all_data()
        case_ids = []
        for event in all_data:
            case_ids.append(event["case_id"])
            self.xdata.append(event["c_bar"])
            self.y1data.append(event["NASS_dv"])
            self.y2data.append(event["TOT_dv"])

        if len(self.xdata) < 2:
            self.canvas.draw()
            return

        # NASS_dv plot, fit, and r^2
        self.ax.scatter(self.xdata, self.y1data, c="r", s=10)

        coeffs = numpy.polyfit(self.xdata, self.y1data, 1)
        polynomial = numpy.poly1d(coeffs)

        x_fit = numpy.linspace(min(self.xdata), max(self.xdata))
        y_fit = polynomial(x_fit)

        self.ax.plot(x_fit, y_fit, color="darkblue", linewidth=1)

        y_pred = polynomial(self.xdata)
        ssr = numpy.sum((y_pred - numpy.mean(self.y1data)) ** 2)
        sst = numpy.sum((self.y1data - numpy.mean(self.y1data)) ** 2)
        r_squared = ssr / sst

        leg = self.ax.legend(
            [
                f"NASS, y = {str(polynomial).strip()}\nR-squared = {r_squared:.2f}",
            ],
            loc="upper left",
        )
        leg.set_draggable(True)

        for i, case_id in enumerate(case_ids):
            self.ax.text(self.xdata[i], self.y1data[i], case_id, fontsize=8)

        # TOT_dv plot and fit
        # self.ax.scatter(self.xdata, self.y2data, c="b", s=10)

        coeffs_e = numpy.polyfit(self.xdata, self.y2data, 1)
        polynomial_e = numpy.poly1d(coeffs_e)

        x_fit_e = numpy.linspace(min(self.xdata), max(self.xdata))
        y_fit_e = polynomial_e(x_fit_e)

        # self.ax.plot(x_fit_e, y_fit_e, color='red')

        y_pred_e = polynomial_e(self.xdata)
        ssr_e = numpy.sum((y_pred_e - numpy.mean(self.y2data)) ** 2)
        sst_e = numpy.sum((self.y2data - numpy.mean(self.y2data)) ** 2)
        r_squared_e = ssr_e / sst_e

        # leg_e = self.ax.legend(
        #     [
        #         f"NASS, y = {str(polynomial).strip()}\nR-squared = {r_squared:.2f}",
        #         f"TOT, y = {str(polynomial_e).strip()}\nR-squared = {r_squared_e:.2f}",
        #     ],
        #     loc="upper left",
        # )
        # leg_e.set_draggable(True)

        # for i, label in enumerate(df.index):
        #    plt.text(dfn.c_bar[i], dfn.TOT_dv[i],label)

        self.ax.set_xlabel("Crush (inches)", fontsize=12)
        self.ax.set_ylabel("Change in Velocity (mph)", fontsize=12)

        self.canvas.draw()

        crush_est = numpy.array([0, 1.0])
        print(polynomial(crush_est))
        print(polynomial_e(crush_est))
        # print(df)

    def scrape_complete(self):
        if not len(self.model.data_list):
            self.ui.summaryEdit.append("Scrape complete. No data found.")
        else:
            self.ui.summaryEdit.append("Scrape complete.")

    ### TODO: Add ability to toggle Total_dv data on scatterplot
    ### TODO: Add ability to toggle case_id labels on scatterplot
