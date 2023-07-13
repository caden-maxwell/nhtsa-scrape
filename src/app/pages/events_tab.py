import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy, QLayout

from app.models import ProfileEvents
from app.ui.EventsTab_ui import Ui_EventsTab


class EventsTab(QWidget):
    def __init__(self, model: ProfileEvents):
        super().__init__()
        self.ui = Ui_EventsTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = model
        self.model.layoutChanged.connect(self.update_size)

        self.ui.eventsList.setModel(self.model)
        self.ui.eventsList.doubleClicked.connect(self.open_event_details)

    def showEvent(self, event) -> None:
        self.update_size()
        return super().showEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.open_event_details(self.ui.eventsList.currentIndex())
        return super().keyPressEvent(event)

    def update_size(self):
        scrollbar = self.ui.eventsList.verticalScrollBar()
        list_size = max(self.ui.eventsList.sizeHintForColumn(0), 200)
        scrollbar_width = 0
        if scrollbar.isVisible():
            scrollbar_width = scrollbar.sizeHint().width()
        self.ui.eventsList.setFixedWidth(list_size + scrollbar_width + 4)

    def open_event_details(self, index):
        for i in reversed(range(self.ui.eventLayout.count())):
            self.ui.eventLayout.itemAt(i).widget().setParent(None)

        event_data = self.model.data(index, Qt.ItemDataRole.UserRole)
        keys_to_keep = set(
            [
                "make",
                "model",
                "model_year",
                "curb_weight",
                "dmg_loc",
                "underride",
                "c_bar",
                "NASS_dv",
                "NASS_vc",
                "TOT_dv",
            ]
        )
        event_data = {k: v for k, v in event_data.items() if k in keys_to_keep}

        for i, (key, value) in enumerate(event_data.items()):
            key_label = QLabel(str(key) + ":")
            key_label.setWordWrap(True)
            key_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            key_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.ui.eventLayout.addWidget(key_label, i + 1, 0)

            value_label = QLabel(str(value))
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.ui.eventLayout.addWidget(value_label, i + 1, 1)

        self.ui.eventLayout.setColumnStretch(1, 2)
