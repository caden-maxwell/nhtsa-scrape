import logging
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QCloseEvent

from app.log_utils import QtLogHandler, ColorFormatter
from app.pages import MainMenu, LogsWindow, ProfileMenu, ScrapeMenu, SettingsMenu
from app.scrape import RequestHandler
from app.models import DatabaseHandler
from app.ui import Ui_MainWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.req_handler = RequestHandler()
        path = Path(__file__).parent.parent / "app.db"
        self.db_handler = DatabaseHandler(path)

        self.req_thread = QThread()
        self.req_handler.moveToThread(self.req_thread)
        self.req_thread.started.connect(self.req_handler.start)

        # Setup logger
        self.logs_window = LogsWindow()
        self.log_handler = QtLogHandler()
        self.log_handler.setFormatter(
            ColorFormatter("%(levelname)s - %(name)s - %(message)s")
        )
        self.log_handler.setLevel(logging.DEBUG)
        self.log_handler.log_message.connect(self.logs_window.handle_logger_message)
        logging.basicConfig(level=logging.DEBUG, handlers=[self.log_handler])
        self.logger = logging.getLogger(__name__)

        # Setup menus
        self.mainMenuPage = MainMenu()
        self.scrapeMenuPage = ScrapeMenu(self.db_handler)
        self.profilesMenuPage = ProfileMenu(self.db_handler)
        self.settingsMenuPage = SettingsMenu()
        self.ui.stackedWidget.addWidget(self.mainMenuPage)
        self.ui.stackedWidget.addWidget(self.scrapeMenuPage)
        self.ui.stackedWidget.addWidget(self.profilesMenuPage)
        self.ui.stackedWidget.addWidget(self.settingsMenuPage)

        self.req_handler.started.connect(self.scrapeMenuPage.fetch_search)
        self.req_thread.start()

        # Setup signals
        back_btns = [
            self.scrapeMenuPage.back,
            self.profilesMenuPage.back,
            self.settingsMenuPage.back,
        ]
        for btn in back_btns:
            btn.connect(
                lambda: self.ui.stackedWidget.setCurrentWidget(self.mainMenuPage)
            )

        self.mainMenuPage.new.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.scrapeMenuPage)
        )
        self.mainMenuPage.existing.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.profilesMenuPage)
        )
        self.mainMenuPage.settings.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.settingsMenuPage)
        )
        self.mainMenuPage.logs.connect(self.logs_window.show)

    def closeEvent(self, event: QCloseEvent):
        """Safely close all threads/processes"""

        reply = QMessageBox.question(
            self,
            "Close Application",
            "Are you sure you want to close the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Logger
            self.logger.removeHandler(self.log_handler)
            self.log_handler.threadpool.waitForDone()

            # Request handler
            self.req_handler.stop()
            self.req_thread.quit()
            self.req_thread.wait()
            self.scrapeMenuPage.cleanup()

            # Database connection
            self.db_handler.close_connection()

            # Wait for all signals/slots to finish
            QApplication.processEvents()

            QApplication.closeAllWindows()
            event.accept()
            return super().closeEvent(event)
        else:
            event.ignore()
