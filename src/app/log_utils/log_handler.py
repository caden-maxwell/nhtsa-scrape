import logging

from PyQt6.QtCore import QObject, QThreadPool, QRunnable, pyqtSignal


class QtLogHandler(logging.Handler, QObject):
    log_message = pyqtSignal(str)

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.threadpool = QThreadPool()

    def emit(self, record):
        task = LogTask(self, record)
        self.threadpool.start(task)

    def handle(self, record):
        msg = self.format(record)
        self.log_message.emit(msg)

    def flush(self):
        pass


class LogTask(QRunnable):
    def __init__(self, handler: QtLogHandler, record):
        super().__init__()
        self.handler = handler
        self.record = record

    def run(self):
        self.handler.handle(self.record)
