import json
from jsonschema import validate, ValidationError, Draft7Validator
import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QFileDialog

from app.pages.utils import open_path
from app.scrape import RequestHandler
from app.ui import Ui_SettingsMenu


class SettingsMenu(QWidget):
    back = pyqtSignal()
    rate_limit_changed = pyqtSignal(float)
    timeout_changed = pyqtSignal(float)
    save_path_changed = pyqtSignal(str)
    SETTINGS_SCHEMA = {
        "type": "object",
        "properties": {
            "rateLimit": {
                "description": f"Rate limit in seconds. Should be greater than {RequestHandler.MIN_RATE_LIMIT} to avoid site bans.",
                "type": "number",
                "default": RequestHandler.DEFAULT_RATE_LIMIT,
                "minimum": RequestHandler.MIN_RATE_LIMIT,
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
            "dataSavePath": {
                "description": "Path to save scraped data, images, etc.",
                "type": "string",
                "default": str((Path(__file__).parent.parent / "data").resolve()),
                "pattern": r"^(?:[a-zA-Z]:)?[\\/].*$",
            },
        },
    }

    def __init__(self, req_handler: RequestHandler):
        super().__init__()

        self.ui = Ui_SettingsMenu()
        self.ui.setupUi(self)

        self._logger = logging.getLogger(__name__)
        self._req_handler = req_handler
        self._validator = Draft7Validator(self.SETTINGS_SCHEMA)

        self.rate_limit_changed.connect(self._req_handler.update_rate_limit)
        self.timeout_changed.connect(self._req_handler.update_timeout)

        self.settings_path = (
            Path(__file__).parent.parent / "resources" / "settings.json"
        )
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.touch(exist_ok=True)
        self._logger.info(f"Loading settings from {self.settings_path}")

        self._settings = {}
        for key, value in self.SETTINGS_SCHEMA["properties"].items():
            self._settings[key] = value["default"]
        validate(self._settings, self.SETTINGS_SCHEMA)

        # Update and validate settings from file
        try:
            tmp_settings = self._settings.copy()
            tmp_settings.update(json.loads(self.settings_path.read_text()))
            validate(tmp_settings, self.SETTINGS_SCHEMA)
            self._settings = tmp_settings
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
            self._settings = tmp_settings

            # Make sure the settings are valid after fixing them
            validate(self._settings, self.SETTINGS_SCHEMA)
            self.settings_path.write_text(json.dumps(self._settings, indent=4))
        except Exception as e:
            self._logger.error(
                f"Failed to load settings file: {e}. Using default settings."
            )

        self._logger.info(
            f"Loaded settings:\n{json.dumps(self._settings, indent=4)}"
        )

        self.ui.backBtn.clicked.connect(self.back.emit)

        # Set up debug mode checkbox
        self.ui.debugCheckbox.setToolTip(
            self.SETTINGS_SCHEMA["properties"]["debug"]["description"]
        )
        self.ui.debugCheckbox.setChecked(self._settings["debug"])
        self.ui.debugCheckbox.clicked.connect(self._toggle_debug)
        
        # Update debug mode for the root logger
        self._set_logger_debug(self._settings["debug"])

        # Set up min rate limit spinbox
        self.ui.rateLimitSpinBox.setToolTip(
            self.SETTINGS_SCHEMA["properties"]["rateLimit"]["description"]
        )
        self.ui.rateLimitSpinBox.setValue(self._settings["rateLimit"])
        self.ui.rateLimitSpinBox.editingFinished.connect(
            lambda: self._update_rate_limit(self.ui.rateLimitSpinBox.value())
        )

        # Set up timeout spinbox
        self.ui.timeoutSpinBox.setValue(self._settings["timeout"])
        self.ui.timeoutSpinBox.editingFinished.connect(
            lambda: self._update_timeout(self.ui.timeoutSpinBox.value())
        )

        # Update request handler with settings
        self.rate_limit_changed.emit(self._settings["rateLimit"])
        self.timeout_changed.emit(self._settings["timeout"])

        # Set up data save path
        self.ui.filenameEdit.setToolTip(
            self.SETTINGS_SCHEMA["properties"]["dataSavePath"]["description"]
        )
        self.ui.filenameEdit.setText(self._settings["dataSavePath"])
        self.ui.browseBtn.clicked.connect(self._browse_data_save_path)

        try:
            Path(self._settings["dataSavePath"]).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._logger.error(
                f"Failed to create data save path '{self._settings['dataSavePath']}': {e}"
            )
            # Set data save path to default
            self._settings["dataSavePath"] = self.SETTINGS_SCHEMA["properties"]["dataSavePath"]["default"]
            self.settings_path.write_text(json.dumps(self._settings, indent=4))
            self.ui.filenameEdit.setText(self._settings["dataSavePath"])

        self.ui.openBtn.clicked.connect(self._open_save_path)

        self._logger.info(f"Successfully applied all settings.")

    def _update_rate_limit(self, value):
        value = round(value, 2)

        # Ensure minimum rate is no smaller than the absolute minimum
        min_rate_limit = self.SETTINGS_SCHEMA["properties"]["rateLimit"]["minimum"]
        if value < min_rate_limit:
            self._logger.warning(
                f"Rate limit set to {min_rate_limit}s to avoid site bans."
            )
            self.ui.rateLimitSpinBox.setValue(min_rate_limit)
            value = min_rate_limit

        # If the value has not changed, no need to update anything else
        if value == self._settings["rateLimit"]:
            return

        self._settings["rateLimit"] = value
        self.settings_path.write_text(json.dumps(self._settings, indent=4))
        self.rate_limit_changed.emit(value)

    def _update_timeout(self, value):
        value = round(value, 2)
        min_timeout = self.SETTINGS_SCHEMA["properties"]["timeout"]["minimum"]
        if value < min_timeout:
            self._logger.warning(f"Timeout must be at least {min_timeout}s.")
            self.ui.timeoutSpinBox.setValue(min_timeout)
            value = min_timeout

        # If the value has not changed, no need to update anything else
        if value == self._settings["timeout"]:
            return

        self._settings["timeout"] = value
        self.settings_path.write_text(json.dumps(self._settings, indent=4))
        self.timeout_changed.emit(value)

    def _set_logger_debug(self, debug_on: bool):
        root_logger = logging.getLogger()
        if debug_on:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)
        self._logger.info(f"Set logger debug mode to {debug_on}")

    def _toggle_debug(self, checked):
        self._set_logger_debug(checked)
        self._settings["debug"] = checked
        self.settings_path.write_text(json.dumps(self._settings, indent=4))

    def _browse_data_save_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Directory", self._settings["dataSavePath"]
        )

        if path and Path(path).exists():
            self.ui.filenameEdit.setText(path)
            self._settings["dataSavePath"] = path
            self.settings_path.write_text(json.dumps(self._settings, indent=4))
            self._logger.info(f"Set data save path to '{path}'.")
            self.save_path_changed.emit(path)

    def get_save_path(self):
        return Path(self._settings["dataSavePath"])

    def _open_save_path(self):
        open_path(self._settings["dataSavePath"])
