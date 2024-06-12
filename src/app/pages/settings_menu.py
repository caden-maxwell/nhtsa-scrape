import json
from jsonschema import validate, ValidationError, Draft7Validator
import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.scrape import RequestHandler
from app.ui import Ui_SettingsMenu


class SettingsMenu(QWidget):
    back = pyqtSignal()
    min_rate_limit_changed = pyqtSignal(float)
    max_rate_limit_changed = pyqtSignal(float)
    timeout_changed = pyqtSignal(float)
    SETTINGS_SCHEMA = {
        "type": "object",
        "properties": {
            "minRateLimit": {
                "description": "Minimum rate limit in seconds. Must be greater than 0.2s to avoid IP bans.",
                "type": "number",
                "default": RequestHandler.DEFAULT_MIN_RATE_LIMIT,
                "minimum": RequestHandler.ABS_MIN_RATE_LIMIT,
            },
            "maxRateLimit": {
                "description": "Maximum rate limit in seconds.",
                "type": "number",
                "default": RequestHandler.DEFAULT_MAX_RATE_LIMIT,
                "minimum": RequestHandler.ABS_MIN_RATE_LIMIT,
            },
            "timeout": {
                "description": "Request timeout in seconds.",
                "type": "number",
                "default": RequestHandler.DEFAULT_TIMEOUT,
                "minimum": RequestHandler.MIN_TIMEOUT,
            },
            "debug": {
                "description": "Enable debug logging.",
                "type": "boolean",
                "default": True,
            },
        },
    }

    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)
        self.request_handler = RequestHandler()
        self.validator = Draft7Validator(self.SETTINGS_SCHEMA)

        self.min_rate_limit_changed.connect(self.request_handler.update_min_rate_limit)
        self.max_rate_limit_changed.connect(self.request_handler.update_max_rate_limit)
        self.timeout_changed.connect(self.request_handler.update_timeout)

        self.settings_path = Path(__file__).parent.parent / "resources" / "settings.json"
        self.logger.debug(f"Settings path: {self.settings_path}")

        self.settings = {}
        for key, value in self.SETTINGS_SCHEMA["properties"].items():
            self.settings[key] = value["default"]
        validate(self.settings, self.SETTINGS_SCHEMA)

        # Update and validate settings from file
        try:
            tmp_settings = self.settings.copy()
            tmp_settings.update(json.loads(self.settings_path.read_text()))
            validate(tmp_settings, self.SETTINGS_SCHEMA)
            self.settings = tmp_settings
        except ValidationError:
            errors = self.validator.iter_errors(tmp_settings)
            for error in errors:
                error: ValidationError
                if len(error.absolute_schema_path) > 1:
                    param = error.absolute_schema_path[1]
                    self.logger.error(f"'{param}' in settings file is invalid: {error}")
                    tmp_settings[param] = self.SETTINGS_SCHEMA["properties"][param]["default"]
                    self.logger.debug(f"Set '{param}' to default value.")
            self.settings = tmp_settings
            validate(
                self.settings, self.SETTINGS_SCHEMA
            )  # Make sure the settings are valid after fixing them
            self.settings_path.write_text(json.dumps(self.settings, indent=4))
        except Exception as e:
            self.logger.error(f"Failed to load settings file: {e}. Using default settings.")

        self.logger.debug(f"Successfully loaded settings:\n{json.dumps(self.settings, indent=4)}")

        self.ui.backBtn.clicked.connect(self.back.emit)

        self.ui.debugCheckbox.setToolTip(self.SETTINGS_SCHEMA["properties"]["debug"]["description"])
        self.ui.debugCheckbox.setChecked(self.settings["debug"])
        self.ui.debugCheckbox.clicked.connect(self.toggle_debug)

        self.ui.minRateSpinBox.setToolTip(self.SETTINGS_SCHEMA["properties"]["minRateLimit"]["description"])
        self.ui.minRateSpinBox.setMinimum(RequestHandler.ABS_MIN_RATE_LIMIT)
        self.ui.minRateSpinBox.setValue(self.settings["minRateLimit"])
        self.ui.minRateSpinBox.editingFinished.connect(self.update_min_rate)

        self.ui.maxRateSpinBox.setToolTip(self.SETTINGS_SCHEMA["properties"]["maxRateLimit"]["description"])
        self.ui.maxRateSpinBox.setMaximum(RequestHandler.DEFAULT_MAX_RATE_LIMIT)
        self.ui.maxRateSpinBox.setValue(self.settings["maxRateLimit"])
        self.ui.maxRateSpinBox.editingFinished.connect(self.update_max_rate)

        self.ui.timeoutSpinBox.setMinimum(RequestHandler.MIN_TIMEOUT)
        self.ui.timeoutSpinBox.setValue(self.settings["timeout"])
        self.ui.timeoutSpinBox.editingFinished.connect(self.update_timeout)

    def toggle_debug(self, checked):
        root_logger = logging.getLogger()
        if checked:
            root_logger.setLevel(logging.DEBUG)
            self.logger.debug("Enabled debug logging.")
        else:
            self.logger.debug("Disabled debug logging.")
            root_logger.setLevel(logging.INFO)
        self.settings["debug"] = checked
        self.settings_path.write_text(json.dumps(self.settings, indent=4))

    def update_min_rate(self):
        value = round(self.ui.minRateSpinBox.value(), 2)

        # Ensure minimum rate is no smaller than the absolute minimum
        min_rate = self.SETTINGS_SCHEMA["properties"]["minRateLimit"]["minimum"]
        if value < min_rate:
            self.logger.warning(
                f"Minimum rate limit must be greater than {min_rate}s to avoid IP bans."
            )
            self.ui.minRateSpinBox.setValue(min_rate)
            value = min_rate

        # If minimum is more than maximum, update maximum to match
        if value > self.ui.maxRateSpinBox.value():
            self.ui.maxRateSpinBox.setValue(value)
            self.update_max_rate()

        # If the value has not changed, no need to update anything else
        if value == self.settings["minRateLimit"]:
            return

        self.settings["minRateLimit"] = value
        self.settings_path.write_text(json.dumps(self.settings, indent=4))
        self.min_rate_limit_changed.emit(value)
        self.logger.debug(f"Updated minimum rate limit to {value}s.")

    def update_max_rate(self):
        value = round(self.ui.maxRateSpinBox.value(), 2)
        if value < self.ui.minRateSpinBox.value():
            self.logger.warning(
                f"Maximum rate limit must be greater than or equal to the minimum rate limit ({self.ui.minRateSpinBox.value()}s)."
            )
            min_rate = self.ui.minRateSpinBox.value()
            self.ui.maxRateSpinBox.setValue(min_rate)
            value = min_rate

        # If the value has not changed, no need to update anything else
        if value == self.settings.get("maxRateLimit", RequestHandler.DEFAULT_MAX_RATE_LIMIT):
            return

        self.settings["maxRateLimit"] = value
        self.settings_path.write_text(json.dumps(self.settings, indent=4))
        self.max_rate_limit_changed.emit(value)
        self.logger.debug(f"Updated maximum rate limit to {value}s.")

    def update_timeout(self):
        value = round(self.ui.timeoutSpinBox.value(), 2)

        # If the value has not changed, no need to update anything else
        if value == self.settings.get("timeout", RequestHandler.DEFAULT_TIMEOUT):
            return

        self.settings["timeout"] = value
        self.settings_path.write_text(json.dumps(self.settings, indent=4))
        self.timeout_changed.emit(value)
        self.logger.debug(f"Updated request timeout to {value}s.")
