import logging

from app.ui.SummaryTab_ui import Ui_SummaryTab
from . import BaseTab


class SummaryTab(BaseTab):
    def __init__(self, profile: tuple):
        super().__init__()
        self.ui = Ui_SummaryTab()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        # profile_id INTEGER PRIMARY KEY,
        # name TEXT,
        # description TEXT,
        # make TEXT,
        # model TEXT,
        # start_year INTEGER,
        # end_year INTEGER,
        # primary_dmg TEXT,
        # secondary_dmg TEXT,
        # min_dv INTEGER,
        # max_dv INTEGER,
        # max_cases INTEGER,
        # created INTEGER,
        # modified INTEGER

        self.ui.makeEdit.setText(profile[3])
        self.ui.modelEdit.setText(profile[4])
        self.ui.startYearEdit.setText(str(profile[5]))
        self.ui.endYearEdit.setText(str(profile[6]))
        self.ui.pDmgEdit.setText(profile[7])
        self.ui.sDmgEdit.setText(profile[8])
        self.ui.minDVEdit.setText(str(profile[9]))
        self.ui.maxDVEdit.setText(str(profile[10]))
        self.ui.maxCasesEdit.setText(str(profile[11]))
