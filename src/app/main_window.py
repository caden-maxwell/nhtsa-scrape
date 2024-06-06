import logging
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import QThread

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
        path = Path(__file__).parent.parent / "db.sqlite3"
        self.db_handler = DatabaseHandler(path)

        self.req_thread = QThread()
        self.req_handler.moveToThread(self.req_thread)
        self.req_thread.started.connect(self.req_handler.start)

        self.setup_logger()
        self.setup_ui()
        self.setup_signals()

        self.req_thread.start()

    def setup_logger(self):
        self.logs_window = LogsWindow()

        self.log_handler = QtLogHandler()
        self.log_handler.setFormatter(
            ColorFormatter("%(levelname)s - %(name)s - %(message)s")
        )
        self.log_handler.setLevel(logging.DEBUG)
        self.log_handler.log_message.connect(self.logs_window.handle_logger_message)
        logging.basicConfig(level=logging.DEBUG, handlers=[self.log_handler])
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        # Instantiate and add menus to the stacked widget
        self.main_menu = MainMenu()
        self.scrape_menu = ScrapeMenu(self.db_handler)
        self.req_handler.started.connect(self.scrape_menu.fetch_search)
        self.profile_menu = ProfileMenu(self.db_handler)
        self.settings_menu = SettingsMenu()
        self.ui.stackedWidget.addWidget(self.main_menu)
        self.ui.stackedWidget.addWidget(self.scrape_menu)
        self.ui.stackedWidget.addWidget(self.profile_menu)
        self.ui.stackedWidget.addWidget(self.settings_menu)

        self.ui.stackedWidget.setCurrentWidget(self.main_menu)

    def setup_signals(self):
        # If a menu has a back signal, connect it to switch to the main menu
        for idx in range(self.ui.stackedWidget.count()):
            menu = self.ui.stackedWidget.widget(idx)
            if getattr(menu, "back", None):
                menu.back.connect(lambda: self.switch_page(self.main_menu))

        self.main_menu.new.connect(lambda: self.switch_page(self.scrape_menu))
        self.main_menu.existing.connect(lambda: self.switch_page(self.profile_menu))
        self.main_menu.settings.connect(lambda: self.switch_page(self.settings_menu))
        self.main_menu.logs.connect(self.logs_window.show)

    def switch_page(self, page):
        self.ui.stackedWidget.setCurrentWidget(page)

    def closeEvent(self, event):
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
            self.scrape_menu.cleanup()

            # Database connection
            self.db_handler.close_connection()
            QApplication.closeAllWindows()
            event.accept()
            return super().closeEvent(event)
        else:
            event.ignore()
