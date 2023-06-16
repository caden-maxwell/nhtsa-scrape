import logging


class ProfileMenuController:
    def __init__(self, widget):
        self.widget = widget
        self.logger = logging.getLogger(__name__)
