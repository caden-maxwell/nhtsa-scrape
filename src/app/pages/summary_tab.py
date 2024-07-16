import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox

from app.ui import Ui_SummaryTab
from app.pages import BaseTab
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
        self.ui.makeEdit.setText(self._profile.make)
        self.ui.modelEdit.setText(self._profile.model)
        self.ui.startYearEdit.setText(str(self._profile.start_year))
        self.ui.endYearEdit.setText(str(self._profile.end_year))
        self.ui.pDmgEdit.setText(self._profile.primary_dmg)
        self.ui.sDmgEdit.setText(self._profile.secondary_dmg)
        self.ui.minDVEdit.setText(str(self._profile.min_dv))
        self.ui.maxDVEdit.setText(str(self._profile.max_dv))

    def open_profile(self):
        os.makedirs(self._profile_dir, exist_ok=True)
        try:
            os.startfile(self._profile_dir)
        except Exception as e:
            self._logger.error(f"Failed to open profile directory: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "Failed to open profile directory",
                QMessageBox.StandardButton.Ok,
            )

    def set_profile(self, profile: Profile):
        self._profile = profile
        self.refresh()
