import logging

from app.ui import Ui_SummaryTab
from app.pages import BaseTab
from app.models import Profile


class SummaryTab(BaseTab):
    def __init__(self, profile: Profile):
        super().__init__()
        self.ui = Ui_SummaryTab()
        self.ui.setupUi(self)

        self._logger = logging.getLogger(__name__)
        self._profile = profile

    def refresh_tab(self):
        self.ui.makeEdit.setText(self._profile.make)
        self.ui.modelEdit.setText(self._profile.model)
        self.ui.startYearEdit.setText(str(self._profile.start_year))
        self.ui.endYearEdit.setText(str(self._profile.end_year))
        self.ui.pDmgEdit.setText(self._profile.primary_dmg)
        self.ui.sDmgEdit.setText(self._profile.secondary_dmg)
        self.ui.minDVEdit.setText(str(self._profile.min_dv))
        self.ui.maxDVEdit.setText(str(self._profile.max_dv))
