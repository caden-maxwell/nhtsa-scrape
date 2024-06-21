import logging

from app.models import DatabaseHandler, Event


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
        events: list[Event] = self.db_handler.get_events(
            self.profile_id, include_ignored=False
        )

        for event in events:
            self._case_ids.append(float(event.case_id))
            self._x_data.append(float(event.c_bar))
            self._y1_data.append(float(event.NASS_dv))
            self._y2_data.append(float(event.TOT_dv))
