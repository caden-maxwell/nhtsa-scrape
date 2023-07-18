from datetime import datetime
from io import BytesIO
import logging
import os
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QModelIndex
from PyQt6.QtGui import QPixmap, QFont, QImage
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
)

from bs4 import BeautifulSoup
from PIL import Image

from app.models import ProfileEvents
from app.scrape import RequestHandler, Priority, Request, ScrapeEngine
from app.ui.EventsTab_ui import Ui_EventsTab


class EventsTab(QWidget):
    COOKIE_EXPIRED_SECS = 900  # Assume site cookies expire after 15 minutes

    def __init__(self, model: ProfileEvents, data_dir: Path):
        super().__init__()
        self.ui = Ui_EventsTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = model
        self.model.layoutChanged.connect(self.update_list_size)
        self.images_dir = data_dir / "images"

        self.ui.eventsList.setModel(self.model)
        self.ui.eventsList.clicked.connect(self.open_event_details)
        self.ui.scrapeBtn.clicked.connect(self.scrape_images)
        self.ui.discardBtn.clicked.connect(self.delete_event)
        self.ui.imgSetCombo.addItem("Front", "F")
        self.ui.imgSetCombo.addItem("Back", "B")
        self.ui.imgSetCombo.addItem("Left", "L")
        self.ui.imgSetCombo.addItem("Right", "R")
        self.ui.imgSetCombo.addItem("Front Left", "FL")
        self.ui.imgSetCombo.addItem("Front Right", "FR")
        self.ui.imgSetCombo.addItem("Back Left", "BL")
        self.ui.imgSetCombo.addItem("Back Right", "BR")

        self.no_images_label = QLabel("There are no images to display")
        font = QFont()
        font.setPointSize(14)
        self.no_images_label.setFont(font)
        self.no_images_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.imgWidgetGrid.addWidget(self.no_images_label, 0, 0)
        self.no_images_label.setVisible(True)

        self.request_handler = RequestHandler()
        self.request_handler.response_received.connect(self.handle_response)

        self.response_cache = {}
        self.case_veh_img_ids = {}
        self.vehicle_imgs = {}

        if self.model.index(0, 0).isValid():
            self.ui.eventsList.setCurrentIndex(self.model.index(0, 0))
            self.open_event_details(self.model.index(0, 0))

    def showEvent(self, event) -> None:
        self.update_list_size()
        return super().showEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.open_event_details(self.ui.eventsList.currentIndex())
        return super().keyPressEvent(event)

    def update_list_size(self):
        scrollbar = self.ui.eventsList.verticalScrollBar()
        list_size = max(self.ui.eventsList.sizeHintForColumn(0), 200)
        scrollbar_width = 0
        if scrollbar.isVisible():
            scrollbar_width = scrollbar.sizeHint().width()
        self.ui.eventsList.setFixedWidth(list_size + scrollbar_width + 4)

    def cache_response(self, case_id, response_content, cookie):
        self.response_cache[case_id] = {
            "cookie": cookie,
            "xml": response_content,
            "created": datetime.now(),
        }

    def open_event_details(self, index: QModelIndex):
        if not index or not index.isValid():
            self.ui.makeLineEdit.setText("")
            self.ui.modelLineEdit.setText("")
            self.ui.yearLineEdit.setText("")
            self.ui.curbWeightLineEdit.setText("")
            self.ui.dmgLocLineEdit.setText("")
            self.ui.underrideLineEdit.setText("")
            self.ui.cBarLineEdit.setText("")
            self.ui.nassDVLineEdit.setText("")
            self.ui.nassVCLineEdit.setText("")
            self.ui.totDVLineEdit.setText("")
            return

        event_data = self.model.data(index, Qt.ItemDataRole.UserRole)

        # Left side of event view data
        self.ui.makeLineEdit.setText(event_data["make"])
        self.ui.modelLineEdit.setText(event_data["model"])
        self.ui.yearLineEdit.setText(str(event_data["model_year"]))
        self.ui.curbWeightLineEdit.setText(str(event_data["curb_weight"]))
        self.ui.dmgLocLineEdit.setText(event_data["dmg_loc"])
        self.ui.underrideLineEdit.setText(event_data["underride"])

        # Right side of event view data
        self.ui.cBarLineEdit.setText(f"{event_data['c_bar']:.4f}")
        self.ui.nassDVLineEdit.setText(f"{event_data['NASS_dv']:.4f}")
        self.ui.nassVCLineEdit.setText(f"{event_data['NASS_vc']:.4f}")
        self.ui.totDVLineEdit.setText(f"{event_data['TOT_dv']:.4f}")

        self.update_images(index)

    def scrape_images(self):
        event_data = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        )
        case_id = int(event_data["case_id"])
        vehicle_num = int(event_data["vehicle_num"])

        if not self.case_veh_img_ids.get((case_id, event_data["vehicle_num"])):
            self.case_veh_img_ids[(case_id, vehicle_num)] = []

        if (
            case_id in self.response_cache
            and (
                datetime.now() - self.response_cache[case_id]["created"]
            ).total_seconds()
            < self.COOKIE_EXPIRED_SECS
        ):
            cached_case = self.response_cache[case_id]
            self.parse_case(cached_case["xml"], cached_case["cookie"])
        else:
            request = Request(
                ScrapeEngine.CASE_URL + str(case_id),
                priority=Priority.CASE_FOR_IMAGE.value,
            )
            self.request_handler.enqueue_request(request)

    def delete_event(self):
        self.model.delete_event(self.ui.eventsList.currentIndex())
        self.ui.eventsList.setCurrentIndex(self.model.index(0, 0))
        self.open_event_details(self.model.index(0, 0))

    @pyqtSlot(int, str, bytes, str)
    def handle_response(self, priority, url, response_content, cookie):
        if priority == Priority.CASE_FOR_IMAGE.value:
            self.parse_case(response_content, cookie)
        elif priority == Priority.IMAGE.value:
            self.parse_image(url, response_content)

    def parse_case(self, response_content, cookie):
        soup = BeautifulSoup(response_content, "xml")
        case_id = int(soup.find("CaseForm").get("caseID"))
        img_form = soup.find("IMGForm")

        self.cache_response(case_id, response_content, cookie)

        if not img_form:
            self.logger.debug("No ImgForm found.")
            return

        vehicle_nums = [
            key[1] for key in self.case_veh_img_ids.keys() if key[0] == case_id
        ]

        veh_img_areas = {
            "F": "Front",
            "B": "Back",
            "L": "Left",
            "R": "Right",
            "FL": "Frontleftoblique",
            "FR": "Backleftoblique",
            "BL": "Frontrightoblique",
            "BR": "Backrightoblique",
        }

        for vehicle_num in vehicle_nums:
            veh_img_form = img_form.find("Vehicle", {"VehicleNumber": {vehicle_num}})
            if not veh_img_form:
                self.logger.warning(
                    f"Image form for vehicle '{vehicle_num}' of case '{case_id}' not found."
                )
                continue

            img_set_lookup = {}
            for key, val in veh_img_areas.items():
                img_area_form = veh_img_form.find(val)
                if not img_area_form:
                    continue
                images = img_area_form.find_all("image")
                img_set_lookup[key] = [(img.text, img["version"]) for img in images]

            image_set = self.ui.imgSetCombo.currentData()

            img_elements = img_set_lookup.get(image_set)
            img_ids = self.case_veh_img_ids.get((case_id, vehicle_num), [])
            for img_element in img_elements:
                img_id = int(img_element[0])
                img_version = img_element[1]
                img_url = f"https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID={img_id}&CaseID={case_id}&Version={img_version}"
                request = Request(
                    img_url, headers={"Cookie": cookie}, priority=Priority.IMAGE.value
                )
                if img_id not in img_ids:
                    self.request_handler.enqueue_request(request)
                    img_ids.append(img_id)
            self.case_veh_img_ids[(case_id, vehicle_num)] = img_ids

    def parse_image(self, url, response_content):
        img_id = int(url.split("&")[1].split("=")[1])
        vals = self.case_veh_img_ids.values()
        img_ids = [img_id for img_id_list in vals for img_id in img_id_list]
        if img_id in img_ids:
            img = Image.open(BytesIO(response_content))
            self.vehicle_imgs[img_id] = img
            self.update_images(self.ui.eventsList.currentIndex())

    def update_images(self, index: QModelIndex = None):
        if not index or not index.isValid():
            self.__remove_images()
            self.no_images_label.setVisible(True)
            return

        event_data = self.model.data(index, Qt.ItemDataRole.UserRole)
        img_ids = self.case_veh_img_ids.get(
            (int(event_data["case_id"]), int(event_data["vehicle_num"])), []
        )
        images = [
            (img_id, img)
            for img_id in img_ids
            if (img := self.vehicle_imgs.get(img_id))
        ]

        self.__remove_images()
        self.no_images_label.setVisible(not len(images))

        for img_id, img in images:
            thumbnail = ImageThumbnail(img_id, img, self.images_dir)
            self.ui.thumbnailsLayout.addWidget(thumbnail)

    def __remove_images(self):
        for i in reversed(range(self.ui.thumbnailsLayout.count())):
            widget = self.ui.thumbnailsLayout.itemAt(i).widget()
            self.ui.thumbnailsLayout.removeWidget(widget)
            widget.setParent(None)


class ImageThumbnail(QWidget):
    def __init__(self, img_id: int, image: Image.Image, images_dir: Path):
        super().__init__()
        self.img_id = img_id
        self.image = image
        self.images_dir = images_dir

        layout = QGridLayout()
        self.thumbnail_label = QLabel()
        pixmap = self.img_to_pixmap(self.image).scaledToHeight(160)
        self.thumbnail_label.setPixmap(pixmap)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.setFixedSize(pixmap.size())

        layout.addWidget(self.thumbnail_label, 0, 0)

        h_layout = QHBoxLayout()

        self.open_button = QPushButton("Open")
        self.open_button.setVisible(False)
        self.open_button.clicked.connect(self.open_image)
        h_layout.addWidget(self.open_button)

        self.save_button = QPushButton("Save")
        self.save_button.setVisible(False)
        self.save_button.clicked.connect(self.save_image)
        h_layout.addWidget(self.save_button)

        layout.addLayout(h_layout, 0, 0, Qt.AlignmentFlag.AlignBottom)

        self.setLayout(layout)

    def img_to_pixmap(self, img: Image.Image):
        qimg = QImage(
            img.tobytes("raw", "RGB"),
            img.size[0],
            img.size[1],
            QImage.Format.Format_RGB888,
        )
        return QPixmap.fromImage(qimg)

    def save_image(self):
        self.save_button.setEnabled(False)
        self.save_button.setText("Saving...")
        self.save_button.repaint()
        os.makedirs(self.images_dir, exist_ok=True)

        path = self.images_dir / f"{self.img_id}.png"
        i = 1
        while path.exists():
            path = self.images_dir / f"{self.img_id}({i}).png"
            i += 1

        self.image.save(path, "PNG")
        self.save_button.setText("Saved!")
        self.save_button.repaint()
        QTimer.singleShot(2500, self.reset_save_button)

    def reset_save_button(self):
        self.save_button.setText("Save")
        self.save_button.setEnabled(True)

    def open_image(self):
        self.image.show()

    def enterEvent(self, event):
        self.open_button.setVisible(True)
        self.save_button.setVisible(True)

    def leaveEvent(self, event):
        self.open_button.setVisible(False)
        self.save_button.setVisible(False)
