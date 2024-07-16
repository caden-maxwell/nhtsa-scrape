import logging
from pathlib import Path
from datetime import datetime

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

        self._req_handler = RequestHandler()
        path = Path(__file__).parent.parent / "app.db"
        self._db_handler = DatabaseHandler(path)

        self._req_thread = QThread()
        self._req_handler.moveToThread(self._req_thread)
        self._req_thread.started.connect(self._req_handler.start)

        # Setup logger
        self._logs_window = LogsWindow()
        self._log_handler = QtLogHandler()
        self._log_handler.setFormatter(
            ColorFormatter("%(levelname)s - %(name)s - %(message)s")
        )
        self._log_handler.setLevel(logging.DEBUG)
        self._log_handler.log_message.connect(self._logs_window.handle_logger_message)
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[self._log_handler, logging.FileHandler("app.log")],
        )
        self._logger = logging.getLogger(__name__)
        # Clear the logs file
        open("app.log", "w").close()
        self._logger.info("This logs file serves to record all logs from the most recent application run.")
        self._logger.info(f"Application started at {datetime.now()}")

        # Setup menus
        self._mainMenuPage = MainMenu()
        self._settingsMenuPage = SettingsMenu(self._req_handler)
        data_dir = self._settingsMenuPage.get_save_path()
        self._scrapeMenuPage = ScrapeMenu(self._req_handler, self._db_handler, data_dir)
        self._profilesMenuPage = ProfileMenu(self._req_handler, self._db_handler, data_dir)
        self.ui.stackedWidget.addWidget(self._mainMenuPage)
        self.ui.stackedWidget.addWidget(self._scrapeMenuPage)
        self.ui.stackedWidget.addWidget(self._profilesMenuPage)
        self.ui.stackedWidget.addWidget(self._settingsMenuPage)

        self._req_handler.started.connect(self._scrapeMenuPage.fetch_search)
        self._req_thread.start()

        # Setup signals
        back_btns = [
            self._scrapeMenuPage.back,
            self._profilesMenuPage.back,
            self._settingsMenuPage.back,
        ]
        for btn in back_btns:
            btn.connect(
                lambda: self.ui.stackedWidget.setCurrentWidget(self._mainMenuPage)
            )

        self._mainMenuPage.new.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self._scrapeMenuPage)
        )
        self._mainMenuPage.existing.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self._profilesMenuPage)
        )
        self._mainMenuPage.settings.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self._settingsMenuPage)
        )
        self._mainMenuPage.logs.connect(self._logs_window.show)

        self._settingsMenuPage.save_path_changed.connect(self._profilesMenuPage.data_dir_changed)
        self._settingsMenuPage.save_path_changed.connect(self._scrapeMenuPage.data_dir_changed)

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
            self._logger.removeHandler(self._log_handler)
            self._log_handler.threadpool.waitForDone()

            # Request handler
            self._req_handler.stop()
            self._req_thread.quit()
            self._req_thread.wait()
            self._scrapeMenuPage.cleanup()

            # Database connection
            self._db_handler.close_connection()

            # Wait for all signals/slots to finish
            QApplication.processEvents()

            QApplication.closeAllWindows()
            event.accept()
            return super().closeEvent(event)
        else:
            event.ignore()
