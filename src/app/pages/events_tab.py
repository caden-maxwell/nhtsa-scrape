import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from app.models import ProfileEvents
from app.ui.EventsTab_ui import Ui_EventsTab


class EventsTab(QWidget):
    def __init__(self, model: ProfileEvents):
        super().__init__()
        self.ui = Ui_EventsTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = model
    
        self.ui.eventsList.setModel(self.model)
        self.ui.eventsList.doubleClicked.connect(self.open_item_details)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Return:
            self.open_item_details(self.ui.eventsList.currentIndex())

        return super().keyPressEvent(event)

    def open_item_details(self, index):
        item = self.ui.eventsList.model().data(index)
        print(item)
        