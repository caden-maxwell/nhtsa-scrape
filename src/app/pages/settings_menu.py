import json
from jsonschema import validate, ValidationError, Draft7Validator
import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QFileDialog

from app.scrape import RequestController
from app.ui import Ui_SettingsMenu


class SettingsMenu(QWidget):
    back = pyqtSignal()
    min_rate_limit_changed = pyqtSignal(float)
    max_rate_limit_changed = pyqtSignal(float)
    timeout_changed = pyqtSignal(float)
    save_path_changed = pyqtSignal(str)
    SETTINGS_SCHEMA = {
        "type": "object",
        "properties": {
            "minRateLimit": {
                "description": f"Minimum rate limit in seconds. Must be greater than {RequestController.ABS_MIN_RATE_LIMIT} to avoid IP bans.",
                "type": "number",
                "default": RequestController.DEFAULT_MIN_RATE_LIMIT,
                "minimum": RequestController.ABS_MIN_RATE_LIMIT,
            },
            "maxRateLimit": {
                "description": "Maximum rate limit in seconds. Must be greater than or equal to the minimum rate limit.",
                "type": "number",
                "default": RequestController.DEFAULT_MAX_RATE_LIMIT,
                "minimum": RequestController.ABS_MIN_RATE_LIMIT,
            },
            "timeout": {
                "description": "Request timeout in seconds.",
                "type": "number",
                "default": RequestController.DEFAULT_TIMEOUT,
                "minimum": RequestController.MIN_TIMEOUT,
            },
            "debug": {
                "description": "Enable debug logging.",
                "type": "boolean",
                "default": True,
            },
            "dataSavePath": {
                "description": "Path to save scraped data, images, etc.",
                "type": "string",
                "default": str((Path(__file__).parent.parent / "data").resolve()),
                "pattern": r"^(?:[a-zA-Z]:)?[\\/].*$",
            },
        },
    }

    def __init__(self, req_handler: RequestController):
        super().__init__()

        self.ui = Ui_SettingsMenu()
        self.ui.setupUi(self)

        self._logger = logging.getLogger(__name__)
        self._req_handler = req_handler
        self._validator = Draft7Validator(self.SETTINGS_SCHEMA)

        self.min_rate_limit_changed.connect(self._req_handler.update_min_rate_limit)
        self.max_rate_limit_changed.connect(self._req_handler.update_max_rate_limit)
        self.timeout_changed.connect(self._req_handler.update_timeout)

        self.settings_path = (
            Path(__file__).parent.parent / "resources" / "settings.json"
        )
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.touch(exist_ok=True)
        self._logger.debug(f"Settings path: {self.settings_path}")

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
            errors = self._validator.iter_errors(tmp_settings)
            for error in errors:
                error: ValidationError
                if len(error.absolute_schema_path) > 1:
                    param = error.absolute_schema_path[1]
                    self._logger.error(
                        f"'{param}' in settings file is invalid: {error}"
                    )
                    tmp_settings[param] = self.SETTINGS_SCHEMA["properties"][param][
                        "default"
                    ]
                    self._logger.debug(f"Set '{param}' to default value.")
            self.settings = tmp_settings

            # Make sure the settings are valid after fixing them
            validate(self.settings, self.SETTINGS_SCHEMA)
            self.settings_path.write_text(json.dumps(self.settings, indent=4))
        except Exception as e:
            self._logger.error(
                f"Failed to load settings file: {e}. Using default settings."
            )

        self._logger.info(
            f"Successfully loaded settings:\n{json.dumps(self.settings, indent=4)}"
        )

        self.ui.backBtn.clicked.connect(self.back.emit)

        # Set up min rate limit spinbox
        self.ui.minRateSpinBox.setToolTip(
            self.SETTINGS_SCHEMA["properties"]["minRateLimit"]["description"]
        )
        self.ui.minRateSpinBox.setValue(self.settings["minRateLimit"])
        self.ui.minRateSpinBox.editingFinished.connect(
            lambda: self._update_min_rate(self.ui.minRateSpinBox.value())
        )

        # Set up max rate limit spinbox
        self.ui.maxRateSpinBox.setToolTip(
            self.SETTINGS_SCHEMA["properties"]["maxRateLimit"]["description"]
        )
        self.ui.maxRateSpinBox.setValue(self.settings["maxRateLimit"])
        self.ui.maxRateSpinBox.editingFinished.connect(
            lambda: self._update_max_rate(self.ui.maxRateSpinBox.value())
        )

        # Set up timeout spinbox
        self.ui.timeoutSpinBox.setValue(self.settings["timeout"])
        self.ui.timeoutSpinBox.editingFinished.connect(
            lambda: self._update_timeout(self.ui.timeoutSpinBox.value())
        )

        # Update request handler with settings
        self.min_rate_limit_changed.emit(self.settings["minRateLimit"])
        self.max_rate_limit_changed.emit(self.settings["maxRateLimit"])
        self.timeout_changed.emit(self.settings["timeout"])

        # Set up debug checkbox
        self.ui.debugCheckbox.setToolTip(
            self.SETTINGS_SCHEMA["properties"]["debug"]["description"]
        )
        self.ui.debugCheckbox.setChecked(self.settings["debug"])
        self.ui.debugCheckbox.clicked.connect(self._toggle_debug)

        # Set up data save path
        self.ui.filenameEdit.setToolTip(
            self.SETTINGS_SCHEMA["properties"]["dataSavePath"]["description"]
        )
        self.ui.filenameEdit.setText(self.settings["dataSavePath"])
        self.ui.browseBtn.clicked.connect(self._browse_data_save_path)

        try:
            Path(self.settings["dataSavePath"]).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._logger.error(
                f"Failed to create data save path '{self.settings['dataSavePath']}': {e}"
            )
            # Set data save path to default
            self.settings["dataSavePath"] = self.SETTINGS_SCHEMA["properties"][
                "dataSavePath"
            ]["default"]
            self.settings_path.write_text(json.dumps(self.settings, indent=4))
            self.ui.filenameEdit.setText(self.settings["dataSavePath"])

    def _update_min_rate(self, value):
        value = round(value, 2)

        # Ensure minimum rate is no smaller than the absolute minimum
        abs_min_rate = self.SETTINGS_SCHEMA["properties"]["minRateLimit"]["minimum"]
        if value < abs_min_rate:
            self._logger.warning(
                f"Minimum rate limit must be greater than {abs_min_rate}s to avoid IP bans."
            )
            self.ui.minRateSpinBox.setValue(abs_min_rate)
            value = abs_min_rate

        # If minimum is more than maximum, update maximum to match
        if value > self.ui.maxRateSpinBox.value():
            self.ui.maxRateSpinBox.setValue(value)
            self._update_max_rate(value)

        # If the value has not changed, no need to update anything else
        if value == self.settings["minRateLimit"]:
            return

        self.settings["minRateLimit"] = value
        self.settings_path.write_text(json.dumps(self.settings, indent=4))
        self.min_rate_limit_changed.emit(value)

    def _update_max_rate(self, value):
        value = round(value, 2)
        min_box_val = round(self.ui.minRateSpinBox.value(), 2)
        if value < min_box_val:
            self._logger.warning(
                f"Maximum rate limit must be greater than or equal to the minimum rate limit ({min_box_val}s)."
            )
            self.ui.maxRateSpinBox.setValue(min_box_val)
            value = min_box_val

        # If the value has not changed, no need to update anything else
        if value == self.settings["maxRateLimit"]:
            return

        self.settings["maxRateLimit"] = value
        self.settings_path.write_text(json.dumps(self.settings, indent=4))
        self.max_rate_limit_changed.emit(value)

    def _update_timeout(self, value):
        value = round(value, 2)
        min_timeout = self.SETTINGS_SCHEMA["properties"]["timeout"]["minimum"]
        if value < min_timeout:
            self._logger.warning(f"Timeout must be at least {min_timeout}s.")
            self.ui.timeoutSpinBox.setValue(min_timeout)
            value = min_timeout

        # If the value has not changed, no need to update anything else
        if value == self.settings["timeout"]:
            return

        self.settings["timeout"] = value
        self.settings_path.write_text(json.dumps(self.settings, indent=4))
        self.timeout_changed.emit(value)

    def _toggle_debug(self, checked):
        root_logger = logging.getLogger()
        if checked:
            root_logger.setLevel(logging.DEBUG)
            self._logger.info("Enabled debug logging.")
        else:
            self._logger.info("Disabled debug logging.")
            root_logger.setLevel(logging.INFO)
        self.settings["debug"] = checked
        self.settings_path.write_text(json.dumps(self.settings, indent=4))

    def _browse_data_save_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.settings["dataSavePath"]
        )

        if path and Path(path).exists():
            self.ui.filenameEdit.setText(path)
            self.settings["dataSavePath"] = path
            self.settings_path.write_text(json.dumps(self.settings, indent=4))
            self._logger.info(f"Set data save path to '{path}'.")
            self.save_path_changed.emit(path)

    def get_save_path(self):
        return Path(self.settings["dataSavePath"])
