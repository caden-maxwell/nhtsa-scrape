import logging
from pathlib import Path

from PyQt6.QtWidgets import QWidget

from app.models import CSVGrid

from app.ui.CSVTab_ui import Ui_CSVTab


class CSVTab(QWidget):
    def __init__(self, profile_id, data_dir: Path):
        super().__init__()
        self.ui = Ui_CSVTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = CSVGrid(profile_id)
        self.ui.tableView.setModel(self.model)

        self.data_dir = data_dir
