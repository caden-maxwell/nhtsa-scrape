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
from PyQt6.QtGui import QFont, QColor, QPainter, QMouseEvent
import numpy

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

        chart = QChart()

        # Set up x-axis
        self.x_axis = QValueAxis()
        self.x_axis.setTitleText("Crush (inches)")
        self.x_axis.setTitleFont(QFont("DejaVu Sans", 20))
        self.x_axis.setLabelsFont(QFont("DejaVu Sans", 10))
        self.x_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.x_axis.setTickAnchor(0)
        self.x_axis.setTickInterval(1.0)
        self.x_axis.setGridLineVisible(False)
        chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)

        # Set up y-axis
        self.y_axis = QValueAxis()
        self.y_axis.setTitleText("Change in Velocity (mph)")
        self.y_axis.setTitleFont(QFont("DejaVu Sans", 20))
        self.y_axis.setLabelsFont(QFont("DejaVu Sans", 10))
        self.y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        self.y_axis.setTickAnchor(0)
        self.y_axis.setTickInterval(1.0)
        self.y_axis.setGridLineVisible(False)
        chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)

        # Set up scatterplot series for NASS_DV
        self.scatter_nass_dv = QScatterSeries()
        self.scatter_nass_dv.setName("Series 1")
        self.scatter_nass_dv.setMarkerShape(
            QScatterSeries.MarkerShape.MarkerShapeRotatedRectangle
        )
        self.scatter_nass_dv.setMarkerSize(8.0)
        self.scatter_nass_dv.setColor(Qt.GlobalColor.darkBlue)
        chart.addSeries(self.scatter_nass_dv)
        self.scatter_nass_dv.attachAxis(self.x_axis)
        self.scatter_nass_dv.attachAxis(self.y_axis)

        # Set up scatterplot series for TOT_DV
        self.scatter_tot_dv = QScatterSeries()
        self.scatter_tot_dv.setName("Series 2")
        self.scatter_tot_dv.setMarkerShape(
            QScatterSeries.MarkerShape.MarkerShapeRotatedRectangle
        )
        self.scatter_tot_dv.setMarkerSize(8.0)
        self.scatter_tot_dv.setColor(Qt.GlobalColor.red)
        chart.addSeries(self.scatter_tot_dv)
        self.scatter_tot_dv.attachAxis(self.x_axis)
        self.scatter_tot_dv.attachAxis(self.y_axis)

        # Set up regression lines
        self.line_series1 = QLineSeries()
        self.line_series1.setName("Regression 1")
        self.line_series1.setColor(Qt.GlobalColor.darkBlue)
        pen = self.line_series1.pen()
        pen.setWidth(2)
        self.line_series1.setPen(pen)
        chart.addSeries(self.line_series1)
        self.line_series1.attachAxis(self.x_axis)
        self.line_series1.attachAxis(self.y_axis)

        self.line_series2 = QLineSeries()
        self.line_series2.setName("Regression 2")
        self.line_series2.setColor(Qt.GlobalColor.red)
        pen = self.line_series2.pen()
        pen.setWidth(2)
        self.line_series2.setPen(pen)
        chart.addSeries(self.line_series2)
        self.line_series2.attachAxis(self.x_axis)
        self.line_series2.attachAxis(self.y_axis)

        # Set up legend
        chart.legend().setMarkerShape(QLegend.MarkerShape.MarkerShapeFromSeries)
        chart.legend().setBackgroundVisible(True)
        chart.legend().setOpacity(0.8)
        chart.legend().setLabelColor(QColor("black"))
        chart.legend().detachFromChart()
        chart.legend().setInteractive(True)

        # Set up chart view
        self.chart_view = CustomChartView(chart)
        self.ui.chartLayout.addWidget(self.chart_view)

        self.update_plot()

    def refresh_tab(self):
        self.model.refresh_data()
        self.update_plot()

    def update_plot(self):
        self.scatter_nass_dv.clear()
        self.scatter_tot_dv.clear()
        self.line_series1.clear()
        self.line_series2.clear()

        case_ids, x_data, y1_data, y2_data = self.model.get_data()

        for i, case_id in enumerate(case_ids):
            self.scatter_nass_dv.append(x_data[i], y1_data[i])

        if len(x_data) < 1:
            return

        x_min = min(x_data)
        x_max = max(x_data)

        if len(x_data) > 1:
            slope1, intercept1 = numpy.polyfit(x_data, y1_data, 1)

            self.line_series1.append(x_min, slope1 * x_min + intercept1)
            self.line_series1.append(x_max, slope1 * x_max + intercept1)

        self.x_axis.setTickAnchor(int(x_min))

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


class CustomChartView(QChartView):
    def __init__(self, chart):
        super().__init__(chart)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.IntersectsItemBoundingRect)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position()  # Get cursor position
        chart = self.chart()  # Get the associated chart

        if chart and chart.plotArea().contains(pos):
            # Convert the cursor position to chart values

            chart_point = chart.mapToValue(pos, chart.series()[0])

            # Update the coordinates somewhere on the chart (e.g., title or annotation)
            self.update_coordinates(chart_point.x(), chart_point.y())

        return super().mouseMoveEvent(event)

    def update_coordinates(self, x, y):
        pass
