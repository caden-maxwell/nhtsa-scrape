from datetime import datetime
from io import BytesIO
import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QFont, QImage
from PyQt6.QtWidgets import QWidget, QLabel, QLabel

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
        self.ui.eventsList.doubleClicked.connect(self.open_event_details)
        self.ui.scrapeBtn.clicked.connect(self.scrape_images)
        self.ui.discardBtn.clicked.connect(self.discard_event)

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

    def open_event_details(self, index):
        self.update_images()

        for i in reversed(range(self.ui.eventLayoutLeft.count())):
            self.ui.eventLayoutLeft.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.ui.eventLayoutRight.count())):
            self.ui.eventLayoutRight.itemAt(i).widget().setParent(None)

        event_data = self.model.data(index, Qt.ItemDataRole.UserRole)

        keys_left_side = set(
            ["make", "model", "model_year", "curb_weight", "dmg_loc", "underride"]
        )

        left_col_data = {k: v for k, v in event_data.items() if k in keys_left_side}
        for i, (key, value) in enumerate(left_col_data.items()):
            key_label = QLabel(str(key) + ":")
            key_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            key_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            font = key_label.font()
            font.setWeight(QFont.Weight.Bold)
            key_label.setFont(font)
            self.ui.eventLayoutLeft.addWidget(key_label, i + 1, 0)

            value_label = QLabel(str(value))
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.ui.eventLayoutLeft.addWidget(value_label, i + 1, 1)

        keys_right_side = set(["c_bar", "NASS_dv", "NASS_vc", "TOT_dv"])

        event_data_right = {k: v for k, v in event_data.items() if k in keys_right_side}
        for i, (key, value) in enumerate(event_data_right.items()):
            key_label = QLabel(str(key) + ":")
            key_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            key_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            font = key_label.font()
            font.setWeight(QFont.Weight.Bold)
            key_label.setFont(font)
            self.ui.eventLayoutRight.addWidget(key_label, i + 1, 0)

            value_label = QLabel(f"{value:.2f}")
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.ui.eventLayoutRight.addWidget(value_label, i + 1, 1)

    def scrape_images(self):
        event_data = self.model.data(self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole)
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

    def discard_event(self):
        pass

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

        pending_veh_nums = [
            key[1]
            for key in self.case_veh_img_ids.keys()
            if key[0] == case_id and not self.case_veh_img_ids[key]
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

        for vehicle_num in pending_veh_nums:
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

            image_set = "R"  # TODO: Get the actual value from the UI.

            img_elements = img_set_lookup.get(image_set, [])
            for img_element in img_elements:
                img_id = img_element[0]
                img_version = img_element[1]
                img_url = f"https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID={img_id}&CaseID={case_id}&Version={img_version}"

                request = Request(
                    img_url, headers={"Cookie": cookie}, priority=Priority.IMAGE.value
                )
                self.request_handler.enqueue_request(request)
                self.case_veh_img_ids[(case_id, vehicle_num)].append(int(img_id))

    def parse_image(self, url, response_content):
        img_id = int(url.split("&")[1].split("=")[1])
        img = Image.open(BytesIO(response_content))
        self.vehicle_imgs[img_id] = img
        self.update_images()

    def update_images(self):
        current_idx = self.ui.eventsList.currentIndex()
        event_data = self.model.data(current_idx, Qt.ItemDataRole.UserRole)
        img_ids = self.case_veh_img_ids.get((int(event_data["case_id"]), int(event_data["vehicle_num"])), [])
        images = [self.vehicle_imgs.get(img_id) for img_id in img_ids]
        images = [img for img in images if img]

        self.no_images_label.setVisible(not len(images))
        for i in reversed(range(self.ui.thumbnailsLayout.count())):
            widget = self.ui.thumbnailsLayout.itemAt(i).widget()
            self.ui.thumbnailsLayout.removeWidget(widget)
            widget.setParent(None)

        for img in images:
            thumbnail = QLabel()
            pixmap = self.img_to_pixmap(img).scaledToHeight(150)
            thumbnail.setPixmap(pixmap)
            thumbnail.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            thumbnail.mouseDoubleClickEvent = img.show
            self.ui.thumbnailsLayout.addWidget(thumbnail)

    def img_to_pixmap(self, img: Image.Image):
        qimg = QImage(
            img.tobytes("raw", "RGB"),
            img.size[0],
            img.size[1],
            QImage.Format.Format_RGB888,
        )
        qimg = QPixmap.fromImage(qimg)
        return qimg
