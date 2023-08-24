import logging

from . import DatabaseHandler


class ScatterPlotModel:
    def __init__(self, db_handler: DatabaseHandler, profile_id: int):
        self.logger = logging.getLogger(__name__)

        self.db_handler = db_handler
        self.profile_id = profile_id

        self._case_ids = []
        self._x_data = []
        self._y1_data = []
        self._y2_data = []
        self.refresh_data()

    def get_data(self):
        return self._case_ids, self._x_data, self._y1_data, self._y2_data

    def refresh_data(self):
        self._case_ids = []
        self._x_data = []
        self._y1_data = []
        self._y2_data = []
        self._data_points = self.db_handler.get_events(
            self.profile_id, include_ignored=False
        )

        for data_point in self._data_points:
            self._case_ids.append(float(data_point[0]))
            self._x_data.append(float(data_point[26]))
            self._y1_data.append(float(data_point[27]))
            self._y2_data.append(float(data_point[30]))
