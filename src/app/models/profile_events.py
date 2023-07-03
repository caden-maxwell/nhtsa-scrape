import logging
from pathlib import Path
import sqlite3

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt


class ProfileEvents(QAbstractListModel):
    def __init__(self, profile_id):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.db = None
        self.cursor = None
        self.profile = None
        self.data_list = []

        try:
            db_path = Path(__file__).parent / "db_saves.sqlite3"
            self.db = sqlite3.connect(db_path)
            self.cursor = self.db.cursor()
            self.db.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id INTEGER PRIMARY KEY,
                    case_num TEXT,
                    summary TEXT
                );
                """
            )
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS case_events (
                    case_id INTEGER,
                    vehicle_num INTEGER,
                    event_num INTEGER,
                    make TEXT,
                    model TEXT,
                    model_year INTEGER,
                    curb_weight INTEGER,
                    dmg_loc TEXT,
                    underride TEXT,
                    edr TEXT,
                    total_dv INTEGER,
                    long_dv INTEGER,
                    lat_dv INTEGER,
                    smashl INTEGER,
                    crush1 INTEGER,
                    crush2 INTEGER,
                    crush3 INTEGER,
                    crush4 INTEGER,
                    crush5 INTEGER,
                    crush6 INTEGER,
                    a_veh_num TEXT,
                    a_make TEXT,
                    a_model TEXT,
                    a_year TEXT,
                    a_curb_weight INTEGER,
                    a_dmg_loc TEXT,
                    c_bar INTEGER,
                    NASS_dv INTEGER,
                    NASS_vc INTEGER,
                    e INTEGER,
                    TOT_dv INTEGER,
                    PRIMARY KEY (case_id, event_num, vehicle_num),
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                );
                """
            )
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS scrape_profile_events (
                    profile_id INTEGER,
                    case_id INTEGER,
                    event_num INTEGER,
                    vehicle_num INTEGER,
                    FOREIGN KEY (profile_id)
                        REFERENCES scrape_profiles(profile_id),
                    FOREIGN KEY (case_id, event_num, vehicle_num)
                        REFERENCES case_events(case_id, event_num, vehicle_num)
                );
                """
            )
            self.db.commit()
            self.profile = self.cursor.execute(
                """
                SELECT * FROM scrape_profiles WHERE profile_id = ?
                """,
                (profile_id,),
            ).fetchone()
            if self.profile is None:
                raise ValueError(f"Profile ID {profile_id} does not exist.")

        except (ValueError, sqlite3.Error) as e:
            self.logger.error(e)

    def close_database(self):
        try:
            self.cursor.close()
            self.db.close()
            self.db = None
            self.cursor = None
        except sqlite3.Error as e:
            self.logger.error(f"Error closing database: {e}")

    def rowCount(self, parent=QModelIndex()):
        return len(self.data_list)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            data = self.data_list[index.row()]
            return f"Case: {data[0]}, Vehicle: {data[2]}, Event: {data[1]}"
        if role == Qt.ItemDataRole.UserRole:
            return self.data_list[index.row()]
        return None

    def add_data(self, event):
        try:
            summary = event["summary"]
            case_num = event["case_num"]
            case_id = event["case_id"]
            veh_num = event["veh_num"]
            event_num = event["event_num"]
            make = event["make"]
            model = event["model"]
            model_year = event["model_year"]
            curb_weight = event["curb_weight"]
            dmg_loc = event["dmg_loc"]
            underride = event["underride"]
            edr = event["edr"]
            total_dv = event["total_dv"]
            long_dv = event["long_dv"]
            lat_dv = event["lat_dv"]
            smashl = event["smashl"]
            crush = event["crush"]

            a_veh_num = event["a_veh_num"]
            a_make = event["a_make"]
            a_model = event["a_model"]
            a_year = event["a_year"]
            a_curb_weight = event["a_curb_weight"]
            a_dmg_loc = event["a_dmg_loc"]

            self.cursor.execute(
                """
                INSERT OR IGNORE INTO cases (case_id, case_num, summary)
                VALUES (?, ?, ?)
                """,
                (case_id, case_num, summary),
            )
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO case_events (
                    case_id,
                    vehicle_num,
                    event_num,
                    make,
                    model,
                    model_year,
                    curb_weight,
                    dmg_loc,
                    underride,
                    edr,
                    total_dv,
                    long_dv,
                    lat_dv,
                    smashl,
                    crush1,
                    crush2,
                    crush3,
                    crush4,
                    crush5,
                    crush6,
                    a_veh_num,
                    a_make,
                    a_model,
                    a_year,
                    a_curb_weight,
                    a_dmg_loc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    veh_num,
                    event_num,
                    make,
                    model,
                    model_year,
                    curb_weight,
                    dmg_loc,
                    underride,
                    edr,
                    total_dv,
                    long_dv,
                    lat_dv,
                    smashl,
                    crush[0],
                    crush[1],
                    crush[2],
                    crush[3],
                    crush[4],
                    crush[5],
                    a_veh_num,
                    a_make,
                    a_model,
                    a_year,
                    a_curb_weight,
                    a_dmg_loc,
                ),
            )
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO scrape_profile_events (
                    profile_id,
                    case_id,
                    event_num,
                    vehicle_num
                )
                VALUES (?, ?, ?, ?)
                """,
                (self.profile[0], case_id, event_num, veh_num),
            )
            self.db.commit()
            self.logger.debug(
                f"Added case event {event_num} from case {case_id} to scrape profile {self.profile[1]}."
            )
        except (sqlite3.Error, KeyError) as e:
            self.logger.error("Error adding case:", e)
            return
        self.refresh_data()

    def delete_event(self, index):
        try:
            data = self.data_list[index.row()]
            self.cursor.execute(
                """
                DELETE FROM case_events
                WHERE (case_id, event_num, vehicle_num) = ?
                """,
                (data[0],),
            )
            self.db.commit()
        except sqlite3.Error as e:
            self.logger.error("Error deleting case:", e)
            return
        except IndexError:
            self.logger.error("Error deleting case: index out of range")
            return
        self.logger.debug(
            f"Deleted event: Case {data[1]} Event {data[2]} Vehicle {data[3]}"
        )
        self.refresh_data()

    def refresh_data(self):
        try:
            self.cursor.execute(
                """
                SELECT * FROM case_events
                WHERE (case_id, event_num, vehicle_num) IN (
                    SELECT case_id, event_num, vehicle_num FROM scrape_profile_events
                    WHERE profile_id = ?
                )
                """,
                (self.profile[0],),
            )
            self.data_list = self.cursor.fetchall()
            self.layoutChanged.emit()
        except sqlite3.Error as e:
            self.logger.error("Error refreshing data:", e)
            return
        self.logger.debug("Refreshed data.")

    def __del__(self):
        self.close_database()
