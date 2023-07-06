import logging
import os
from pathlib import Path

from PyQt6.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

import matplotlib
import matplotlib.pyplot as plt
import numpy
import pandas
import sklearn.metrics


class WorkerSignals(QObject):
    finished = pyqtSignal()


class ScatterplotWorker(QRunnable):
    def __init__(self, data: list[dict], path: Path):
        super().__init__()
        self.data = data
        self.signals = WorkerSignals()
        self.path = path

    @pyqtSlot()
    def run(self):
        matplotlib.use("agg")
        matplotlib.rcParams["font.family"] = "Arial, sans-serif"
        logging.getLogger("matplotlib").setLevel(logging.WARNING)

        data_frame = pandas.DataFrame(self.data)
        data_frame = data_frame[["case_id", "c_bar", "NASS_dv", "NASS_vc", "TOT_dv"]]
        data_frame = data_frame.apply(pandas.to_numeric, errors="coerce")

        # dv_plot_e = dfn.plot.scatter(x="c_bar", y="TOT_dv", c='r',figsize=(20,12))
        dv_plot = data_frame.plot.scatter(
            x="c_bar", y="NASS_dv", c="r", figsize=(20, 12)
        )

        fit = numpy.polyfit(data_frame.c_bar, data_frame.NASS_dv, 1)
        fit_e = numpy.polyfit(data_frame.c_bar, data_frame.TOT_dv, 1)

        slope = fit[0]
        # slope_e = fit_e[0]

        intercept = fit[1]
        # intercept_e = fit_e[1]

        s_eq = "Y = " + str(round(slope, 1)) + "X + " + str(round(intercept, 1))
        # s_eq_e = "Y = " + str(round(slope_e, 1)) + "X + " + str(round(intercept_e, 1))

        # regression lines
        plt.plot(
            data_frame.c_bar,
            fit[0] * data_frame.c_bar + fit[1],
            color="darkblue",
            linewidth=2,
        )
        # plt.plot(dfn.c_bar, fit_e[0] * dfn.c_bar + fit_e[1], color='red', linewidth=2)

        predict = numpy.poly1d(fit)
        predict_e = numpy.poly1d(fit_e)
        r2 = str(
            round(
                (
                    sklearn.metrics.r2_score(
                        data_frame.NASS_dv, predict(data_frame.c_bar)
                    )
                ),
                2,
            )
        )
        # r2_e = str(round((sklearn.metrics.r2_score(dfn.TOT_dv, predict_e(dfn.c_bar))), 2))

        # legend, title and labels.
        # plt.legend(labels=['NASS, ' + 'r$\mathregular{^2}$ value = ' + r2 + ' - ' + s_eq, 'Total, ' + 'r$\mathregular{^2}$ value = ' + r2_e + ' - ' + s_eq_e], fontsize=14)
        plt.legend(
            labels=["NASS, " + "r$\mathregular{^2}$ value = " + r2 + " - " + s_eq],
            fontsize=14,
        )
        plt.xlabel("Crush (inches)", size=24)
        plt.ylabel("Change in Velocity (mph)", size=24)
        for i, label in enumerate(data_frame["case_id"]):
            plt.text(data_frame.c_bar[i], data_frame.NASS_dv[i], label)
        # for i, label in enumerate(df.index):
        #    plt.text(dfn.c_bar[i], dfn.TOT_dv[i],label)

        os.makedirs(self.path, exist_ok=True)
        plt.savefig(self.path / "NASS_Analysis.png", format="png", dpi=150)
        plt.close()

        crush_est = numpy.array([0, 1.0])
        # print(predict(crush_est))
        # print(predict_e(crush_est))
        # print(df)

        self.signals.finished.emit()
