from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QApplication

from app.pages.data_view import DataView
from app.pages.logs_window import LogsWindow
from app.pages.profile_menu import ProfileMenu
from app.pages.scrape_menu import ScrapeMenu
from app.pages.settings_menu import SettingsMenu
from app.pages.main_menu import MainMenu

from app.log_handler import QtLogHandler
import logging


class MainWindowController(QWidget):
    def __init__(self):
        super().__init__()

        # Setup widgets and controllers
        self.main_menu = MainMenu()
        self.scrape_menu = ScrapeMenu()
        self.profile_menu = ProfileMenu()
        self.data_view = DataView()
        self.logs_window = LogsWindow()
        self.settings_menu = SettingsMenu()

        self.setup_logger()
        self.setup_ui()
        self.setup_signals()

    def setup_logger(self):
        log_handler = QtLogHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        log_handler.log_message.connect(self.logs_window.handle_logger_message)
        logging.basicConfig(level=logging.DEBUG, handlers=[log_handler])

    def setup_ui(self):
        # Add the controllers to the stacked widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.scrape_menu)
        self.stacked_widget.addWidget(self.profile_menu)
        self.stacked_widget.addWidget(self.data_view)
        self.stacked_widget.addWidget(self.settings_menu)

        # Set layout for the main widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def setup_signals(self):
        # Main menu signals
        self.main_menu.new_scrape_clicked.connect(self.switch_to_scrape_menu)
        self.main_menu.open_existing_clicked.connect(self.switch_to_profile_menu)
        self.main_menu.logs_clicked.connect(self.open_logs_window)
        self.main_menu.settings_clicked.connect(self.switch_to_settings_menu)

        # Scrape menu signals
        self.scrape_menu.back_button_clicked.connect(self.switch_to_main_menu)
        self.scrape_menu.scrape_finished.connect(self.switch_to_data_view)

        # Profile menu signals
        self.profile_menu.back_button_clicked.connect(self.switch_to_main_menu)
        self.profile_menu.open_profile_clicked.connect(self.switch_to_data_view)
        self.profile_menu.rescrape_clicked.connect(self.switch_to_scrape_menu)

        # Settings menu signals
        self.settings_menu.back_button_clicked.connect(self.switch_to_main_menu)

        # Data view signals:


    def switch_to_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu)
        
    def switch_to_scrape_menu(self):
        self.stacked_widget.setCurrentWidget(self.scrape_menu)
    
    def switch_to_profile_menu(self):
        self.stacked_widget.setCurrentWidget(self.profile_menu)

    def switch_to_settings_menu(self):
        self.stacked_widget.setCurrentWidget(self.settings_menu)

    def switch_to_data_view(self):
        self.stacked_widget.setCurrentWidget(self.data_view)

    def open_logs_window(self):
        self.logs_window.show()

    def closeEvent(self, event):
        QApplication.closeAllWindows()