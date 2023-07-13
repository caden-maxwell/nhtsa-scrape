import logging
from pathlib import Path

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
    def __init__(self, model: ProfileEvents, data_dir: Path):
        super().__init__()
        self.ui = Ui_EventsTab()
        self.ui.setupUi(self)
        self.logger = logging.getLogger(__name__)

        self.model = model
        self.model.layoutChanged.connect(self.update_size)
        self.images_dir = data_dir / "images"

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

        # TODO: Download images from NHTSA if they don't already exist
        img_paths = []
        if self.images_dir.exists():
            img_paths = [
                str(img_path)
                for img_path in self.images_dir.iterdir()
                if img_path.is_file()
            ]
        self.img_grid.update_images(img_paths)

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

    def get_event_images(self, url, response_text, cookie):
        return

        img_form = case_xml.find("IMGForm")
        if not img_form:
            print("No ImgForm found.")
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
                for img in img_form.find("Vehicle", {"VehicleNumber": event["voi"]})
                .find(v)
                .find_all("image")
            ]

        image_set = image_set.split(" ")[0]
        img_elements = img_set_lookup.get(image_set, [])

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
                img_url = (
                    "https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID="
                    + str(img_element[0])
                    + "&CaseID="
                    + caseid
                    + "&Version="
                    + str(img_element[1])
                )
                print(f"Image URL: {img_url}")

                cookie = {"Cookie": response.headers["Set-Cookie"]}
                response = requests.get(img_url, headers=cookie)
                img = Image.open(BytesIO(response.content))
                draw = ImageDraw.Draw(img)
                draw.rectangle(((0, 0), (300, 30)), fill="white")
                tot_mph = str(float(tot) * 0.6214)
                img_text = "Case No: " + caseid + " - NASS DV: " + tot_mph
                draw.text(
                    (0, 0),
                    img_text,
                    (220, 20, 60),
                    font=ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 24),
                )
                img.show()
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
        self.image_paths = []

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

    def update_images(self, image_paths):
        self.no_images_label.setVisible(not len(image_paths))
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

    def create_mouse_press_event(self, image_path):
        def mouse_press_event(event):
            print(f"Opening image: {image_path}")

            ### TODO: Open image in a new window

        return mouse_press_event
