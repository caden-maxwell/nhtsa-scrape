import logging

from app.ui import Ui_SummaryTab
from app.pages import BaseTab
from app.models import Profile


class SummaryTab(BaseTab):
    def __init__(self, profile: Profile):
        super().__init__()
        self.ui = Ui_SummaryTab()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.ui.makeEdit.setText(profile.make)
        self.ui.modelEdit.setText(profile.model)
        self.ui.startYearEdit.setText(str(profile.start_year))
        self.ui.endYearEdit.setText(str(profile.end_year))
        self.ui.pDmgEdit.setText(profile.primary_dmg)
        self.ui.sDmgEdit.setText(profile.secondary_dmg)
        self.ui.minDVEdit.setText(str(profile.min_dv))
        self.ui.maxDVEdit.setText(str(profile.max_dv))

    def refresh_tab(self):
        pass
