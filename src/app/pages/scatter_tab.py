import logging
import os
from pathlib import Path
from matplotlib import use as mpl_use

mpl_use("qtagg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from PyQt6.QtWidgets import QMessageBox

from app.pages import BaseTab
from app.pages.utils import open_file
from app.models import DatabaseHandler, ScatterPlotModel, Profile
from app.ui import Ui_ScatterTab

logging.getLogger("matplotlib").setLevel(logging.WARNING)
sns.set_style("ticks")


class ScatterTab(BaseTab):
    def __init__(self, db_handler: DatabaseHandler, profile: Profile, data_dir: Path):
        super().__init__()
        self.ui = Ui_ScatterTab()
        self.ui.setupUi(self)
        self._logger = logging.getLogger(__name__)

        self._model = ScatterPlotModel(db_handler, profile)
        self._data_dir = data_dir

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

        self.figure, self.ax = plt.subplots()
        self.ax: plt.Axes

        self.figure.tight_layout()
        self.figure.set_dpi(60)

        self.canvas = FigureCanvas(self.figure)
        toolbar = CustomToolbar(self.canvas, self)

        self.ui.scatterLayout.addWidget(toolbar)
        self.ui.scatterLayout.addWidget(self.canvas)

        self.nass_plots: list[plt.Artist] = []
        self.nass_labels: list[plt.Annotation] = []
        self.nass_legend: list[str] = []
        self.tot_plots: list[plt.Artist] = []
        self.tot_labels: list[plt.Annotation] = []
        self.tot_legend: list[str] = []

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

    def refresh(self):
        self._model.refresh_data()
        self.ax.clear()

        case_ids, x_data, y1_data, y2_data = self._model.get_data()
        if len(x_data) < 2:
            self.canvas.draw()
            return

        # NASS_dv
        coeffs = np.polyfit(x_data, y1_data, 1)
        polynomial = np.poly1d(coeffs)

        x_fit = np.linspace(min(x_data), max(x_data))
        y_fit = polynomial(x_fit)

        scatter_nass = self.ax.scatter(x_data, y1_data, c="darkblue", s=10)
        reg_nass = self.ax.plot(x_fit, y_fit, color="darkblue", linewidth=2)[0]
        self.nass_plots = [scatter_nass, reg_nass]

        # NASS_dv R^2 calculation
        y_pred = polynomial(x_data)
        ssr = np.sum((y_pred - np.mean(y1_data)) ** 2)
        sst = np.sum((y1_data - np.mean(y1_data)) ** 2)
        r_squared = 0
        if sst != 0:
            r_squared = ssr / sst

        self.nass_legend = [
            f"NASS, $R^2= {r_squared:.2f}$",
            f"$y = {str(polynomial).strip()}$",
        ]

        # TOT_dv
        coeffs_e = np.polyfit(x_data, y2_data, 1)
        polynomial_e = np.poly1d(coeffs_e)

        x_fit_e = np.linspace(min(x_data), max(x_data))
        y_fit_e = polynomial_e(x_fit_e)

        scatter_tot = self.ax.scatter(x_data, y2_data, c="red", s=10)
        reg_tot = self.ax.plot(x_fit_e, y_fit_e, color="red", linewidth=2)[0]
        self.tot_plots = [scatter_tot, reg_tot]

        # TOT_dv R^2 calculation
        y_pred_e = polynomial_e(x_data)
        ssr_e = np.sum((y_pred_e - np.mean(y2_data)) ** 2)
        sst_e = np.sum((y2_data - np.mean(y2_data)) ** 2)
        r_squared_e = ssr_e / sst_e

        self.tot_legend = [
            f"TOT, $R^2= {r_squared_e:.2f}$",
            f"$y = {str(polynomial_e).strip()}$",
        ]

        # Case ID labels
        self.nass_labels = []
        self.tot_labels = []
        for i, case_id in enumerate(case_ids):
            nass_label = self.ax.annotate(case_id, (x_data[i], y1_data[i]), size=8)
            nass_label.draggable(True)
            self.nass_labels.append(nass_label)
            tot_label = self.ax.annotate(case_id, (x_data[i], y2_data[i]), size=8)
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

    def save_figure(self):
        os.makedirs(self._data_dir, exist_ok=True)
        path = self._data_dir / "scatterplot.png"
        i = 1
        while path.exists():
            path = self._data_dir / f"scatterplot({i}).png"
            i += 1

        self.figure.savefig(
            path,
            format="png",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.75,
        )
        self._logger.info(f"Figure saved to:\n{path}")
        box = QMessageBox()
        box.setWindowTitle("Saved")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText("Figure saved to:")
        box.setInformativeText(str(path))
        box.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open
        )
        box.setDefaultButton(QMessageBox.StandardButton.Ok)
        button_result = box.exec()

        if button_result == QMessageBox.StandardButton.Open:
            open_file(self._data_dir, self)


class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent: ScatterTab):
        super().__init__(canvas, parent)
        self.parent = parent

    def save_figure(self, *args):
        self.parent.save_figure()
