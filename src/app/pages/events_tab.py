import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QLabel,
    QSizePolicy,
)

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

        self.img_grid = ImageViewerWidget()
        self.img_grid.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.ui.gridLayout.addWidget(self.img_grid, 2, 0, 1, 2)

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

        self.img_grid.update_images(
            [
                "src/test_images/image1.jpg",
                "src/test_images/image2.jpg",
                "src/test_images/image3.jpg",
                "src/test_images/image4.jpg",
                "src/test_images/image5.jpg",
                "src/test_images/image6.jpg",
                "src/test_images/image7.jpg",
            ]
        )

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


class ImageViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.image_paths = []

        self.v_layout = QGridLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(175)

        self.thumbnails = QWidget()
        self.thumbnails_layout = QHBoxLayout()
        self.thumbnails.setLayout(self.thumbnails_layout)

        self.scroll_area.setWidget(self.thumbnails)
        self.v_layout.addWidget(self.scroll_area)
        self.setLayout(self.v_layout)

        self.no_images_label = QLabel("There are no images to display")
        font = QFont()
        font.setPointSize(14)
        self.no_images_label.setFont(font)
        self.no_images_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.v_layout.addWidget(self.no_images_label, 0, 0)
        self.no_images_label.setVisible(True)

    def update_images(self, image_paths):
        # Clear existing thumbnails
        for i in reversed(range(self.thumbnails_layout.count())):
            widget = self.thumbnails_layout.itemAt(i).widget()
            self.thumbnails_layout.removeWidget(widget)
            widget.setParent(None)

        # Add new thumbnails to the layout
        for image_path in image_paths:
            thumbnail = QLabel()
            pixmap = QPixmap(image_path).scaledToHeight(150)
            thumbnail.setPixmap(pixmap)
            thumbnail.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            thumbnail.mouseDoubleClickEvent = self.create_mouse_press_event(image_path)
            self.thumbnails_layout.addWidget(thumbnail)

    def update_images(self, image_paths):
        self.no_images_label.setVisible(not len(image_paths))
        for i in reversed(range(self.thumbnails_layout.count())):
            widget = self.thumbnails_layout.itemAt(i).widget()
            self.thumbnails_layout.removeWidget(widget)
            widget.setParent(None)

        # Add new thumbnails to the layout
        for image_path in image_paths:
            thumbnail = QLabel()
            pixmap = QPixmap(image_path).scaledToWidth(200)
            thumbnail.setPixmap(pixmap)
            thumbnail.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            thumbnail.mousePressEvent = self.create_mouse_press_event(
                image_path
            )  # Assign click event
            self.thumbnails_layout.addWidget(thumbnail)

    def create_mouse_press_event(self, image_path):
        def mouse_press_event(event):
            print(f"Opening image: {image_path}")

            ### TODO: Open image in a new window

        return mouse_press_event
