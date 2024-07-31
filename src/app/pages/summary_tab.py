import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox

from app.ui import Ui_SummaryTab
from app.pages import BaseTab
from app.pages.utils import open_path
from app.models import Profile


class SummaryTab(BaseTab):
    def __init__(self, profile: Profile, profile_dir: Path):
        super().__init__()
        self.ui = Ui_SummaryTab()
        self.ui.setupUi(self)

        self._logger = logging.getLogger(__name__)
        self._profile = profile
        self._profile_dir = profile_dir
        self.ui.openBtn.clicked.connect(self.open_profile)

    def refresh(self):
        self.ui.paramsEdit.setText(self._profile.params)

    def open_profile(self):
        os.makedirs(self._profile_dir, exist_ok=True)
        success = open_path(self._profile_dir, self)
        if not success:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to open profile directory. See log for details.",
                QMessageBox.StandardButton.Ok,
            )
