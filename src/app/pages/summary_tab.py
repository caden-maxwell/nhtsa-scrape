import logging

from app.ui.SummaryTab_ui import Ui_SummaryTab
from . import BaseTab

class SummaryTab(BaseTab):
    def __init__(self, profile: tuple):
        super().__init__()
        self.ui = Ui_SummaryTab()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)
