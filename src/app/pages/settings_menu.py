import json
import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.scrape import RequestHandler
from app.ui.SettingsMenu_ui import Ui_SettingsMenu


class SettingsMenu(QWidget):
    back = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)
        self.request_handler = RequestHandler()

        self.settings_path = (
            Path(__file__).parent.parent / "resources" / "settings.json"
        )
        self.settings = {}
        try:
            self.settings = json.loads(self.settings_path.read_text())
        except Exception as e:
            self.logger.error(f"Failed to load settings file: {e}")

        min_rate_limit = self.settings.get(
            "minRateLimit", RequestHandler.DEFAULT_MIN_RATE_LIMIT
        )
        self.request_handler.update_min_rate_limit(min_rate_limit)
        self.logger.debug(f"Loaded min rate limit of {min_rate_limit}.")

        max_rate_limit = self.settings.get(
            "maxRateLimit", RequestHandler.DEFAULT_MAX_RATE_LIMIT
        )
        self.request_handler.update_max_rate_limit(max_rate_limit)
        self.logger.debug(f"Loaded max rate limit of {max_rate_limit}.")

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.debugCheckbox.clicked.connect(self.toggle_debug)
        self.ui.minRateBox.setValue(min_rate_limit)
        self.ui.maxRateBox.setValue(max_rate_limit)
        self.ui.minRateBox.editingFinished.connect(self.update_min_rate)
        self.ui.maxRateBox.editingFinished.connect(self.update_max_rate)

    def toggle_debug(self, checked):
        root_logger = logging.getLogger()
        if checked:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)

    def update_min_rate(self):
        value = self.ui.minRateBox.value()
        if value < RequestHandler.ABS_MIN_RATE_LIMIT:
            self.logger.warning(
                f"Min rate limit must be greater than {RequestHandler.ABS_MIN_RATE_LIMIT}. Setting to {RequestHandler.ABS_MIN_RATE_LIMIT}."
            )
            self.ui.minRateBox.setValue(RequestHandler.ABS_MIN_RATE_LIMIT)
            value = RequestHandler.ABS_MIN_RATE_LIMIT
        if value > self.ui.maxRateBox.value():
            self.ui.maxRateBox.setValue(value)
            self.update_max_rate()
        if value != self.settings.get(
            "minRateLimit", RequestHandler.DEFAULT_MIN_RATE_LIMIT
        ):
            self.settings["minRateLimit"] = value
            self.settings_path.write_text(json.dumps(self.settings, indent=4))
            self.request_handler.update_min_rate_limit(value)
            self.logger.debug(f"Successfully updated min rate limit to {value}.")

    def update_max_rate(self):
        value = self.ui.maxRateBox.value()
        if value < self.ui.minRateBox.value():
            self.logger.warning(
                "Max rate limit must be equal to or greater than min rate limit. Setting to min rate limit."
            )
            min_rate = self.ui.minRateBox.value()
            self.ui.maxRateBox.setValue(min_rate)
            value = min_rate
        if value != self.settings.get(
            "maxRateLimit", RequestHandler.DEFAULT_MAX_RATE_LIMIT
        ):
            self.settings["maxRateLimit"] = value
            self.settings_path.write_text(json.dumps(self.settings, indent=4))
            self.request_handler.update_max_rate_limit(value)
            self.logger.debug(f"Successfully updated max rate limit to {value}.")
