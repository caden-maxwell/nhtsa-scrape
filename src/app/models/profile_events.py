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
        try:
            db_path = Path(__file__).parent / "db_saves.sqlite3"
            self.db = sqlite3.connect(db_path)
            self.cursor = self.db.cursor()
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
                    event_num INTEGER,
                    vehicle_num INTEGER,
                    make TEXT,
                    model TEXT,
                    model_year INTEGER,
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
                    FOREIGN KEY (profile_id) REFERENCES scrape_profiles(profile_id),
                    FOREIGN KEY (case_id, event_num, vehicle_num) REFERENCES case_events(case_id, event_num, vehicle_num)
                );
                """
            )
            self.db.commit()
            self.profile = self.cursor.execute(
                """
                SELECT * FROM scrape_profiles WHERE profile_id = ?
                """,
                (profile_id,)
            ).fetchone()
            if self.profile is None:
                raise ValueError(f"Profile ID {profile_id} does not exist.")
            
        except (ValueError, sqlite3.Error) as e:
            self.logger.error(e)

        self.data_list = []

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
            return f"Case {data[1]} Event {data[2]} Vehicle {data[3]}"
        if role == Qt.ItemDataRole.UserRole:
            return self.data_list[index.row()]
        return None
    
    def add_data(self, event):
        try:
            case_id = event["case_id"]
            case_num = event["case_num"]
            summary = event["summary"]
            event_num = event["event_num"]
            vehicle_num = event["veh_num"]
            make = event["make"]
            model = event["model"]
            model_year = event["model_year"]

            self.cursor.execute(
                """
                INSERT OR IGNORE INTO scrape_profile_events (profile_id, case_id, event_num, vehicle_num)
                VALUES (?, ?, ?, ?)
                """,
                (self.profile[0], case_id, event_num, vehicle_num)
            )
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO cases (case_id, case_num, summary)
                VALUES (?, ?, ?)
                """,
                (case_id, case_num, summary)
            )
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO case_events (
                    case_id,
                    event_num,
                    vehicle_num,
                    make,
                    model,
                    model_year
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (case_id, event_num, vehicle_num, make, model, model_year)
            )
            self.db.commit()
            self.logger.debug(f"Added case event {event_num} from case {case_id} to scrape profile {self.profile[1]}.")
        except (sqlite3.Error, KeyError) as e:
            self.logger.error("Error adding case:", e)
            return
        self.refresh_data()

    def delete_data(self, index):
        try:
            data = self.data_list[index.row()]
            self.cursor.execute(
                """
                DELETE FROM case_events WHERE (case_id, event_num, vehicle_num) = ?
                """,
                (data[0],)
            )
            self.db.commit()
        except sqlite3.Error as e:
            self.logger.error("Error deleting case:", e)
            return
        except IndexError:
            self.logger.error("Error deleting case: index out of range")
            return
        self.logger.debug(f"Deleted event: Case {data[1]} Event {data[2]} Vehicle {data[3]}")
        self.refresh_data()

    def refresh_data(self):
        try:
            self.cursor.execute(
                """
                SELECT * FROM scrape_profile_events
                WHERE profile_id = ?
                """,
                (self.profile[0],)
            )
            self.data_list = self.cursor.fetchall()
            self.layoutChanged.emit()
        except sqlite3.Error as e:
            self.logger.error("Error refreshing data:", e)
            return
        self.logger.debug("Refreshed data.")

    def __del__(self):
        self.close_database()
