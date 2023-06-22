import logging

from PyQt6.QtCore import QThread


class ScrapeEngine(QThread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.model_start_year = "All"
        self.model_end_year = "All"
        self.make = "All"
        self.model = "All"
        self.dv_max = 0
        self.dv_max = 0
        self.primary_dmg = "All"
        self.secondary_dmg = "All"
        self.image_set = "All"

    def set_param(self, value):
        sender = self.sender()
        match sender.objectName():
            case "startYearCombo": self.model_start_year = value
            case "endYearCombo": self.model_end_year = value
            case "makeCombo": self.make = value
            case "modelCombo": self.model = value
            case "dvMinSpin": self.dv_min = value
            case "dvMaxSpin": self.dv_max = value
            case "pDmgCombo": self.primary_dmg = value
            case "sDmgCombo": self.secondary_dmg = value
            case "imageSetCombo": self.image_set = value
            case _: self.logger.error(f"Invalid sender: {sender.objectName()}"); return
        self.logger.debug(f"Set {sender.objectName()} to {value}")

    def run(self):
        self.logger.debug( f"""Scrape engine started with these params:
{{
    start_year: {self.start_year}
    end_year: {self.end_year}
    make: {self.make}
    model: {self.model}
    dv_min: {self.dv_min}
    dv_max: {self.dv_max}
    primary_dmg: {self.primary_dmg}
    secondary_dmg: {self.secondary_dmg}
    image_set: {self.image_set}
}}"""
        )


        self.logger.info("Scrape engine finished.")
