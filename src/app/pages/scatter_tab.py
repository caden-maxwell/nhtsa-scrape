import logging
from pathlib import Path

from PyQt6.QtCharts import (
    QScatterSeries,
    QChart,
    QChartView,
    QValueAxis,
    QLineSeries,
    QLegend,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from . import BaseTab
from app.models import ScatterPlotModel, DatabaseHandler
from app.ui.ScatterTab_ui import Ui_ScatterTab


class ScatterTab(BaseTab):
    def __init__(self, db_handler: DatabaseHandler, profile_id, data_dir: Path):
        super().__init__()
        self.ui = Ui_ScatterTab()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.model = ScatterPlotModel(db_handler, profile_id)
        self.data_dir = data_dir
        self.profile_id = profile_id

        self.chart = QChart()

        # Set up axes
        self.x_axis = QValueAxis()
        self.x_axis.setTitleText("Crush (inches)")
        self.x_axis.setTitleFont(QFont("Segoe UI", 20))
        self.x_axis.setLabelsFont(QFont("Segoe UI", 10))
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickAnchor(0)
        self.x_axis.setTickInterval(1.0)
        self.x_axis.setGridLineVisible(False)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)

        self.y_axis = QValueAxis()
        self.y_axis.setTitleText("Change in Velocity (mph)")
        self.y_axis.setTitleFont(QFont("Segoe UI", 20))
        self.y_axis.setLabelsFont(QFont("Segoe UI", 10))
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickAnchor(0)
        self.y_axis.setTickInterval(1.0)
        self.y_axis.setGridLineVisible(False)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)

        # Set up scatterplot series
        self.scatter_nass_dv = QScatterSeries()
        self.scatter_nass_dv.setName("Series 1")
        self.scatter_nass_dv.setMarkerShape(
            QScatterSeries.MarkerShape.MarkerShapeRotatedRectangle
        )
        self.scatter_nass_dv.setMarkerSize(8.0)
        self.scatter_nass_dv.setColor(Qt.GlobalColor.blue)
        self.chart.addSeries(self.scatter_nass_dv)
        self.scatter_nass_dv.attachAxis(self.x_axis)
        self.scatter_nass_dv.attachAxis(self.y_axis)

        self.scatter_series2 = QScatterSeries()
        self.scatter_series2.setName("Series 2")
        self.scatter_series2.setMarkerShape(
            QScatterSeries.MarkerShape.MarkerShapeRotatedRectangle
        )
        self.scatter_series2.setMarkerSize(8.0)
        self.scatter_series2.setColor(Qt.GlobalColor.red)
        self.chart.addSeries(self.scatter_series2)
        self.scatter_series2.attachAxis(self.x_axis)
        self.scatter_series2.attachAxis(self.y_axis)

        # Set up regression lines
        self.line_series1 = QLineSeries()
        self.line_series1.setName("Regression 1")
        self.line_series1.setColor(Qt.GlobalColor.blue)
        self.chart.addSeries(self.line_series1)
        self.line_series1.attachAxis(self.x_axis)
        self.line_series1.attachAxis(self.y_axis)

        self.line_series2 = QLineSeries()
        self.line_series2.setName("Regression 2")
        self.line_series2.setColor(Qt.GlobalColor.red)
        self.chart.addSeries(self.line_series2)
        self.line_series2.attachAxis(self.x_axis)
        self.line_series2.attachAxis(self.y_axis)

        # Set up legend
        self.legend = self.chart.legend()
        self.legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeFromSeries)
        self.legend.setBackgroundVisible(True)
        self.legend.setOpacity(0.8)
        self.legend.setLabelColor(QColor("black"))

        self.legend.detachFromChart()
        self.legend.setInteractive(True)

        self.chart_view = QChartView(self.chart)
        self.ui.chartLayout.addWidget(self.chart_view)

        self.update_plot()

    def refresh_tab(self):
        self.model.refresh_data()
        self.update_plot()

    def update_plot(self):
        self.scatter_nass_dv.clear()
        self.scatter_series2.clear()
        self.line_series1.clear()
        self.line_series2.clear()

        case_ids, x_data, y1_data, y2_data = self.model.get_data()

        for i, case_id in enumerate(case_ids):
            self.scatter_nass_dv.append(x_data[i], y1_data[i])

        if not len(x_data):
            return

        x_min = min(x_data)
        self.x_axis.setTickAnchor(int(x_min))

        x_max = max(x_data)
        x_range = x_max - x_min
        x_min -= x_range * 0.05
        x_max += x_range * 0.05
        self.x_axis.setRange(x_min, x_max)
        self.x_axis.setTickInterval(round_to_nearest_half(x_range / 9))

        y1_min = min(y1_data)
        self.y_axis.setTickAnchor(int(y1_min))

        y1_max = max(y1_data)
        y1_range = y1_max - y1_min
        y1_min -= y1_range * 0.05
        y1_max += y1_range * 0.05
        self.y_axis.setRange(y1_min, y1_max)
        self.y_axis.setTickInterval(round_to_nearest_half(y1_range / 8))


def round_to_nearest_half(number):
    return round(number * 2) / 2
