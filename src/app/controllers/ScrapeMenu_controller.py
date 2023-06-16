import logging

from PyQt6.QtCore import QObject, pyqtSignal

from app.widgets.LoadingDialog import LoadingWindowWidget


class ScrapeMenuController(QObject):
    scrape_finished = pyqtSignal()

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.logger = logging.getLogger(__name__)
        self.loading_window_controller = LoadingWindowController()

        self.widget.submit_button_clicked.connect(self.handle_submission)

    def handle_submission(self):
        self.loading_window_controller.show()
    

class LoadingWindowController(QObject):
    def __init__(self):
        super().__init__()
        self.widget = LoadingWindowWidget()
        self.logger = logging.getLogger(__name__)

        self.widget.cancel_btn_clicked.connect(self.handle_cancel_button_clicked)
        self.widget.view_btn_clicked.connect(self.handle_view_button_clicked)

    def show(self):
        self.widget.exec()

    def handle_cancel_button_clicked(self):
        self.logger.info("Cancel button clicked")
        self.widget.close()

    def handle_view_button_clicked(self):
        ### TODO: Add logic to get scraped data and export to data viewer ###
        self.logger.info("View button clicked")
        self.widget.close()