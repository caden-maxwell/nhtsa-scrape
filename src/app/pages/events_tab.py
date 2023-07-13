from datetime import datetime
from io import BytesIO
import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QFont, QImage
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QLabel,
    QSizePolicy,
)

from bs4 import BeautifulSoup
from PIL import Image

from app.models import ProfileEvents
from app.scrape import RequestHandler, Priority, Request, ScrapeEngine
from app.ui.EventsTab_ui import Ui_EventsTab


class EventsTab(QWidget):
    def __init__(self, model: ProfileEvents, data_dir: Path):
        super().__init__()
        self.ui = Ui_EventsTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = model
        self.model.layoutChanged.connect(self.update_scrollbar_size)
        self.images_dir = data_dir / "images"

        self.ui.eventsList.setModel(self.model)
        self.ui.eventsList.doubleClicked.connect(self.open_event_details)

        self.img_grid = ImageViewerWidget()
        self.img_grid.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.ui.gridLayout.addWidget(self.img_grid, 2, 0, 1, 2)

        self.request_handler = RequestHandler()
        self.request_handler.response_received.connect(self.handle_response)
        self.events_pending = []
        self.responses = {}

        self.previous_index = None

    def showEvent(self, event) -> None:
        self.update_scrollbar_size()
        return super().showEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.open_event_details(self.ui.eventsList.currentIndex())
        return super().keyPressEvent(event)

    def update_scrollbar_size(self):
        scrollbar = self.ui.eventsList.verticalScrollBar()
        list_size = max(self.ui.eventsList.sizeHintForColumn(0), 200)
        scrollbar_width = 0
        if scrollbar.isVisible():
            scrollbar_width = scrollbar.sizeHint().width()
        self.ui.eventsList.setFixedWidth(list_size + scrollbar_width + 4)

    def cache_response(self, case_id, response_content, cookie):
        self.responses[case_id] = {
            "cookie": cookie,
            "xml": response_content,
            "created": datetime.now(),
        }

    def open_event_details(self, index):
        # If index already open, ignore
        if self.ui.eventsList.currentIndex() == self.previous_index:
            return
        self.previous_index = index
        self.img_grid.clear_images()
        self.request_handler.clear_queue(Priority.IMAGE.value)

        for i in reversed(range(self.ui.eventLayout.count())):
            self.ui.eventLayout.itemAt(i).widget().setParent(None)

        event_data = self.model.data(index, Qt.ItemDataRole.UserRole)
        case_id = event_data["case_id"]

        COOKIE_EXPIRED_SECS = 900  # Assume that the cookie expires after 15 minutes
        if (
            case_id in self.responses
            and (datetime.now() - self.responses[case_id][1]).total_seconds()
            < COOKIE_EXPIRED_SECS
        ):
            self.parse_case(
                self.responses[case_id]["xml"], self.responses[case_id]["cookie"]
            )
            return

        request = Request(
            ScrapeEngine.CASE_URL + str(case_id), priority=Priority.CASE_FOR_IMAGE.value
        )
        self.request_handler.enqueue_request(request)
        self.events_pending.append(
            {"case_id": case_id, "vehicle_num": event_data["vehicle_num"]}
        )
        self.events_pending = list(
            {val["case_id"]: val for val in self.events_pending}.values()
        )

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

        self.ui.eventLayout.setColumnStretch(1, 1)

    @pyqtSlot(int, str, bytes, str)
    def handle_response(self, priority, url, response_content, cookie):
        if priority == Priority.CASE_FOR_IMAGE.value:
            self.parse_case(response_content, cookie)
        elif priority == Priority.IMAGE.value:
            self.parse_image(response_content)

    def parse_case(self, response_content, cookie):
        soup = BeautifulSoup(response_content, "xml")
        case_id = soup.find("CaseForm").get("caseID")
        img_form = soup.find("IMGForm")

        if not img_form:
            self.logger.debug("No ImgForm found.")
            return

        vehicle_num = None
        for pending in self.events_pending:
            if pending["case_id"] == int(case_id):
                vehicle_num = pending["vehicle_num"]
                self.events_pending.remove(pending)
                break
        if not vehicle_num:
            self.logger.warning("No matching pending event found.")
            return

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

        img_set_lookup = {}
        for k, v in veh_img_areas.items():
            img_set_lookup[k] = [
                (img.text, img["version"])
                for img in img_form.find("Vehicle", {"VehicleNumber": {vehicle_num}})
                .find(v)
                .find_all("image")
            ]

        image_set = "R"  # TODO: Get this from the UI. Default to right side for now.

        img_elements = img_set_lookup.get(image_set, [])
        for img_element in img_elements:
            img_id = img_element[0]
            img_version = img_element[1]
            img_url = f"https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID={img_id}&CaseID={case_id}&Version={img_version}"

            request = Request(
                img_url, headers={"Cookie": cookie}, priority=Priority.IMAGE.value
            )
            self.request_handler.enqueue_request(request)

    def parse_image(self, response_content):
        img = Image.open(BytesIO(response_content))
        self.img_grid.add_image(img)
        return

        if not img_elements:
            print(
                f"No images found for image set {image_set}. Attempting to set to defaults..."
            )
            veh_dmg_areas = {
                2: img_set_lookup["F"],
                5: img_set_lookup["B"],
                4: img_set_lookup["L"],
                3: img_set_lookup["R"],
            }
            img_elements = veh_dmg_areas.get(int(payload["ddlPrimaryDamage"]), [])

        fileName = "i"
        while True:
            for img_element in img_elements:
                g = input(
                    "Select: [NE]xt Image, [SA]ve Image, [DE]lete Case, [FT]ront, [FL]ront Left, [LE]ft,"
                    "[BL]ack Left, [BA]ck, [BR]ack Right, [RI]ght, [FR]ront Right: "
                )

                def check_image_set(image_set):
                    if not self.image_set:
                        self.image_set = img_set_lookup["F"]
                        if "F" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["F"]
                        elif "R" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["R"]
                        elif "B" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["B"]
                        elif "L" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["L"]
                        print("Empty Image Set")
                        return self.image_set
                    else:
                        return self.image_set

                if "sa" in g.lower():
                    caseid_path = (
                        os.getcwd()
                        + "/"
                        + self.search_payload["ddlStartModelYear"]
                        + "_"
                        + self.search_payload["ddlEndModelYear"]
                        + "_"
                        + self.search_payload["ddlMake"]
                        + "_"
                        + self.search_payload["ddlModel"]
                        + "_"
                        + self.search_payload["ddlPrimaryDamage"]
                    )
                    if not os.path.exists(caseid_path):
                        os.makedirs(caseid_path)
                    os.chdir(caseid_path)

                    img_num = str(img_element[0])
                    fileName = caseid_path + "//" + img_num + ".jpg"
                    img.save(fileName)
                    g = "de"
                    break
                elif "ne" in g.lower():
                    continue
                elif "de" in g.lower():
                    break
                elif "ft" in g.lower():
                    img_elements = check_image_set(front_images)
                    break
                elif "fr" in g.lower():
                    img_elements = check_image_set(frontright_images)
                    break
                elif "ri" in g.lower():
                    img_elements = check_image_set(right_images)
                    break
                elif "br" in g.lower():
                    img_elements = check_image_set(backright_images)
                    break
                elif "ba" in g.lower():
                    img_elements = check_image_set(back_images)
                    break
                elif "bl" in g.lower():
                    img_elements = check_image_set(backleft_images)
                    break
                elif "le" in g.lower():
                    img_elements = check_image_set(left_images)
                    break
                elif "fl" in g.lower():
                    img_elements = check_image_set(frontleft_images)
                    break
                img.close()
            if "de" in g.lower():
                break


class ImageViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.images = []

        self.v_layout = QGridLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(200)

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

    def add_image(self, img: Image.Image):
        self.images.append(img)
        self.update_images()

    def update_images(self):
        # Clear existing thumbnails
        self.no_images_label.setVisible(not len(self.images))
        for i in reversed(range(self.thumbnails_layout.count())):
            widget = self.thumbnails_layout.itemAt(i).widget()
            self.thumbnails_layout.removeWidget(widget)
            widget.setParent(None)

        # Add new thumbnails to the layout
        for img in self.images:
            thumbnail = QLabel()
            pixmap = self.convert_image_to_pixmap(img).scaledToHeight(150)
            thumbnail.setPixmap(pixmap)
            thumbnail.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            thumbnail.mouseDoubleClickEvent = img.show
            self.thumbnails_layout.addWidget(thumbnail)

    def convert_image_to_pixmap(self, img: Image.Image):
        qimg = QImage(
            img.tobytes("raw", "RGB"),
            img.size[0],
            img.size[1],
            QImage.Format.Format_RGB888,
        )
        qimg = QPixmap.fromImage(qimg)
        return qimg

    def clear_images(self):
        for img in self.images:
            img.close()
        self.images = []
        self.update_images()
