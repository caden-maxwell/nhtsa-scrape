import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QWidget

from matplotlib import style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy

from app.models import ProfileEvents
from app.ui.ScatterTab_ui import Ui_ScatterTab

logging.getLogger("matplotlib").setLevel(logging.WARNING)
style.use("seaborn-deep")


class ScatterTab(QWidget):
    def __init__(self, model: ProfileEvents, data_dir: Path):
        super().__init__()
        self.ui = Ui_ScatterTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = model
        self.data_dir = data_dir

        self.ui.nassDataBtn.clicked.connect(
            lambda: self.btn_update(self.update_nass_data)
        )
        self.ui.nassLabelBtn.clicked.connect(
            lambda: self.btn_update(self.update_nass_labels)
        )
        self.ui.totalDataBtn.clicked.connect(
            lambda: self.btn_update(self.update_tot_data)
        )
        self.ui.totalLabelBtn.clicked.connect(
            lambda: self.btn_update(self.update_tot_labels)
        )

        self.figure = Figure(tight_layout=True, dpi=60)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        toolbar = CustomToolbar(self.canvas, self)
        toolbar.setStyleSheet("background-color: none;")

        self.ui.scatterLayout.addWidget(toolbar)
        self.ui.scatterLayout.addWidget(self.canvas)

        self.nass_plots = []
        self.nass_labels = []
        self.nass_legend = []
        self.tot_plots = []
        self.tot_labels = []
        self.tot_legend = []

    def showEvent(self, event) -> None:
        self.update_plot()
        return super().showEvent(event)

    def save_figure(self):
        os.makedirs(self.data_dir, exist_ok=True)
        path = self.data_dir / "scatterplot.png"
        i = 1
        while path.exists():
            path = self.data_dir / f"scatterplot({i}).png"
            i += 1

        self.figure.savefig(
            path,
            format="png",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.75,
        )
        self.logger.info(f"Saved figure to {path}")

    def btn_update(self, btn_func):
        btn_func()
        self.canvas.draw()

    def update_nass_data(self):
        checked = self.ui.nassDataBtn.isChecked()
        for plot in self.nass_plots:
            plot.set_visible(checked)
        self.ui.nassLabelBtn.setEnabled(checked)

        self.update_nass_labels()
        self.update_legend()

    def update_nass_labels(self):
        visible = self.ui.nassLabelBtn.isChecked() and self.ui.nassLabelBtn.isEnabled()
        for label in self.nass_labels:
            label.set_visible(visible)

    def update_tot_data(self):
        checked = self.ui.totalDataBtn.isChecked()
        for plot in self.tot_plots:
            plot.set_visible(checked)
        self.ui.totalLabelBtn.setEnabled(checked)

        self.update_tot_labels()
        self.update_legend()

    def update_tot_labels(self):
        visible = (
            self.ui.totalLabelBtn.isChecked() and self.ui.totalLabelBtn.isEnabled()
        )
        for label in self.tot_labels:
            label.set_visible(visible)

    def update_legend(self):
        if legend := self.ax.get_legend():
            legend.remove()
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
        self.ax.get_legend().set_draggable(True)

    def update_plot(self):
        if not self.isVisible():
            return
        self.ax.clear()

        xdata = []
        y1data = []
        y2data = []
        case_ids = []
        nass_vc = []
        for event in self.model.all_events():
            if not event["ignored"]:
                xdata.append(event["c_bar"])
                y1data.append(event["NASS_dv"])
                y2data.append(event["TOT_dv"])
                case_ids.append(event["case_id"])
                nass_vc.append(event["NASS_vc"])

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
        r_squared = 0
        if sst != 0:
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
        self.ax.legend(
            self.nass_legend + self.tot_legend, loc="upper left"
        ).set_draggable(True)

        self.update_nass_data()
        self.update_tot_data()

        self.canvas.draw()

        crush_est = numpy.array([0, 1.0])
        print(polynomial(crush_est))
        print(polynomial_e(crush_est))
        print(
            f"{'Case ID':^12}{'c_bar':^10}{'NASS_vc':^10}{'NASS_dv':^10}{'TOT_dv':^10}"
        )
        for i, case_id in enumerate(case_ids):
            print(
                f"{case_id:^12}{xdata[i]:^10.2f}{nass_vc[i]:^10.2f}{y1data[i]:^10.2f}{y2data[i]:^10.2f}"
            )


class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.parent = parent

    def save_figure(self, *args):
        self.parent.save_figure()
