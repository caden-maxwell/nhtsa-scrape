from datetime import datetime
from io import BytesIO
import logging
import os
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot, QModelIndex
from PyQt6.QtGui import QPixmap, QFont, QImage, QColor, QPalette
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QStyledItemDelegate,
)

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

from . import BaseTab
from app.models import DatabaseHandler, EventList
from app.scrape import RequestHandler, Priority, RequestQueueItem, ScrapeEngine
from app.ui.EventsTab_ui import Ui_EventsTab


class EventsTab(BaseTab):
    COOKIE_EXPIRED_SECS = 900  # Assume site cookies expire after 15 minutes

    def __init__(self, db_handler: DatabaseHandler, profile_id, data_dir: Path):
        super().__init__()
        self.ui = Ui_EventsTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = EventList(db_handler, profile_id)
        self.current_index_vals = None
        self.images_dir = data_dir / "images"

        self.ui.eventsList.setModel(self.model)
        delegate = CustomItemDelegate()
        self.ui.eventsList.setItemDelegate(delegate)

        self.ui.eventsList.clicked.connect(self.open_event_details)
        self.ui.scrapeBtn.clicked.connect(self.scrape_btn_clicked)
        self.ui.stopBtn.clicked.connect(self.stop_btn_clicked)
        self.ui.ignoreBtn.clicked.connect(self.ignore_event)
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
        self.case_veh_img_ids: dict[tuple[int, int], dict[int, None | Image.Image]] = {}

        if self.model.index(0, 0).isValid():
            self.ui.eventsList.setCurrentIndex(self.model.index(0, 0))
            self.open_event_details(self.model.index(0, 0))

    def refresh_tab(self):
        self.model.refresh_data()
        self.list_changed()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.open_event_details(self.ui.eventsList.currentIndex())
        return super().keyPressEvent(event)

    def list_changed(self):
        scrollbar = self.ui.eventsList.verticalScrollBar()
        list_size = max(self.ui.eventsList.sizeHintForColumn(0), 200)
        scrollbar_width = 0
        if scrollbar.isVisible():
            scrollbar_width = scrollbar.sizeHint().width()
        self.ui.eventsList.setFixedWidth(list_size + scrollbar_width + 4)

        if self.current_index_vals:
            # In the case that another event is inserted before the currently
            # selected event, we need to find the new index of the current one
            # and select it again.
            index = self.model.index_from_vals(*self.current_index_vals)
            self.ui.eventsList.setCurrentIndex(index)

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

            self.ui.scrapeBtn.setEnabled(False)
            self.ui.stopBtn.setVisible(False)
            self.ui.scrapeBtn.repaint()
            self.ui.stopBtn.repaint()

            self.no_images_label.setVisible(True)
            self.__clear_thumbnails()

            self.ui.ignoreBtn.setText("Ignore Event")
            return

        event_data = self.model.data(index, Qt.ItemDataRole.UserRole)
        self.update_buttons(event_data)
        case_id = int(event_data["case_id"])
        vehicle_num = int(event_data["vehicle_num"])

        # We need to get the unique values for this index so we can find it later
        # if another event is inserted before it in the list
        self.current_index_vals = (case_id, vehicle_num, event_data["event_num"])

        # Left side of event view data
        self.ui.makeLineEdit.setText(event_data["make"])
        self.ui.modelLineEdit.setText(event_data["model"])
        self.ui.yearLineEdit.setText(str(event_data["model_year"]))
        self.ui.curbWeightLineEdit.setText(f"{event_data['curb_weight'] * 2.20462:.4f}")
        self.ui.dmgLocLineEdit.setText(event_data["dmg_loc"])
        self.ui.underrideLineEdit.setText(event_data["underride"])

        # Right side of event view data
        self.ui.cBarLineEdit.setText(f"{event_data['c_bar']:.4f}")
        self.ui.nassDVLineEdit.setText(f"{event_data['NASS_dv']:.4f}")
        self.ui.nassVCLineEdit.setText(f"{event_data['NASS_vc']:.4f}")
        self.ui.totDVLineEdit.setText(f"{event_data['TOT_dv']:.4f}")

        # Clear and repopulate image thumbnails
        img_ids = self.case_veh_img_ids.get((case_id, vehicle_num), {})
        images = [(img_id, img) for img_id, img in img_ids.items() if img]

        self.no_images_label.setVisible(not len(images))
        self.__clear_thumbnails()

        for img_id, img in images:
            thumbnail = ImageThumbnail(img_id, img, self.images_dir, event_data)
            self.ui.thumbnailsLayout.addWidget(thumbnail)

        if self.model.data(index, Qt.ItemDataRole.FontRole):
            self.ui.ignoreBtn.setText("Unignore Event")
        else:
            self.ui.ignoreBtn.setText("Ignore Event")

    def __clear_thumbnails(self):
        for i in reversed(range(self.ui.thumbnailsLayout.count())):
            widget = self.ui.thumbnailsLayout.itemAt(i).widget()
            self.ui.thumbnailsLayout.removeWidget(widget)
            widget.setParent(None)

    def update_buttons(self, event_data):
        case_id = int(event_data["case_id"])
        vehicle_num = int(event_data["vehicle_num"])
        img_extra_data = {"case_id": case_id, "vehicle_num": vehicle_num}
        case_extra_data = {"case_id": case_id}
        if self.request_handler.contains(
            Priority.IMAGE.value, img_extra_data
        ) or self.request_handler.contains(
            Priority.CASE_FOR_IMAGE.value, case_extra_data
        ):
            self.ui.scrapeBtn.setText("Scraping...")
            self.ui.scrapeBtn.setEnabled(False)
            self.ui.stopBtn.setVisible(True)
        else:
            self.ui.scrapeBtn.setText("Scrape Images")
            self.ui.scrapeBtn.setEnabled(True)
            self.ui.stopBtn.setVisible(False)
        self.ui.scrapeBtn.repaint()
        self.ui.stopBtn.repaint()

    def scrape_btn_clicked(self):
        event_data = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        )

        case_id = int(event_data["case_id"])
        vehicle_num = int(event_data["vehicle_num"])

        self.case_veh_img_ids[(case_id, vehicle_num)] = self.case_veh_img_ids.get(
            (case_id, vehicle_num), {}
        )

        cached_case = self.response_cache.get(case_id)
        if self.cached_and_valid(case_id):
            self.logger.debug(f"Using cached case ({case_id})")
            self.parse_case(cached_case["xml"], cached_case["cookie"])
        else:
            request = RequestQueueItem(
                f"{ScrapeEngine.CASE_URL}{case_id}&docinfo=0",
                priority=Priority.CASE_FOR_IMAGE.value,
                extra_data={"case_id": case_id},
            )
            self.request_handler.enqueue_request(request)
        self.update_buttons(event_data)

    def stop_btn_clicked(self):
        event_data = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        )

        extra_data = {"case_id": int(event_data["case_id"])}
        self.request_handler.clear_queue(Priority.CASE_FOR_IMAGE.value, extra_data)

        extra_data.update({"vehicle_num": int(event_data["vehicle_num"])})
        self.request_handler.clear_queue(Priority.IMAGE.value, extra_data)

        self.ui.scrapeBtn.setText("Scrape Images")
        self.ui.scrapeBtn.setEnabled(True)
        self.ui.stopBtn.setVisible(False)

    def cached_and_valid(self, case_id):
        """Check if the case has been cached and if the cookie is still valid."""
        cached_case = self.response_cache.get(case_id)
        return (
            cached_case
            and (datetime.now() - cached_case["created"]).total_seconds()
            < self.COOKIE_EXPIRED_SECS
        )

    def delete_event(self):
        msg_box = QMessageBox()
        msg_box.setText(
            "Are you sure you want to delete this event?"
            "\nThis action cannot be undone."
        )
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Delete Event")
        msg_box.exec()

        if msg_box.result() == QMessageBox.StandardButton.No:
            return

        index = self.ui.eventsList.currentIndex()
        self.model.delete_event(index)

        if index.row() >= self.model.rowCount():
            index = self.model.index(self.model.rowCount() - 1, 0)

        self.ui.eventsList.setCurrentIndex(index)
        self.open_event_details(index)

    def ignore_event(self):
        index = self.ui.eventsList.currentIndex()
        self.model.toggle_ignored(index)

        if self.model.data(index, Qt.ItemDataRole.FontRole):
            self.ui.ignoreBtn.setText("Unignore Event")
        else:
            self.ui.ignoreBtn.setText("Ignore Event")

    @pyqtSlot(int, str, bytes, str, dict)
    def handle_response(self, priority, url, response_content, cookie, extra_data):
        if priority == Priority.CASE_FOR_IMAGE.value:
            self.parse_case(response_content, cookie)
        elif priority == Priority.IMAGE.value:
            self.parse_image(url, response_content, extra_data)

        if self.ui.eventsList.currentIndex().isValid():
            event_data = self.model.data(
                self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
            )
            self.update_buttons(event_data)

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
            "FR": "Frontrightoblique",
            "BL": "Backleftoblique",
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

            img_elements = img_set_lookup.get(image_set, [])
            img_id_dict = self.case_veh_img_ids.get((case_id, vehicle_num), {})
            for img_element in img_elements:
                img_id = int(img_element[0])
                img_version = img_element[1]
                img_url = f"https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID={img_id}&CaseID={case_id}&Version={img_version}"
                request = RequestQueueItem(
                    img_url,
                    headers={"Cookie": cookie},
                    priority=Priority.IMAGE.value,
                    extra_data={"case_id": case_id, "vehicle_num": vehicle_num},
                )
                if img_id_dict.get(img_id) is None:
                    self.request_handler.enqueue_request(request)
                    img_id_dict.update({img_id: None})
            self.case_veh_img_ids[(case_id, vehicle_num)] = img_id_dict

    def parse_image(self, url: str, response_content: bytes, extra_data: dict):
        vals = self.case_veh_img_ids.values()
        img_id = int(url.split("&")[1].split("=")[1])
        event_data = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        )
        for img_id_dict in vals:
            if img_id not in img_id_dict.keys():
                continue
            img = Image.open(BytesIO(response_content))
            img_id_dict[img_id] = img
            case_match = int(event_data["case_id"]) == extra_data["case_id"]
            veh_match = int(event_data["vehicle_num"]) == extra_data["vehicle_num"]
            if case_match and veh_match:
                self.__add_thumbnail(img_id, img, event_data)
            break

    def __add_thumbnail(self, img_id: int, image: Image.Image, data: dict):
        self.no_images_label.setVisible(False)
        thumbnail = ImageThumbnail(img_id, image, self.images_dir, data)
        self.ui.thumbnailsLayout.addWidget(thumbnail)


class ImageThumbnail(QWidget):
    def __init__(self, img_id: int, image: Image.Image, images_dir: Path, data: dict):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.img_id = img_id
        self.image = image
        self.images_dir = images_dir

        self.case_id = data["case_id"]
        self.nass_dv = data["NASS_dv"]
        self.tot_dv = data["TOT_dv"]

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

        text = f"Case No: {self.case_id} - NASS DV: {self.nass_dv:.4f} - TOT DV: {self.tot_dv:.4f}"

        draw = ImageDraw.Draw(self.image)

        width, height = self.image.size

        font_size = 100
        text_size = draw.textbbox(
            (0, 0), text, ImageFont.truetype("segoeui.ttf", font_size)
        )
        while text_size[2] - text_size[0] > width:
            font_size -= 1
            text_size = draw.textbbox(
                (0, 0), text, ImageFont.truetype("segoeui.ttf", font_size)
            )

        rect_height = text_size[3] - text_size[1] + int(height * 0.05)

        new_img = Image.new("RGB", (width, height + rect_height), (255, 255, 255))

        new_img.paste(self.image, (0, rect_height))

        draw = ImageDraw.Draw(new_img)
        draw.text(
            (0, 0),
            text,
            (0, 0, 0),
            ImageFont.truetype("segoeui.ttf", font_size),
        )

        os.makedirs(self.images_dir, exist_ok=True)

        path = self.images_dir / f"{self.img_id}.png"
        i = 1
        while path.exists():
            path = self.images_dir / f"{self.img_id}({i}).png"
            i += 1

        new_img.save(path, "PNG")
        self.logger.debug(f"Saved image to {path}")
        self.save_button.setText("Saved!")

    def open_image(self):
        self.image.show()

    def enterEvent(self, event):
        self.open_button.setVisible(True)
        self.save_button.setVisible(True)

    def leaveEvent(self, event):
        self.open_button.setVisible(False)
        self.save_button.setVisible(False)


class CustomItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        ignored = index.data(Qt.ItemDataRole.FontRole)
        if ignored:
            option.palette.setColor(QPalette.ColorRole.Text, QColor("gray"))
        else:
            option.palette.setColor(QPalette.ColorRole.Text, QColor("black"))
        super().paint(painter, option, index)
