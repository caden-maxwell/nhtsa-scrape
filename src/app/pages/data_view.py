import csv
import logging

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QDialog

from app.models import ProfileEvents
from app.ui.ExitDataViewDialog_ui import Ui_ExitDialog
from app.ui.DataView_ui import Ui_DataView

import numpy
import pandas
import matplotlib.pyplot as plt
import sklearn.metrics
from PIL import Image, ImageDraw


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

    def showEvent(self, event):
        self.model.refresh_data()
        self.ui.listView.clearSelection()
        return super().showEvent(event)

    def handle_exit_button_clicked(self):
        self.exit_dialog_controller = ExitDataViewDialog()
        self.exit_dialog_controller.exec()
        self.exited.emit()

    def open_item_details(self, index):
        print(f"Opening item details for index {index.row()}")

    @pyqtSlot(dict)
    def add_event(self, event):
        self.model.add_data(event)
        self.calculate()

    def scrape_complete(self):
        if not len(self.model.data_list):
            self.ui.textEdit.append("Scrape complete. No data found.")
            return

    def calculate(self):
        caseid_path = ""
        contents = []
        x = []
        y_nass = []
        y_total = []
        return
        file = f"{self.search_payload['ddlStartModelYear']}_{self.search_payload['ddlEndModelYear']}_{self.search_payload['ddlMake']}_{self.search_payload['ddlModel']}_{self.search_payload['ddlPrimaryDamage']}.csv"
        for cse in contents:
            # average crush in inches
            c_bar = (
                0.393701
                * ((cse["crush"][0] + cse["crush"][5]) * 0.5 + sum(cse["crush"][1:4]))
                / 5.0
            )
            cse["c_bar"] = c_bar
            # NASS DV in MPH
            NASS_dv = cse["total_dv"] * 0.621371
            cse["NASS_dv"] = NASS_dv
            # Vehicle Weights in LBS
            voi_wt = cse["curbweight"] * 2.20462
            a_wt = cse["a_curbweight"] * 2.20462
            NASS_vc = NASS_dv / (a_wt / (voi_wt + a_wt))
            cse["NASS_vc"] = NASS_vc
            e = 0.5992 * numpy.exp(
                -0.1125 * NASS_vc + 0.003889 * NASS_vc**2 - 0.0001153 * NASS_vc**3
            )
            cse["e"] = e
            TOT_dv = NASS_dv * (1.0 + e)
            cse["TOT_dv"] = TOT_dv
            x.append(c_bar)
            y_nass.append(NASS_dv)
            y_total.append(TOT_dv)
        slope, intercept = numpy.polyfit(x, y_nass, 1)

        i = []
        [i.append(cse["image"]) for cse in contents]
        df_original = pandas.DataFrame(contents, index=i)

        df = df_original[["caseid", "c_bar", "NASS_dv", "NASS_vc", "TOT_dv"]]
        df_original = df_original[
            [
                "caseid",
                "casenum",
                "vehnum",
                "year",
                "make",
                "model",
                "curbweight",
                "damloc",
                "underride",
                "edr",
                "total_dv",
                "long_dv",
                "lateral_dv",
                "smashl",
                "crush",
                "a_vehnum",
                "a_year",
                "a_make",
                "a_model",
                "a_curbweight",
                "image",
                "c_bar",
                "NASS_dv",
                "NASS_vc",
                "e",
                "TOT_dv",
                "summary",
            ]
        ]

        # Scatter plots.
        dfn = df.apply(pandas.to_numeric, errors="coerce")

        # dv_plot_e = dfn.plot.scatter(x="c_bar", y="TOT_dv", c='r',figsize=(16,12))
        dv_plot = dfn.plot.scatter(x="c_bar", y="NASS_dv", c="r", figsize=(16, 12))

        fit = numpy.polyfit(dfn.c_bar, dfn.NASS_dv, 1)
        fit_e = numpy.polyfit(dfn.c_bar, dfn.TOT_dv, 1)

        slope = fit[0]
        slope_e = fit_e[0]

        intercept = fit[1]
        intercept_e = fit_e[1]

        s_eq = "Y = " + str(round(slope, 1)) + "X + " + str(round(intercept, 1))
        s_eq_e = "Y = " + str(round(slope_e, 1)) + "X + " + str(round(intercept_e, 1))

        # regression lines
        plt.plot(dfn.c_bar, fit[0] * dfn.c_bar + fit[1], color="darkblue", linewidth=2)
        # plt.plot(dfn.c_bar, fit_e[0] * dfn.c_bar + fit_e[1], color='red', linewidth=2)

        predict = numpy.poly1d(fit)
        predict_e = numpy.poly1d(fit_e)
        r2 = str(round((sklearn.metrics.r2_score(dfn.NASS_dv, predict(dfn.c_bar))), 2))
        r2_e = str(
            round((sklearn.metrics.r2_score(dfn.TOT_dv, predict_e(dfn.c_bar))), 2)
        )

        # legend, title and labels.
        # plt.legend(labels=['NASS, ' + 'r$\mathregular{^2}$ value = ' + r2 + ' - ' + s_eq, 'Total, ' + 'r$\mathregular{^2}$ value = ' + r2_e + ' - ' + s_eq_e], fontsize=14)
        plt.legend(
            labels=["NASS, " + "r$\mathregular{^2}$ value = " + r2 + " - " + s_eq],
            fontsize=14,
        )
        plt.xlabel("Crush (inches)", size=24)
        plt.ylabel("Change in Velocity (mph)", size=24)
        for i, label in enumerate(df["caseid"]):
            plt.text(dfn.c_bar[i], dfn.NASS_dv[i], label)
        # for i, label in enumerate(df.index):
        #    plt.text(dfn.c_bar[i], dfn.TOT_dv[i],label)

        plt.savefig(caseid_path + "//" + "NASS_Analysis.png", dpi=150)

        crush_est = numpy.array([0, 1.0])
        print(predict(crush_est))
        print(predict_e(crush_est))
        print(df)

        # Re-Analyze Info - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in df.index:
            s = (
                "Caseid: "
                + str(df.loc[i].caseid)
                + ". NASSDV = "
                + str(df.loc[i].NASS_dv)
            )
            img = Image.open(caseid_path + "//" + i + ".jpg")
            draw = ImageDraw.Draw(img)
            # draw.text((0, 0),s,(220,20,60),font=font)
            img.show()
            # plt.text(25, 25, s, fontsize=18, bbox=dict(facecolor='white', edgecolor='red', linewidth=2))
            g = input(s + " " "Select: [SA]ve case, [DE]lete Case, [ST]op: ")
            img.close()
            if "de" in g.lower():
                df = df.drop(index=i)
                df_original = df_original.drop(index=i)
                continue
            elif "st" in g.lower():
                break
            else:
                continue
        # Re-Analyze Info - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        dfn = df.apply(pandas.to_numeric, errors="coerce")

        # dv_plot_e = dfn.plot.scatter(x="c_bar", y="TOT_dv", c='r',figsize=(16,12))
        dv_plot = dfn.plot.scatter(x="c_bar", y="NASS_dv", c="r", figsize=(16, 12))

        fit = numpy.polyfit(dfn.c_bar, dfn.NASS_dv, 1)
        fit_e = numpy.polyfit(dfn.c_bar, dfn.TOT_dv, 1)

        slope = fit[0]
        slope_e = fit_e[0]

        intercept = fit[1]
        intercept_e = fit_e[1]

        s_eq = "Y = " + str(round(slope, 1)) + "X + " + str(round(intercept, 1))
        s_eq_e = "Y = " + str(round(slope_e, 1)) + "X + " + str(round(intercept_e, 1))

        # regression lines
        plt.plot(dfn.c_bar, fit[0] * dfn.c_bar + fit[1], color="darkblue", linewidth=2)
        # plt.plot(dfn.c_bar, fit_e[0] * dfn.c_bar + fit_e[1], color='red', linewidth=2)

        predict = numpy.poly1d(fit)
        predict_e = numpy.poly1d(fit_e)
        r2 = str(round((sklearn.metrics.r2_score(dfn.NASS_dv, predict(dfn.c_bar))), 2))
        r2_e = str(
            round((sklearn.metrics.r2_score(dfn.TOT_dv, predict_e(dfn.c_bar))), 2)
        )

        # legend, title and labels.
        # plt.legend(labels=['NASS, ' + 'r$\mathregular{^2}$ value = ' + r2 + ' - ' + s_eq, 'Total, ' + 'r$\mathregular{^2}$ value = ' + r2_e + ' - ' + s_eq_e], fontsize=14)
        plt.legend(
            labels=["NASS, " + "r$\mathregular{^2}$ value = " + r2 + " - " + s_eq],
            fontsize=14,
        )
        plt.xlabel("Crush (inches)", size=24)
        plt.ylabel("Change in Velocity (mph)", size=24)
        for i, label in enumerate(df["caseid"]):
            plt.text(dfn.c_bar[i], dfn.NASS_dv[i], label)
        # for i, label in enumerate(df.index):
        #    plt.text(dfn.c_bar[i], dfn.TOT_dv[i],label)

        plt.savefig(caseid_path + "//" + "NASS_Analysis.png", dpi=150)

        crush_est = numpy.array([0, 1.0])
        print(predict(crush_est))
        print(predict_e(crush_est))
        print(df)

        df_original.to_csv(caseid_path + "//" + file)
        f = open(caseid_path + "//" + file, "a")
        writer = csv.writer(f)

        csestr = ""
        end = len(df["caseid"]) - 1
        for i in range(len(df["caseid"])):
            cnum = df["caseid"].iloc[i]
            if i == end:
                csestr = csestr + "and " + cnum + "."
            else:
                csestr = csestr + cnum + ", "

        temp1 = df.sort_values(by=["NASS_dv"])
        minval = str(round(temp1.iloc[0]["NASS_dv"], 1))
        mincase = temp1.iloc[0]["caseid"]
        maxval = str(round(temp1.iloc[end]["NASS_dv"], 1))
        maxcase = temp1.iloc[end]["caseid"]

        dvstr = f"Among these cases, the changes in velocity ranged from as low as {minval} mph ({mincase}) to as high as {maxval} mph ({maxcase})."

        par = csestr + dvstr
        writer.writerows([[], [par]])
        f.close()


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
