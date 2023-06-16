from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QApplication
from .MainMenu_controller import MainMenuController
from .ScrapeMenu_controller import ScrapeMenuController
from .ProfileMenu_controller import ProfileMenuController
from .LogsWindow_controller import LogsWindowController
from .LoadingScreen_controller import LoadingScreenController
from .DataView_controller import DataViewController

class MainWindowController(QWidget):
    def __init__(self, log_handler):
        super().__init__()

        self.main_menu_controller = MainMenuController()
        self.scrape_menu_controller = ScrapeMenuController()
        self.profile_menu_controller = ProfileMenuController()
        self.loading_screen_controller = LoadingScreenController()
        self.data_view_controller = DataViewController()

        self.logs_window_controller = LogsWindowController()
        log_handler.log_message.connect(self.logs_window_controller.handle_logger_message)

        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        # Setup the stacked widget with the other page controllers
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.main_menu_controller)
        self.stacked_widget.addWidget(self.scrape_menu_controller)
        self.stacked_widget.addWidget(self.profile_menu_controller)
        self.stacked_widget.addWidget(self.loading_screen_controller)
        self.stacked_widget.addWidget(self.data_view_controller)

        # Set layout for the main widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.main_menu_controller)

    def setup_signals(self):
        # Main menu signals
        self.main_menu_controller.new_scrape_clicked.connect(self.change_to_scrape_menu)
        self.main_menu_controller.open_existing_clicked.connect(self.change_to_profile_menu)
        self.main_menu_controller.open_logs_clicked.connect(self.open_logs_window)

        # Scrape menu signals
        self.scrape_menu_controller.back_btn_clicked.connect(self.change_to_main_menu)
        self.scrape_menu_controller.submit_scrape.connect(self.change_to_loading_screen)

        # Profile menu signals
        self.profile_menu_controller.back_btn_clicked.connect(self.change_to_main_menu)
        self.profile_menu_controller.open_profile_clicked.connect(self.change_to_data_view)
        self.profile_menu_controller.rescrape_clicked.connect(self.change_to_scrape_menu)

        # Loading screen menu signals
        self.loading_screen_controller.cancel_btn_clicked.connect(self.change_to_scrape_menu)
        self.loading_screen_controller.stop_btn_clicked.connect(self.change_to_data_view)

        # Data view screen signals
        # self.data_view_controller.save_btn_clicked.connect(self.change_to_profile_menu)

    def change_to_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu_controller)
        
    def change_to_scrape_menu(self):
        self.stacked_widget.setCurrentWidget(self.scrape_menu_controller)

    def change_to_profile_menu(self):
        self.stacked_widget.setCurrentWidget(self.profile_menu_controller)

    def change_to_data_view(self):
        self.stacked_widget.setCurrentWidget(self.data_view_controller)

    def change_to_loading_screen(self):
        self.stacked_widget.setCurrentWidget(self.loading_screen_controller)
        
    def open_logs_window(self):
        self.logs_window_controller.show()

    def closeEvent(self, event):
        QApplication.closeAllWindows()