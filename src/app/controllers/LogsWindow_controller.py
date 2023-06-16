import logging


class LogsWindowController:
    def __init__(self, widget):
        self.widget = widget
        self.logger = logging.getLogger(__name__)

        self.widget.clear_logs.connect(self.handle_clear_btn_clicked)
        self.widget.save_logs.connect(self.handle_save_btn_clicked)

    def handle_logger_message(self, msg):
        self.widget.ui.logsEdit.append(msg)

    def handle_clear_btn_clicked(self):
        self.widget.ui.logsEdit.clear()

    def handle_save_btn_clicked(self):
        ### TODO: Actually save the logs somewhere ###
        self.logger.info('Saving logs to file...')
