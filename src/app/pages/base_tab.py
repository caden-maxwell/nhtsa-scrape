from PyQt6.QtWidgets import QWidget


class BaseTab(QWidget):
    def __init__(self):
        super().__init__()

    def refresh_tab(self):
        pass