import logging
from pathlib import Path
import sqlite3

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt


class ProfileEvents(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
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
                CREATE TABLE IF NOT EXISTS scrape_profile_cases (
                    profile_id INTEGER,
                    case_id INTEGER,
                    PRIMARY KEY (profile_id, case_id),
                    FOREIGN KEY (profile_id) REFERENCES scrape_profiles(profile_id),
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                );
                """
            )
            self.db.commit()
        except sqlite3.Error as e:
            self.logger.error(e)
            self.db = None
            self.cursor = None
        
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
            return str(data)
        return None
    
    def add_data(self, event, profile_id):
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
                INSERT OR IGNORE INTO scrape_profile_cases (profile_id, case_id)
                VALUES (?, ?)
                """,
                (profile_id, case_id)
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
        except (sqlite3.Error, KeyError) as e:
            self.logger.error("Error adding case:", e)
            return
        self.logger.debug(f"Added case event {event_num} from case {case_id} to scrape profile {profile_id}.")

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
        self.logger.debug("Deleted profile: " + str(data[1]))
        self.refresh_data()

    def refresh_data(self):
        try:
            self.cursor.execute('SELECT * FROM case_events')
            self.data_list = self.cursor.fetchall()
            self.layoutChanged.emit()
        except sqlite3.Error as e:
            self.logger.error("Error refreshing data:", e)
            return
        self.logger.debug("Refreshed data")

    def __del__(self):
        self.close_database()
