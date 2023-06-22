import json
import logging

from PyQt6.QtCore import QThread


class ScrapeEngine(QThread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.image_set = "All"

        # Get deafult search payload
        with open("app/scrape/payload.json", "r") as f:
            self.search_payload = json.load(f)

    def update_payload(self, key, val):
        self.search_payload[key] = val
        self.logger.info(f"{key} updated to '{val}'.")

    def run(self):
        self.logger.debug( f"""Scrape engine started with these params:
{{
    make: {self.search_payload['ddlMake']},
    model: {self.search_payload['ddlModel']},
    model_start_year: {self.search_payload['ddlStartModelYear']},
    model_end_year: {self.search_payload['ddlEndModelYear']},
    dv_min: {self.search_payload['tDeltaVFrom']},
    dv_max: {self.search_payload['tDeltaVTo']},
    primary_dmg: {self.search_payload['ddlPrimaryDamage']},
    secondary_dmg: {self.search_payload['lSecondaryDamage']},
    image_set: {self.image_set}
}}"""
        )

        


        self.logger.info("Scrape engine finished.")
