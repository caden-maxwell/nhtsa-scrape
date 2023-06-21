from .log_utils.log_handler import QtLogHandler
import logging

from PyQt6.QtWidgets import QWidget, QApplication

from .pages import MainMenu, LogsWindow, ProfileMenu, ScrapeMenu, SettingsMenu

from .ui.MainWindow_ui import Ui_MainWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_logger()
        self.setup_ui()
        self.setup_signals()

    def setup_logger(self):
        self.logs_window = LogsWindow()
        log_handler = QtLogHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        log_handler.log_message.connect(self.logs_window.handle_logger_message)
        logging.basicConfig(level=logging.DEBUG, handlers=[log_handler])
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        # Instantiate and add menus to the stacked widget
        self.main_menu = MainMenu()
        self.scrape_menu = ScrapeMenu()
        self.profile_menu = ProfileMenu()
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
        if getattr(page, "setup", None):
            page.setup()
        self.ui.stackedWidget.setCurrentWidget(page)

    def closeEvent(self, event):
        QApplication.closeAllWindows()
    