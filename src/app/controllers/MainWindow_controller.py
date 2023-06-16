from PyQt6.QtWidgets import (
    QWidget, QStackedWidget, QVBoxLayout, QApplication
)

from .DataView_controller import DataViewController
from .LogsWindow_controller import LogsWindowController
from .ProfileMenu_controller import ProfileMenuController
from .ScrapeMenu_controller import ScrapeMenuController
from .SettingsMenu_controller import SettingsMenuController

from app.widgets.DataViewWidget import DataViewWidget
from app.widgets.LogsWindowWidget import LogsWindowWidget
from app.widgets.MainMenuWidget import MainMenuWidget
from app.widgets.ProfileMenuWidget import ProfileMenuWidget
from app.widgets.ScrapeMenuWidget import ScrapeMenuWidget
from app.widgets.SettingsMenuWidget import SettingsMenuWidget

from app.logger_utils.log_handler import QtLogHandler
import logging


class MainWindowController(QWidget):
    def __init__(self):
        super().__init__()

        # Setup widgets and controllers
        self.main_menu_widget = MainMenuWidget()

        self.scrape_menu_widget = ScrapeMenuWidget()
        self.scrape_menu_controller = ScrapeMenuController(self.scrape_menu_widget)

        self.profile_menu_widget = ProfileMenuWidget()
        self.profile_menu_controller = ProfileMenuController(self.profile_menu_widget)

        self.data_view_widget = DataViewWidget()
        self.data_view_controller = DataViewController(self.data_view_widget)

        self.logs_window_widget = LogsWindowWidget()
        self.logs_window_controller = LogsWindowController(self.logs_window_widget)

        self.settings_menu_widget = SettingsMenuWidget()
        self.settings_menu_controller = SettingsMenuController(self.settings_menu_widget)

        self.menu_history = []

        self.setup_logger()
        self.setup_ui()
        self.setup_signals()

    def setup_logger(self):
        log_handler = QtLogHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        log_handler.log_message.connect(self.logs_window_controller.handle_logger_message)
        logging.basicConfig(level=logging.DEBUG, handlers=[log_handler])

    def setup_ui(self):
        # Add the controllers to the stacked widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.main_menu_widget)
        self.stacked_widget.addWidget(self.scrape_menu_widget)
        self.stacked_widget.addWidget(self.profile_menu_widget)
        self.stacked_widget.addWidget(self.data_view_widget)
        self.stacked_widget.addWidget(self.settings_menu_widget)

        # Set layout for the main widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.main_menu_widget)

    def setup_signals(self):
        # Main menu signals
        self.main_menu_widget.new_scrape_clicked.connect(self.switch_to_scrape_menu)
        self.main_menu_widget.open_existing_clicked.connect(self.switch_to_profile_menu)
        self.main_menu_widget.logs_clicked.connect(self.open_logs_window)
        self.main_menu_widget.settings_clicked.connect(self.switch_to_settings_menu)

        # Scrape menu signals
        self.scrape_menu_widget.back_button_clicked.connect(self.switch_to_main_menu)
        self.scrape_menu_controller.scrape_finished.connect(self.switch_to_data_view)

        # Profile menu signals
        self.profile_menu_widget.back_button_clicked.connect(self.switch_to_main_menu)
        self.profile_menu_widget.open_profile_clicked.connect(self.switch_to_data_view)
        self.profile_menu_widget.rescrape_clicked.connect(self.switch_to_scrape_menu)

        # Settings menu signals
        self.settings_menu_widget.back_button_clicked.connect(self.switch_to_main_menu)

        # Data view signals:


    def switch_to_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu_widget)
        
    def switch_to_scrape_menu(self):
        self.stacked_widget.setCurrentWidget(self.scrape_menu_widget)
    
    def switch_to_profile_menu(self):
        self.stacked_widget.setCurrentWidget(self.profile_menu_widget)

    def switch_to_settings_menu(self):
        self.stacked_widget.setCurrentWidget(self.settings_menu_widget)

    def switch_to_data_view(self):
        self.stacked_widget.setCurrentWidget(self.data_view_widget)

    def open_logs_window(self):
        self.logs_window_widget.show()

    def closeEvent(self, event):
        QApplication.closeAllWindows()