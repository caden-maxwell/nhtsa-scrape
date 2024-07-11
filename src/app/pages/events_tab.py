from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
import json
import logging
import os
from pathlib import Path
from typing import Callable
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from requests import Response

from PyQt6.QtCore import Qt, pyqtSlot, QModelIndex
from PyQt6.QtGui import QPixmap, QFont, QImage
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QStyledItemDelegate,
)

from app.pages import BaseTab
from app.models import DatabaseHandler, EventList, Event, Profile
from app.scrape import (
    RequestHandler,
    Priority,
    RequestQueueItem,
    BaseScraper,
    ScraperNASS,
    ScraperCISS,
)
from app.ui import Ui_EventsTab


@dataclass
class _CachedCase:
    COOKIE_EXPIRED_SECS = 900  # Assume site cookies expire after 15 minutes

    response: Response
    created: datetime = datetime.now()

    def expired(self):
        return (
            datetime.now() - self.created
        ).total_seconds() > self.COOKIE_EXPIRED_SECS


class EventsTab(BaseTab):
    def __init__(self, db_handler: DatabaseHandler, profile: Profile, data_dir: Path):
        super().__init__()
        self.ui = Ui_EventsTab()
        self.ui.setupUi(self)
        self._logger = logging.getLogger(__name__)

        self.model = EventList(db_handler, profile)
        self.current_index_vals = None
        self.data_dir = data_dir

        self.ui.eventsList.setModel(self.model)
        delegate = CustomItemDelegate()
        self.ui.eventsList.setItemDelegate(delegate)

        self.ui.eventsList.clicked.connect(self.open_event_details)
        self.ui.scrapeImgsBtn.clicked.connect(self._scrape_btn_clicked)
        self.ui.stopBtn.clicked.connect(self._stop_btn_clicked)
        self.ui.ignoreBtn.clicked.connect(self._ignore_event)
        self.ui.discardBtn.clicked.connect(self._delete_event)
        self.ui.saveCaseBtn.clicked.connect(self._save_case_btn_clicked)
        self.ui.saveEDRBtn.clicked.connect(self._save_edr_btn_clicked)

        self.ui.imgSetCombo.addItem("Front", "Front")
        self.ui.imgSetCombo.addItem("Back", "Back")
        self.ui.imgSetCombo.addItem("Left", "Left")
        self.ui.imgSetCombo.addItem("Right", "Right")
        self.ui.imgSetCombo.addItem("Front Left", "Frontleftoblique")
        self.ui.imgSetCombo.addItem("Front Right", "Frontrightoblique")
        self.ui.imgSetCombo.addItem("Back Left", "Backleftoblique")
        self.ui.imgSetCombo.addItem("Back Right", "Backrightoblique")

        self.no_images_label = QLabel("There are no images to display")
        font = QFont()
        font.setPointSize(14)
        self.no_images_label.setFont(font)
        self.no_images_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.imgWidgetGrid.addWidget(self.no_images_label, 0, 0)
        self.no_images_label.setVisible(True)

        self._req_handler = RequestHandler()
        self._req_handler.response_received.connect(self.handle_response)

        self.response_cache: dict[int, _CachedCase] = dict()
        self.img_cache = defaultdict(dict)  # key: event, value: dict of img_id: img

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

    def cache_response(self, case_id, response: Response):
        self.response_cache[case_id] = _CachedCase(response)

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

            self.ui.scrapeImgsBtn.setEnabled(False)
            self.ui.stopBtn.setVisible(False)
            self.ui.scrapeImgsBtn.update()
            self.ui.stopBtn.update()

            self.no_images_label.setVisible(True)
            self._clear_thumbnails()

            self.ui.ignoreBtn.setText("Ignore Event")
            return

        event: Event = self.model.data(index, Qt.ItemDataRole.UserRole).event

        # We need to get the unique values for this index so we can find it later
        # if another event is inserted before it in the list
        self.current_index_vals = (event.case_id, event.vehicle_num, event.event_num)

        # Left side of event view data
        self.ui.makeLineEdit.setText(event.make)
        self.ui.modelLineEdit.setText(event.model)
        self.ui.yearLineEdit.setText(str(event.model_year))
        self.ui.curbWeightLineEdit.setText(str(event.curb_wgt))
        self.ui.dmgLocLineEdit.setText(event.dmg_loc)
        self.ui.underrideLineEdit.setText(event.underride)

        # Right side of event view data
        self.ui.cBarLineEdit.setText(str(event.c_bar))
        self.ui.nassDVLineEdit.setText(str(event.NASS_dv))
        self.ui.nassVCLineEdit.setText(str(event.NASS_vc))
        self.ui.totDVLineEdit.setText(str(event.TOT_dv))

        # Clear and repopulate image thumbnails
        img_ids = self.img_cache[event]
        images = [(img_id, img) for img_id, img in img_ids.items() if img]

        self.no_images_label.setVisible(not len(images))
        self._clear_thumbnails()

        for img_id, img in images:
            thumbnail = ImageThumbnail(img_id, img, self.data_dir, event)
            self.ui.thumbnailsLayout.addWidget(thumbnail)

        if self.model.data(index, Qt.ItemDataRole.FontRole):
            self.ui.ignoreBtn.setText("Unignore Event")
        else:
            self.ui.ignoreBtn.setText("Ignore Event")

        self._update_buttons(event)

    def _clear_thumbnails(self):
        for i in reversed(range(self.ui.thumbnailsLayout.count())):
            widget = self.ui.thumbnailsLayout.itemAt(i).widget()
            self.ui.thumbnailsLayout.removeWidget(widget)
            widget.setParent(None)

    def _update_buttons(self, event: Event, override=False):
        """
        Update the scrape images button and stop button based on the current state of the request handler.
        Set override to True to force the buttons to be set to their scraping state.
        """
        extra_data = {"event": event}
        if self._req_handler.contains(Priority.IMAGE.value, extra_data) or override:
            self.ui.scrapeImgsBtn.setText("Scraping...")
            self.ui.scrapeImgsBtn.setEnabled(False)
            self.ui.stopBtn.setVisible(True)
        else:
            self.ui.scrapeImgsBtn.setText("Scrape Images")
            self.ui.scrapeImgsBtn.setEnabled(True)
            self.ui.stopBtn.setVisible(False)

        self.ui.scrapeImgsBtn.update()
        self.ui.stopBtn.update()

    def _scrape_btn_clicked(self):
        event: Event = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        ).event
        self._update_buttons(event, True)

        self._fetch_case_data(self._fetch_imgs)

    def _save_case_btn_clicked(self):
        self.ui.saveCaseBtn.setEnabled(False)
        self.ui.saveCaseBtn.setText("Saving...")
        self.ui.saveCaseBtn.update()

        self._fetch_case_data(self._save_case)

    def _save_edr_btn_clicked(self):
        self.ui.saveEDRBtn.setEnabled(False)
        self.ui.saveEDRBtn.setText("Saving...")
        self.ui.saveEDRBtn.update()

        self._fetch_case_data(self._fetch_edr)

    def _fetch_case_data(self, callback: Callable[[RequestQueueItem, Response], None]):
        event: Event = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        ).event

        scraper: BaseScraper = None
        if event.scraper_type == "NASS":
            scraper = ScraperNASS
        elif event.scraper_type == "CISS":
            scraper = ScraperCISS
        else:
            self._logger.error(f"Unknown scraper type: {event.scraper_type}")

        request = RequestQueueItem(
            BaseScraper.ROOT + str(scraper.case_url_raw).format(case_id=event.case_id),
            priority=Priority.EVENT_DATA.value,
            extra_data={"event": event},
            callback=callback,
        )
        cached_case = self.response_cache.get(event.case_id)
        if cached_case and not cached_case.expired():
            self._logger.debug(f"Using cached case ({event.case_id})")
            callback(request, cached_case.response)
        else:
            self._req_handler.enqueue_request(request)

    def _stop_btn_clicked(self):
        event = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        ).event

        extra_data = {"event": event}
        self._req_handler.clear_queue(Priority.EVENT_DATA.value, extra_data)
        self._req_handler.clear_queue(Priority.IMAGE.value, extra_data)

        self.ui.scrapeImgsBtn.setText("Scrape Images")
        self.ui.scrapeImgsBtn.setEnabled(True)
        self.ui.stopBtn.setVisible(False)

    def _ignore_event(self):
        index = self.ui.eventsList.currentIndex()
        self.model.setData(
            index,
            not self.model.data(index, Qt.ItemDataRole.FontRole),
            Qt.ItemDataRole.FontRole,
        )

        if self.model.data(index, Qt.ItemDataRole.FontRole):
            self.ui.ignoreBtn.setText("Unignore Event")
        else:
            self.ui.ignoreBtn.setText("Ignore Event")

    def _delete_event(self):
        button = QMessageBox.warning(
            self,
            "Delete Event",
            "Are you sure you want to delete this event? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            button == QMessageBox.StandardButton.No
            or button == QMessageBox.StandardButton.Escape
        ):
            return

        index = self.ui.eventsList.currentIndex()
        self.model.delete_event(index)

        if index.row() >= self.model.rowCount():
            index = self.model.index(self.model.rowCount() - 1, 0)

        self.ui.eventsList.setCurrentIndex(index)
        self.open_event_details(index)

    @pyqtSlot(RequestQueueItem, Response)
    def handle_response(self, request: RequestQueueItem, response: Response):
        # Make sure only the object that requested the data actually processes it
        if request.callback.__self__ == self:
            request.callback(request, response)

            event: Event = self.model.data(
                self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
            ).event
            self._update_buttons(event)

    def _fetch_imgs(self, request: RequestQueueItem, response: Response):
        event: Event = request.extra_data.get("event")
        self.cache_response(event.case_id, response)

        scraper_type = event.scraper_type
        if scraper_type == "NASS":
            self._fetch_imgs_nass(event, request, response)
        elif scraper_type == "CISS":
            self._fetch_imgs_ciss(event, request, response)

        self._update_buttons(event)

    def _fetch_imgs_nass(
        self, event: Event, request: RequestQueueItem, response: Response
    ):
        soup = BeautifulSoup(response.content, "xml")
        img_form = soup.find("IMGForm")
        cookie = response.headers.get("Set-Cookie", "")

        if not img_form:
            self._logger.debug("No ImgForm found.")
            return

        veh_img_form = img_form.find("Vehicle", {"VehicleNumber": {event.vehicle_num}})
        if not veh_img_form:
            self._logger.warning(
                f"Image form for vehicle '{event.vehicle_num}' of case '{event.case_id}' not found."
            )
            return

        form_id = self.ui.imgSetCombo.currentData()
        img_area_form = veh_img_form.find(form_id)
        if not img_area_form:
            self._logger.warning(f"Image area form '{form_id}' not found.")
            return

        image_elements = img_area_form.find_all("image")
        event_imgs = self.img_cache[event]
        for img_element in image_elements:
            img_element: BeautifulSoup
            img_id = int(img_element.text)

            # Skip if image already exists in cache
            if event_imgs.get(img_id):
                continue

            self._req_handler.enqueue_request(
                RequestQueueItem(
                    BaseScraper.ROOT
                    + str(ScraperNASS.img_url).format(
                        img_id=img_id,
                        case_id=event.case_id,
                        version=img_element["version"],
                    ),
                    headers={"Cookie": cookie},
                    priority=Priority.IMAGE.value,
                    extra_data={"event": event},
                    callback=self._parse_image,
                )
            )
            event_imgs.update({img_id: None})
        self.img_cache[event] = event_imgs

    def _fetch_imgs_ciss(
        self, event: Event, request: RequestQueueItem, response: Response
    ):
        json_data: dict = response.json()
        photos = json_data.get("Photos")

        if not photos:
            self._logger.debug("No photos found.")
            return

        veh_photos = []
        for photo in photos:
            if int(photo.get("VehNum")) == event.vehicle_num:
                veh_photos.append(photo)

        if not veh_photos:
            self._logger.warning(
                f"No photos found for vehicle '{event.vehicle_num}' of case '{event.case_id}'."
            )
            return

        sorted_photos = defaultdict(list)
        for photo in veh_photos:
            dmg_text = photo.get("SubTypeText", "")
            dmg_text = dmg_text.lower().replace(" ", "").replace("plane", "")
            sorted_photos[dmg_text].append(photo)

        img_set = self.ui.imgSetCombo.currentData()
        if not img_set:
            self._logger.error("No image set selected.")
            return

        filtered_photos = sorted_photos.get(img_set.lower(), [])

        event_imgs = self.img_cache[event]
        for photo in filtered_photos:
            obj_id = photo.get("ObjectId")

            if event_imgs.get(obj_id):
                continue

            self._req_handler.enqueue_request(
                RequestQueueItem(
                    BaseScraper.ROOT + str(ScraperCISS.img_url).format(obj_id=obj_id),
                    priority=Priority.IMAGE.value,
                    extra_data={"event": event},
                    callback=self._parse_image,
                )
            )
            event_imgs.update({obj_id: None})
        self.img_cache[event] = event_imgs

    def _parse_image(self, request: RequestQueueItem, response: Response):
        event: Event = request.extra_data.get("event")
        event_imgs = self.img_cache[event]

        img_key = ""
        if event.scraper_type == "NASS":
            img_key = int(request.url.split("&")[1].split("=")[1])
        elif event.scraper_type == "CISS":
            img_key = request.url.split("/")[5]

        image = Image.open(BytesIO(response.content))

        w, h = image.size
        aspect_ratio = w / h
        if aspect_ratio < 1:
            # image is portrait, make width at least 1080
            w = 1080
            h = round(w / aspect_ratio)
        else:
            # image is landscape, make width at least 1920
            w = 1920
            h = round(w / aspect_ratio)

        image = image.resize((w, h))

        event_imgs[img_key] = image

        selected_event: Event = self.model.data(
            self.ui.eventsList.currentIndex(), Qt.ItemDataRole.UserRole
        ).event

        # If the event is the same as the one currently selected, update the thumbnails
        if event == selected_event:
            self.no_images_label.setVisible(False)
            thumbnail = ImageThumbnail(img_key, image, self.data_dir, event)
            self.ui.thumbnailsLayout.addWidget(thumbnail)

    def _save_case(self, request: RequestQueueItem, response: Response):
        event: Event = request.extra_data.get("event")
        self.cache_response(event.case_id, response)

        raw_data_dir = self.data_dir / f"case_{event.case_id}"
        os.makedirs(raw_data_dir, exist_ok=True)

        # Check whether data is json or xml
        filename = "case"
        if "application/json" in response.headers.get("Content-Type", ""):
            self._save_json_case(event, response, raw_data_dir, filename)
        elif "text/xml" in response.headers.get("Content-Type", ""):
            self._save_xml_case(event, response, raw_data_dir, filename)
        else:
            self._logger.error(
                f"Returned case has unknown content type: {response.headers.get('Content-Type')}"
            )

        self.ui.saveCaseBtn.setEnabled(True)
        self.ui.saveCaseBtn.setText("Save Raw Case Data")
        self.ui.saveCaseBtn.update()

    def _save_json_case(
        self, event: Event, response: Response, raw_data_dir: Path, filename: str
    ):
        # Create a unique file name
        filename = filename + ".json"
        raw_data_path = raw_data_dir / filename
        i = 1
        while raw_data_path.exists():
            raw_data_path = raw_data_dir / filename.replace(".", f"({i}).")
            i += 1

        # Pretty-print the JSON data to the file
        with open(raw_data_path, "w") as f:
            data = json.loads(response.text)
            data = json.dumps(data, indent=4)
            f.write(data)

        self._logger.info(
            f"Saved JSON case data for case {event.case_id} to {raw_data_path}"
        )

    def _save_xml_case(
        self, event: Event, response: Response, edr_data_dir: Path, filename: str
    ):
        # Create a unique file name
        filename = filename + ".xml"
        raw_data_path = edr_data_dir / filename
        i = 1
        while raw_data_path.exists():
            raw_data_path = edr_data_dir / filename.replace(".", f"({i}).")
            i += 1

        # Write pretty-printed XML data to the file
        with open(raw_data_path, "wb") as f:
            soup = BeautifulSoup(response.content, "xml")
            f.write(soup.prettify("utf-8"))

        self._logger.info(
            f"Saved XML case data for case {event.case_id} to {raw_data_path}"
        )

    def _fetch_edr(self, request: RequestQueueItem, response: Response):
        event: Event = request.extra_data.get("event")
        self.cache_response(event.case_id, response)

        edr_data_dir = self.data_dir / f"case_{event.case_id}" / "edr"
        os.makedirs(edr_data_dir, exist_ok=True)

        if event.scraper_type == "NASS":
            self._fetch_nass_edr(event, response, edr_data_dir)
        elif event.scraper_type == "CISS":
            self._fetch_ciss_edr(event, response, edr_data_dir)
        else:
            self._logger.error(f"Unknown scraper type: {event.scraper_type}")

        self.ui.saveEDRBtn.setEnabled(True)
        self.ui.saveEDRBtn.setText("Fetch Event EDR")
        self.ui.saveEDRBtn.update()

    def _fetch_nass_edr(self, event: Event, response: Response, edr_data_dir: Path):
        QMessageBox.warning(
            self,
            "Not Yet Implemented",
            "NASS EDR data fetcher not yet implemented.",
            QMessageBox.StandardButton.Ok,
        )
        self._logger.error("NASS EDR data fetcher not yet implemented.")

    def _fetch_ciss_edr(self, event: Event, response: Response, edr_data_dir: Path):
        json_data: dict = response.json()
        docs = json_data.get("Docs")

        edr_docs = []
        for doc in docs:
            if (
                doc.get("DocTypeDesc") == "EDR"
                and doc.get("VehNum") == event.vehicle_num
            ):
                edr_docs.append(doc)

        if not edr_docs:
            QMessageBox.warning(
                self,
                "No EDR Data",
                "No EDR data found for this vehicle.",
                QMessageBox.StandardButton.Ok,
            )
            return

        filenames = []
        for doc in edr_docs:
            filenames.append(doc.get("FileName"))

        filenames_str = "\n ".join(filenames)
        button = QMessageBox.question(
            self,
            "EDR Data Found",
            f"EDR data found for this vehicle. Would you like to save it?\n{filenames_str}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if (
            button == QMessageBox.StandardButton.No
            or button == QMessageBox.StandardButton.Escape
        ):
            self._logger.debug("User chose not to save EDR data.")
            return

        for doc in edr_docs:
            filename = doc.get("FileName")
            obj_id = doc.get("ObjectID")
            request = RequestQueueItem(
                BaseScraper.ROOT
                + str(ScraperCISS.edr_url).format(filename=filename, obj_id=obj_id),
                priority=Priority.EVENT_DATA.value,
                extra_data={"event": event, "dir": edr_data_dir, "filename": filename},
                callback=self._save_ciss_edr,
            )
            self._req_handler.enqueue_request(request)

    def _save_ciss_edr(self, request: RequestQueueItem, response: Response):
        filename = response.headers["Content-Disposition"].split("filename=")[1]

        event: Event = request.extra_data.get("event")
        edr_dir: Path = request.extra_data.get("dir")
        filename: str = request.extra_data.get("filename")

        # Create a unique file name
        edr_data_path = edr_dir / filename
        i = 1
        while edr_data_path.exists():
            edr_data_path = edr_dir / filename.replace(".", f"({i}).")
            i += 1

        # Write the EDR data to the file
        with open(edr_data_path, "wb") as f:
            f.write(response.content)

        self._logger.info(f"Saved EDR data for case {event.case_id} to {edr_data_path}")

    def closeEvent(self, event):
        self._req_handler.clear_queue(Priority.EVENT_DATA.value)
        self._req_handler.clear_queue(Priority.IMAGE.value)
        self._logger.debug("Cleared image requests.")


class ImageThumbnail(QWidget):
    def __init__(self, img_id: int, image: Image.Image, data_dir: Path, event: Event):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.img_id = img_id
        self.image = image
        self.data_dir = data_dir

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
        self.save_button.clicked.connect(lambda: self.save_image(event))
        h_layout.addWidget(self.save_button)

        layout.addLayout(h_layout, 0, 0, Qt.AlignmentFlag.AlignBottom)

        self.setLayout(layout)

    def img_to_pixmap(self, img: Image.Image):
        pixmap = QPixmap()

        # If img.size is not on a byte boundary, .fromImage will crash without throwing an error
        # We have a problematic image that is 1919 x 1079, for example. We need to resize it to 1920 x 1080
        if img.size[0] % 8 != 0 or img.size[1] % 8 != 0:
            img = img.resize(((img.size[0] + 7) // 8 * 8, (img.size[1] + 7) // 8 * 8))

        try:
            qimg = QImage(
                img.tobytes("raw", "RGB"),
                img.size[0],
                img.size[1],
                QImage.Format.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(qimg)
        except Exception as e:
            self.logger.error(f"Error converting image to pixmap: {e}")
            pixmap = QPixmap()

        return pixmap

    def save_image(self, event: Event):
        self.save_button.setEnabled(False)
        self.save_button.setText("Saving...")

        text = f"Case No: {event.case_id} - NASS DV: {event.NASS_dv:.4f} - TOT DV: {event.TOT_dv:.4f}"
        draw = ImageDraw.Draw(self.image)

        width, height = self.image.size
        font_size = 100
        font = ImageFont.truetype("segoeui.ttf", font_size)
        text_length = draw.textlength(text, font)

        # Iteratively make the text size smaller until it fits in the width of the image
        while text_length > width:
            font_size -= 1
            font = ImageFont.truetype("segoeui.ttf", font_size)
            text_length = draw.textlength(text, font)

        x1, y1, x2, y2 = draw.textbbox((0, 0), text, font)
        _, h = x2 - x1, y2 - y1
        text_rect_height = h + (y1 * 2)

        # Stitch the text block to the top of the image so we dont lose any info
        new_img = Image.new("RGB", (width, height + text_rect_height), (255, 255, 255))
        new_img.paste(self.image, (0, text_rect_height))

        draw = ImageDraw.Draw(new_img)
        draw.text(xy=(0, 0), text=text, fill=(0, 0, 0), font=font)

        case_dir = self.data_dir / f"case_{event.case_id}" / "images"
        os.makedirs(case_dir, exist_ok=True)

        path = case_dir / f"{self.img_id}.png"
        i = 1
        while path.exists():
            path = case_dir / f"{self.img_id}({i}).png"
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
        painter.setOpacity(0.4 if ignored else 1.0)
        super().paint(painter, option, index)
