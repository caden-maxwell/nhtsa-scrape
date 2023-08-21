import logging

from PyQt6.QtWidgets import QWidget

from app.ui.SummaryTab_ui import Ui_SummaryTab


class SummaryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SummaryTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)
