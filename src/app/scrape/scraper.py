import logging

from PyQt6.QtCore import QThread


class ScrapeEngine(QThread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.start_year = "All"
        self.end_year = "All"
        self.make = "All"
        self.model = "All"
        self.dv_min = 0
        self.dv_max = 0
        self.primary_dmg = "All"
        self.secondary_dmg = "All"
        self.image_set = "All"

    def set_param(self, param, value):
        match param:
            case "start_year": self.start_year = value
            case "end_year": self.end_year = value
            case "make": self.make = value
            case "model": self.model = value
            case "dv_min": self.dv_min = value
            case "dv_max": self.dv_max = value
            case "primary_dmg": self.primary_dmg = value
            case "secondary_dmg": self.secondary_dmg = value
            case "image_set": self.image_set = value
            case _: self.logger.error(f"Invalid param: {param}"); return

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
